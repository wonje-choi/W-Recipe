import datetime

class Seed:
    def struct(self):
        return wiz.model("portal/recipe/struct")

    def constants(self):
        return wiz.model("portal/recipe/constants")

    def dumps(self, value):
        return self.struct().json_dumps(value)

    def now(self):
        return datetime.datetime.now()

    def _upsert(self, table, data, keys="id"):
        table.upsert(data, keys=keys)
        return data.get("id")

    def run(self, admin_email="", admin_password_hash=""):
        core = self.struct()
        constants = self.constants()
        now = self.now()

        admin_id = self.seed_admin(admin_email, admin_password_hash, now)
        demo_user_id = self.seed_demo_user(now)
        dish_ids, version_ids = self.seed_recipes(now)
        ai_ids = self.seed_ai_examples(version_ids, admin_id, now)

        return {
            "categories": constants.DEFAULT_CATEGORIES,
            "tags": constants.DEFAULT_TAGS,
            "adminUserId": admin_id,
            "demoUserId": demo_user_id,
            "dishIds": dish_ids,
            "versionIds": version_ids,
            "aiModificationIds": ai_ids,
            "publicStatus": constants.PUBLIC_RECIPE_STATUS,
        }

    def seed_admin(self, admin_email, admin_password_hash, now=None):
        if not admin_email or not admin_password_hash:
            return ""
        if now is None:
            now = self.now()
        constants = self.constants()
        user_db = self.struct().db("user")
        admin_id = "recipe_admin_seed"
        self._upsert(user_db, {
            "id": admin_id,
            "email": admin_email,
            "password_hash": admin_password_hash,
            "nickname": "Recipe Admin",
            "role": constants.USER_ROLES["ADMIN"],
            "status": constants.USER_STATUSES["ACTIVE"],
            "login_failed_count": 0,
            "created_at": now,
            "updated_at": now,
        })
        return admin_id

    def seed_demo_user(self, now=None):
        if now is None:
            now = self.now()
        constants = self.constants()
        core = self.struct()
        user_db = core.db("user")
        preference_db = core.db("user_preference")
        user_id = "recipe_demo_user"
        self._upsert(user_db, {
            "id": user_id,
            "email": "demo.recipe@example.invalid",
            "password_hash": "disabled-seed-account",
            "nickname": "Demo User",
            "role": constants.USER_ROLES["USER"],
            "status": constants.USER_STATUSES["PENDING"],
            "login_failed_count": 0,
            "created_at": now,
            "updated_at": now,
        })
        self._upsert(preference_db, {
            "id": "pref_recipe_demo_user",
            "user_id": user_id,
            "preferred_diet_types": self.dumps([constants.DIET_TYPES["LOW_SODIUM"], constants.DIET_TYPES["SOFT_TEXTURE"]]),
            "allergies": self.dumps(["새우"]),
            "disliked_ingredients": self.dumps(["고수"]),
            "preferred_cooking_time": 30,
            "cooking_tools": self.dumps(["냄비", "프라이팬"]),
            "baby_age_month": 10,
            "sodium_preference": "low",
            "texture_preference": "soft",
            "created_at": now,
            "updated_at": now,
        })
        return user_id

    def seed_recipes(self, now=None):
        if now is None:
            now = self.now()
        constants = self.constants()
        core = self.struct()
        dish_db = core.db("recipe_dish")
        version_db = core.db("recipe_version")

        dishes = [
            {
                "id": "dish_low_sodium_soup",
                "name": "저염 된장국",
                "description": "된장의 풍미는 살리고 나트륨 부담은 낮춘 국 레시피",
                "category": "저염",
                "tags": self.dumps(["저염", "국/찌개", "간단요리"]),
                "thumbnail_url": "",
                "view_count": 24,
                "status": constants.RECIPE_STATUSES["APPROVED"],
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "dish_baby_porridge",
                "name": "닭고기 채소 이유식",
                "description": "부드럽게 갈아 먹기 좋은 후기 이유식 샘플",
                "category": "이유식",
                "tags": self.dumps(["이유식", "부드러운 식감", "죽/미음"]),
                "thumbnail_url": "",
                "view_count": 18,
                "status": constants.RECIPE_STATUSES["APPROVED"],
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "dish_tofu_salad",
                "name": "고단백 두부 샐러드",
                "description": "가볍지만 단백질을 보강한 다이어트 샐러드",
                "category": "고단백",
                "tags": self.dumps(["고단백", "다이어트", "간단요리"]),
                "thumbnail_url": "",
                "view_count": 12,
                "status": constants.RECIPE_STATUSES["APPROVED"],
                "created_at": now,
                "updated_at": now,
            },
        ]

        versions = [
            self.low_sodium_original(now),
            self.low_sodium_ai_pending(now),
            self.baby_porridge_original(now),
            self.tofu_salad_original(now),
        ]

        for dish in dishes:
            self._upsert(dish_db, dish)
        for version in versions:
            self._upsert(version_db, version)

        return [dish["id"] for dish in dishes], [version["id"] for version in versions]

    def low_sodium_original(self, now):
        constants = self.constants()
        return {
            "id": "ver_soup_original",
            "dish_id": "dish_low_sodium_soup",
            "title": "기본 저염 된장국",
            "source_type": constants.SOURCE_TYPES["DIRECT"],
            "summary": "멸치육수와 채소 단맛으로 된장 양을 줄인 버전",
            "ingredients": self.dumps(["된장 1큰술", "두부 100g", "애호박 1/3개", "양파 1/4개", "멸치육수 600ml"]),
            "steps": self.dumps(["멸치육수를 끓인다", "된장을 풀고 채소를 넣는다", "두부를 넣고 3분 더 끓인다"]),
            "cooking_tips": self.dumps(["된장은 마지막에 간을 보며 추가한다"]),
            "failure_prevention_tips": self.dumps(["센 불에서 오래 끓이면 된장 향이 텁텁해질 수 있다"]),
            "substitution_tips": self.dumps(["애호박 대신 무를 얇게 썰어 넣어도 좋다"]),
            "nutrition_info": self.dumps({"calorie": 95, "protein": 7}),
            "sodium_info": self.dumps({"estimatedMg": 520, "level": "reduced"}),
            "allergen_info": self.dumps(["대두"]),
            "difficulty": "easy",
            "cooking_time": 20,
            "serving_size": "2인분",
            "view_count": 24,
            "ai_modified": False,
            "status": constants.RECIPE_STATUSES["APPROVED"],
            "created_at": now,
            "updated_at": now,
        }

    def low_sodium_ai_pending(self, now):
        constants = self.constants()
        return {
            "id": "ver_soup_ai_pending",
            "dish_id": "dish_low_sodium_soup",
            "title": "AI 제안 더 낮은 나트륨 된장국",
            "source_type": constants.SOURCE_TYPES["AI_MODIFIED"],
            "summary": "채소 육수와 표고 향으로 된장 사용량을 더 줄인 검수 대기 버전",
            "ingredients": self.dumps(["된장 2작은술", "두부 100g", "표고버섯 2개", "무 80g", "채소육수 650ml"]),
            "steps": self.dumps(["무와 표고로 육수를 우린다", "된장을 소량 풀고 두부를 넣는다", "부족한 감칠맛은 표고가루로 보완한다"]),
            "cooking_tips": self.dumps(["짠맛 대신 향과 감칠맛을 먼저 끌어올린다"]),
            "failure_prevention_tips": self.dumps(["저염 버전은 끓인 뒤 바로 먹어야 맛이 흐려지지 않는다"]),
            "substitution_tips": self.dumps(["표고버섯은 양송이로 대체 가능하지만 감칠맛은 줄어든다"]),
            "nutrition_info": self.dumps({"calorie": 88, "protein": 7}),
            "sodium_info": self.dumps({"estimatedMg": 390, "level": "low"}),
            "allergen_info": self.dumps(["대두"]),
            "difficulty": "easy",
            "cooking_time": 22,
            "serving_size": "2인분",
            "view_count": 0,
            "ai_modified": True,
            "status": constants.RECIPE_STATUSES["PENDING_REVIEW"],
            "created_at": now,
            "updated_at": now,
        }

    def baby_porridge_original(self, now):
        constants = self.constants()
        return {
            "id": "ver_baby_porridge",
            "dish_id": "dish_baby_porridge",
            "title": "닭고기 채소 이유식",
            "source_type": constants.SOURCE_TYPES["DIRECT"],
            "summary": "잘게 찢은 닭고기와 익힌 채소를 부드럽게 끓인 이유식",
            "ingredients": self.dumps(["쌀밥 80g", "닭가슴살 40g", "당근 20g", "애호박 20g", "물 300ml"]),
            "steps": self.dumps(["닭고기를 완전히 익힌다", "채소를 잘게 다진다", "밥과 물을 넣고 퍼질 때까지 끓인다"]),
            "cooking_tips": self.dumps(["아기 월령에 맞춰 입자 크기를 조절한다"]),
            "failure_prevention_tips": self.dumps(["간을 하지 않고 재료를 충분히 익힌다"]),
            "substitution_tips": self.dumps(["닭고기 대신 흰살생선을 사용할 수 있다"]),
            "nutrition_info": self.dumps({"calorie": 160, "protein": 10}),
            "sodium_info": self.dumps({"estimatedMg": 35, "level": "very_low"}),
            "allergen_info": self.dumps([]),
            "difficulty": "normal",
            "cooking_time": 30,
            "serving_size": "2회분",
            "view_count": 18,
            "ai_modified": False,
            "status": constants.RECIPE_STATUSES["APPROVED"],
            "created_at": now,
            "updated_at": now,
        }

    def tofu_salad_original(self, now):
        constants = self.constants()
        return {
            "id": "ver_tofu_salad",
            "dish_id": "dish_tofu_salad",
            "title": "고단백 두부 샐러드",
            "source_type": constants.SOURCE_TYPES["DIRECT"],
            "summary": "두부와 달걀로 포만감을 높인 간단 샐러드",
            "ingredients": self.dumps(["두부 150g", "삶은 달걀 1개", "양상추 60g", "방울토마토 5개", "요거트 드레싱 2큰술"]),
            "steps": self.dumps(["두부 물기를 제거한다", "채소를 씻고 한입 크기로 자른다", "두부와 달걀을 올리고 드레싱을 곁들인다"]),
            "cooking_tips": self.dumps(["두부는 팬에 살짝 구우면 물기가 줄어든다"]),
            "failure_prevention_tips": self.dumps(["드레싱은 먹기 직전에 넣는다"]),
            "substitution_tips": self.dumps(["달걀 대신 병아리콩을 넣을 수 있다"]),
            "nutrition_info": self.dumps({"calorie": 260, "protein": 19}),
            "sodium_info": self.dumps({"estimatedMg": 300, "level": "normal"}),
            "allergen_info": self.dumps(["대두", "달걀", "유제품"]),
            "difficulty": "easy",
            "cooking_time": 15,
            "serving_size": "1인분",
            "view_count": 12,
            "ai_modified": False,
            "status": constants.RECIPE_STATUSES["APPROVED"],
            "created_at": now,
            "updated_at": now,
        }

    def seed_ai_examples(self, version_ids, admin_id="", now=None):
        if now is None:
            now = self.now()
        constants = self.constants()
        ai_db = self.struct().db("ai_recipe_modification")
        modification = {
            "id": "ai_low_sodium_pending",
            "recipe_version_id": "ver_soup_original",
            "requested_by": admin_id or "recipe_seed",
            "purpose": constants.AI_PURPOSES["LOW_SODIUM"],
            "target_user_type": "low_sodium",
            "original_summary": "기본 저염 된장국에서 나트륨을 더 낮추는 제안",
            "modified_ingredients": self.dumps(["된장 2작은술", "표고버섯", "무", "채소육수"]),
            "modified_steps": self.dumps(["채소육수를 먼저 우린다", "된장을 소량만 풀고 향채로 맛을 보강한다"]),
            "improvement_reason": "짠맛 대신 감칠맛을 강화해 나트륨 부담을 낮춘다.",
            "taste_improvement_point": "표고와 무의 감칠맛을 사용한다.",
            "sodium_reduction_point": "된장 사용량을 약 30% 줄인다.",
            "baby_food_safety_notes": "영아용으로 제공할 때는 된장을 더 줄이고 알레르기 반응을 확인한다.",
            "allergen_warnings": self.dumps(["대두"]),
            "caution_notes": self.dumps(["저염식이 필요한 사용자는 개인별 의료 지침을 우선한다"]),
            "risk_flags": self.dumps([]),
            "status": constants.AI_STATUSES["PENDING_REVIEW"],
            "reviewed_by": "",
            "rejected_reason": "",
            "created_at": now,
            "updated_at": now,
        }
        self._upsert(ai_db, modification)
        return [modification["id"]]

    def admin_creation_procedure(self):
        return [
            "FN-0012 인증 구현 후 안전한 해시 함수로 초기 관리자 비밀번호 해시를 생성한다.",
            "wiz.model('portal/recipe/seed').run(admin_email, admin_password_hash)를 관리자 전용 초기화 API 또는 콘솔에서 1회 실행한다.",
            "초기 로그인 후 운영자는 즉시 비밀번호를 변경하고 seed 해시 값을 기록에 남기지 않는다.",
        ]

Model = Seed()

class AIDiet:
    def __init__(self, core):
        self.core = core
        self.constants = core.constants

    def to_list(self, value):
        if value in [None, ""]:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                parsed = self.core.json_loads(text, [])
                if isinstance(parsed, list):
                    return parsed
            return [item.strip() for item in text.split(",") if item.strip()]
        return []

    def normalize_purpose(self, purpose):
        purpose = (purpose or self.constants.AI_PURPOSES["TASTIER"]).strip()
        if purpose not in self.constants.values("AI_PURPOSES"):
            raise Exception("지원하지 않는 개량 목적입니다.")
        return purpose

    def prompt_key_for_purpose(self, purpose):
        if purpose == self.constants.AI_PURPOSES["LOW_SODIUM"]:
            return self.constants.AI_PROMPT_TYPES["LOW_SODIUM"]
        if purpose == self.constants.AI_PURPOSES["BABY_FOOD"]:
            return self.constants.AI_PROMPT_TYPES["BABY_FOOD"]
        return self.constants.AI_PROMPT_TYPES["TASTE_IMPROVEMENT"]

    def ensure_prompt(self, prompt_key, admin_user_id=""):
        active = self.core.ai.prompt_db.get(prompt_key=prompt_key, is_active=True)
        if active:
            return active
        if self.core.is_admin() == False:
            raise Exception("활성 특수식단 프롬프트가 없습니다. 관리자에게 문의해주세요.")
        fallback_version = "heuristic-v1"
        fallback_prompt_version = self.core.ai.prompt_version_key(prompt_key, fallback_version)
        existing = self.core.ai.get_prompt_by_version(fallback_prompt_version)
        if existing:
            self.core.ai.activate_prompt(existing.get("id"), admin_user_id, "Built-in diet modification fallback activated")
            return self.core.ai.get_prompt(existing.get("id"))
        titles = {
            self.constants.AI_PROMPT_TYPES["LOW_SODIUM"]: "내장 저염식 개량 휴리스틱",
            self.constants.AI_PROMPT_TYPES["BABY_FOOD"]: "내장 이유식 개량 휴리스틱",
            self.constants.AI_PROMPT_TYPES["TASTE_IMPROVEMENT"]: "내장 맛 개선 휴리스틱",
        }
        prompt_id = self.core.ai.create_prompt({
            "prompt_key": prompt_key,
            "version": fallback_version,
            "title": titles.get(prompt_key, "내장 특수식단 개량 휴리스틱"),
            "description": "MVP 환경에서 레시피를 특수식단 목적에 맞게 구조화하는 기본 규칙 기반 프롬프트",
            "template": "입력 레시피와 사용자 조건을 바탕으로 재료와 조리 단계를 조정하고, 개선 이유와 주의사항을 구조화한다.",
            "input_schema": {"recipeVersionId": "string", "purpose": "string", "constraints": "object"},
            "output_schema": {"modifiedIngredients": "array", "modifiedSteps": "array", "riskFlags": "array"},
            "model_hint": "internal-heuristic",
            "is_active": True,
            "change_reason": "Built-in fallback for MVP diet modification pipeline",
        }, admin_user_id=admin_user_id)
        return self.core.ai.get_prompt(prompt_id)

    def visible_version(self, version_id):
        public = self.core.is_admin() == False
        version = self.core.recipe.get_version(version_id, public=public)
        if version is None:
            raise Exception("개량할 레시피 버전을 찾을 수 없습니다.")
        return version

    def source_lines(self, version):
        ingredients = self.core.json_loads(version.get("ingredients"), [])
        steps = self.core.json_loads(version.get("steps"), [])
        return ingredients, steps

    def remove_excluded(self, ingredients, excluded):
        if not excluded:
            return list(ingredients)
        filtered = []
        for item in ingredients:
            blocked = False
            for excluded_item in excluded:
                if excluded_item and excluded_item in item:
                    blocked = True
            if blocked == False:
                filtered.append(item)
        return filtered

    def low_sodium_ingredients(self, ingredients):
        high_sodium = ["소금", "간장", "된장", "고추장", "액젓", "장아찌", "햄", "베이컨", "치즈", "라면스프"]
        result = []
        changed = False
        for item in ingredients:
            if any(keyword in item for keyword in high_sodium):
                result.append(f"{item} - 양을 30~50% 줄이고 향채/식초/육수로 보완")
                changed = True
            else:
                result.append(item)
        if changed == False:
            result.append("소금/간장류는 마지막에 간을 보며 최소량만 추가")
        return result

    def baby_food_ingredients(self, ingredients, baby_age_month):
        result = []
        for item in ingredients:
            if any(keyword in item for keyword in ["꿀", "견과", "땅콩", "소금", "설탕", "고추", "고춧가루"]):
                continue
            result.append(item)
        if baby_age_month and int(baby_age_month or 0) < 12:
            result.append("소금/설탕 없이 재료 본연의 단맛으로 조리")
        return result

    def simplify_steps(self, steps, desired_time=0, baby_food=False):
        result = []
        for step in steps:
            text = step
            if desired_time and int(desired_time or 0) <= 20:
                text = text.replace("오래", "짧게").replace("천천히", "간단히")
            if baby_food:
                text = f"{text} 후 월령에 맞게 곱게 다지거나 으깬다"
            result.append(text)
        if not result:
            result.append("재료를 손질한 뒤 목적에 맞게 간을 조절하고 충분히 익힌다")
        return result

    def allergen_warnings(self, text, allergies):
        warnings = []
        for allergy in allergies:
            if allergy and allergy in text:
                warnings.append(f"알레르기 후보 포함: {allergy}")
        return warnings

    def build_result(self, version, data):
        purpose = self.normalize_purpose(data.get("purpose"))
        ingredients, steps = self.source_lines(version)
        excluded = self.to_list(data.get("excluded_ingredients"))
        allergies = self.to_list(data.get("allergies"))
        desired_time = int(data.get("desired_cooking_time") or 0)
        baby_age_month = int(data.get("baby_age_month") or 0)
        taste_direction = data.get("taste_direction", "")
        target_user_type = data.get("target_user_type") or purpose
        modified_ingredients = self.remove_excluded(ingredients, excluded)
        risk_flags = []
        caution_notes = []
        sodium_reduction_point = ""
        baby_food_safety_notes = ""

        if purpose == self.constants.AI_PURPOSES["LOW_SODIUM"]:
            modified_ingredients = self.low_sodium_ingredients(modified_ingredients)
            sodium_reduction_point = "고나트륨 양념을 줄이고 향채, 식초, 육수, 감칠맛 재료로 풍미를 보완한다."
            caution_notes.append("저염식이 필요한 사용자는 개인 의료 지침을 우선한다.")
        if purpose == self.constants.AI_PURPOSES["BABY_FOOD"]:
            modified_ingredients = self.baby_food_ingredients(modified_ingredients, baby_age_month)
            steps = self.simplify_steps(steps, desired_time, baby_food=True)
            baby_food_safety_notes = f"{baby_age_month or '미지정'}개월 기준으로 소금/설탕을 제한하고, 질감은 월령에 맞게 조절한다. 남은 음식은 빠르게 식혀 냉장 보관한다."
            risk_flags.append("baby_food_review_required")
        else:
            steps = self.simplify_steps(steps, desired_time)
        if purpose == self.constants.AI_PURPOSES["DIET"]:
            modified_ingredients.append("채소 비중을 늘리고 기름 사용량을 줄인다")
            caution_notes.append("극단적인 열량 제한 표현은 사용하지 않는다.")
        if purpose == self.constants.AI_PURPOSES["HIGH_PROTEIN"]:
            modified_ingredients.append("두부, 달걀, 닭가슴살 등 단백질 재료를 상황에 맞게 추가")
        if purpose == self.constants.AI_PURPOSES["SIMPLER_INGREDIENTS"]:
            modified_ingredients = modified_ingredients[:6]
        original_text = " ".join(ingredients + steps + [version.get("summary", "")])
        warnings = self.allergen_warnings(original_text, allergies)
        if warnings:
            risk_flags.append("allergy_review_required")
        safety_text = " ".join(modified_ingredients + steps + warnings + caution_notes + [sodium_reduction_point, baby_food_safety_notes])
        safety = self.core.safety.check_text(safety_text, purpose=purpose, baby_age_month=baby_age_month)
        risk_flags = self.core.safety.unique(risk_flags + safety.get("riskFlags", []))
        for issue in safety.get("issues", []):
            message = issue.get("message", "")
            if message and message not in caution_notes:
                caution_notes.append(message)
        improvement_reason = "요청 목적에 맞춰 재료 구성, 조리 단계, 맛 보완 근거를 조정했다."
        if excluded:
            improvement_reason += f" 제외 재료({', '.join(excluded)})는 개량안에서 제거했다."
        taste_point = taste_direction or "향, 감칠맛, 식감 균형을 유지하도록 보완한다."
        return {
            "purpose": purpose,
            "target_user_type": target_user_type,
            "modified_ingredients": modified_ingredients,
            "modified_steps": steps,
            "improvement_reason": improvement_reason,
            "taste_improvement_point": taste_point,
            "sodium_reduction_point": sodium_reduction_point,
            "baby_food_safety_notes": baby_food_safety_notes,
            "allergen_warnings": warnings,
            "caution_notes": caution_notes,
            "risk_flags": risk_flags,
        }

    def create(self, data, requester_user_id=""):
        data = dict(data or {})
        version_id = data.get("recipe_version_id")
        if not version_id:
            raise Exception("개량할 레시피 버전을 선택해주세요.")
        version = self.visible_version(version_id)
        purpose = self.normalize_purpose(data.get("purpose"))
        prompt_key = self.prompt_key_for_purpose(purpose)
        prompt_version = data.get("prompt_version", "")
        if not prompt_version:
            prompt = self.ensure_prompt(prompt_key, requester_user_id)
            prompt_version = prompt.get("prompt_version", "")
        log_id = ""
        try:
            log_id = self.core.ai.create_log({
                "request_type": purpose,
                "target_id": version_id,
                "prompt_version": prompt_version,
                "input_summary": self.core.json_dumps({
                    "recipeVersionId": version_id,
                    "purpose": purpose,
                    "targetUserType": data.get("target_user_type", ""),
                    "excludedIngredients": self.to_list(data.get("excluded_ingredients")),
                    "allergies": self.to_list(data.get("allergies")),
                    "desiredCookingTime": data.get("desired_cooking_time", ""),
                    "tasteDirection": data.get("taste_direction", ""),
                    "babyAgeMonth": data.get("baby_age_month", ""),
                }),
            })
            result = self.build_result(version, data)
            modification_id = self.core.ai.create_modification({
                "recipe_version_id": version_id,
                "requested_by": requester_user_id,
                "purpose": result["purpose"],
                "target_user_type": result["target_user_type"],
                "original_summary": version.get("summary", ""),
                "modified_ingredients": self.core.json_dumps(result["modified_ingredients"]),
                "modified_steps": self.core.json_dumps(result["modified_steps"]),
                "improvement_reason": result["improvement_reason"],
                "taste_improvement_point": result["taste_improvement_point"],
                "sodium_reduction_point": result["sodium_reduction_point"],
                "baby_food_safety_notes": result["baby_food_safety_notes"],
                "allergen_warnings": self.core.json_dumps(result["allergen_warnings"]),
                "caution_notes": self.core.json_dumps(result["caution_notes"]),
                "risk_flags": self.core.json_dumps(result["risk_flags"]),
                "status": self.constants.AI_STATUSES["PENDING_REVIEW"],
            })
            self.core.ai.log_db.update({"target_id": modification_id}, id=log_id)
            self.core.ai.finish_log(log_id, output_summary=f"{purpose} / {modification_id}")
            modification = self.core.db("ai_recipe_modification").get(id=modification_id)
            log = self.core.ai.log_db.get(id=log_id)
        except Exception as error:
            if log_id:
                self.core.ai.fail_log(log_id, str(error))
            raise
        return {
            "version": version,
            "modification": modification,
            "log": log,
        }

Model = AIDiet

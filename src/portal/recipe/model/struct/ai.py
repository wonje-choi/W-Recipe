import json
import os
import re

AI_SETTINGS_DEFAULT = {
    "auto_approve_threshold": 0.85,
}

class AI:
    def __init__(self, core):
        self.core = core
        self.prompt_db = core.db("ai_prompt_template")
        self.modification_db = core.db("ai_recipe_modification")
        self.log_db = core.db("ai_processing_log")
        self.constants = core.constants

    def bool_value(self, value, default=False):
        if isinstance(value, bool):
            return value
        if value in ["true", "True", "1", 1]:
            return True
        if value in ["false", "False", "0", 0]:
            return False
        return default

    def settings_path(self):
        try:
            return wiz.project.path(os.path.join("config", "ai_settings.json"))
        except Exception:
            return os.path.join("config", "ai_settings.json")

    def get_settings(self):
        settings = dict(AI_SETTINGS_DEFAULT)
        try:
            with open(self.settings_path(), "r", encoding="utf-8") as fp:
                loaded = json.load(fp)
            if isinstance(loaded, dict):
                settings.update(loaded)
        except Exception:
            pass
        settings["auto_approve_threshold"] = self.normalize_confidence_score(settings.get("auto_approve_threshold"), AI_SETTINGS_DEFAULT["auto_approve_threshold"])
        return settings

    def save_settings(self, data):
        settings = self.get_settings()
        settings["auto_approve_threshold"] = self.normalize_confidence_score(data.get("auto_approve_threshold"), settings["auto_approve_threshold"])
        path = self.settings_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(settings, fp, ensure_ascii=False, indent=2)
        return settings

    def normalize_confidence_score(self, value, default=0.0):
        try:
            score = float(value)
        except Exception:
            score = default
        if score < 0:
            return 0.0
        if score > 1:
            return 1.0
        return round(score, 2)

    def estimate_confidence_score(self, data):
        data = dict(data or {})
        score = 0.86
        if data.get("modified_ingredients") not in [None, "", "[]"]:
            score += 0.04
        if data.get("modified_steps") not in [None, "", "[]"]:
            score += 0.04
        if not data.get("original_summary"):
            score -= 0.05
        risk_flags = self.core.json_loads(data.get("risk_flags"), [])
        caution_notes = self.core.json_loads(data.get("caution_notes"), [])
        score -= min(0.6, len(risk_flags) * 0.2)
        if len(caution_notes) > 2:
            score -= 0.05
        if data.get("purpose") == self.constants.AI_PURPOSES["BABY_FOOD"]:
            score -= 0.1
        return self.normalize_confidence_score(score)

    def prompt_version_key(self, prompt_key, version):
        return f"{prompt_key}:{version}"

    def normalize_prompt_key(self, prompt_key):
        prompt_key = (prompt_key or "").strip()
        if not prompt_key:
            raise Exception("프롬프트 유형을 입력해주세요.")
        if prompt_key not in self.constants.values("AI_PROMPT_TYPES"):
            raise Exception("지원하지 않는 프롬프트 유형입니다.")
        return prompt_key

    def json_text(self, value, default=None):
        if default is None:
            default = {}
        if value in [None, ""]:
            return self.core.json_dumps(default)
        if isinstance(value, (list, dict)):
            return self.core.json_dumps(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return self.core.json_dumps(default)
            self.core.json_loads(text, default)
            return text
        return self.core.json_dumps(default)

    def get_prompt(self, prompt_id):
        prompt = self.prompt_db.get(id=prompt_id)
        if prompt is None:
            raise Exception("프롬프트 템플릿을 찾을 수 없습니다.")
        return prompt

    def get_prompt_by_version(self, prompt_version):
        if not prompt_version:
            return None
        return self.prompt_db.get(prompt_version=prompt_version)

    def active_prompt(self, prompt_key):
        prompt_key = self.normalize_prompt_key(prompt_key)
        return self.prompt_db.get(prompt_key=prompt_key, is_active=True)

    def deactivate_active_prompts(self, prompt_key, except_id="", admin_user_id=""):
        rows = self.prompt_db.rows(prompt_key=prompt_key, is_active=True, page=1, dump=100)
        for row in rows:
            if row.get("id") == except_id:
                continue
            self.prompt_db.update({
                "is_active": False,
                "updated_by": admin_user_id,
                "updated_at": self.core.now(),
                "deactivated_at": self.core.now(),
            }, id=row.get("id"))

    def create_prompt(self, data, admin_user_id=""):
        data = dict(data or {})
        prompt_key = self.normalize_prompt_key(data.get("prompt_key"))
        version = str(data.get("version") or "").strip()
        template = data.get("template") or ""
        if not version:
            raise Exception("프롬프트 버전을 입력해주세요.")
        if not template:
            raise Exception("프롬프트 템플릿을 입력해주세요.")
        prompt_version = self.prompt_version_key(prompt_key, version)
        if self.get_prompt_by_version(prompt_version):
            raise Exception("이미 등록된 프롬프트 버전입니다.")
        is_active = self.bool_value(data.get("is_active"), False)
        if is_active:
            self.deactivate_active_prompts(prompt_key, admin_user_id=admin_user_id)
        now = self.core.now()
        return self.prompt_db.insert({
            "prompt_key": prompt_key,
            "version": version,
            "prompt_version": prompt_version,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "template": template,
            "input_schema": self.json_text(data.get("input_schema"), {}),
            "output_schema": self.json_text(data.get("output_schema"), {}),
            "model_hint": data.get("model_hint", ""),
            "is_active": is_active,
            "change_reason": data.get("change_reason", ""),
            "created_by": admin_user_id,
            "updated_by": admin_user_id,
            "deactivated_at": None,
            "created_at": now,
            "updated_at": now,
        })

    def update_prompt(self, prompt_id, data, admin_user_id=""):
        prompt = self.get_prompt(prompt_id)
        data = dict(data or {})
        payload = {}
        if "prompt_key" in data:
            payload["prompt_key"] = self.normalize_prompt_key(data.get("prompt_key"))
        if "version" in data:
            version = str(data.get("version") or "").strip()
            if not version:
                raise Exception("프롬프트 버전을 입력해주세요.")
            payload["version"] = version
        for key in ["title", "description", "template", "model_hint", "change_reason"]:
            if key in data:
                payload[key] = data.get(key) or ""
        if "template" in payload and not payload.get("template"):
            raise Exception("프롬프트 템플릿을 입력해주세요.")
        if "input_schema" in data:
            payload["input_schema"] = self.json_text(data.get("input_schema"), {})
        if "output_schema" in data:
            payload["output_schema"] = self.json_text(data.get("output_schema"), {})
        next_prompt_key = payload.get("prompt_key", prompt.get("prompt_key"))
        next_version = payload.get("version", prompt.get("version"))
        if "prompt_key" in payload or "version" in payload:
            next_prompt_version = self.prompt_version_key(next_prompt_key, next_version)
            existing = self.get_prompt_by_version(next_prompt_version)
            if existing and existing.get("id") != prompt_id:
                raise Exception("이미 등록된 프롬프트 버전입니다.")
            payload["prompt_version"] = next_prompt_version
        if "is_active" in data:
            payload["is_active"] = self.bool_value(data.get("is_active"), False)
            if payload["is_active"]:
                self.deactivate_active_prompts(next_prompt_key, except_id=prompt_id, admin_user_id=admin_user_id)
                payload["deactivated_at"] = None
            elif prompt.get("is_active"):
                payload["deactivated_at"] = self.core.now()
        payload["updated_by"] = admin_user_id
        payload["updated_at"] = self.core.now()
        self.prompt_db.update(payload, id=prompt_id)

    def activate_prompt(self, prompt_id, admin_user_id="", change_reason=""):
        prompt = self.get_prompt(prompt_id)
        self.deactivate_active_prompts(prompt.get("prompt_key"), except_id=prompt_id, admin_user_id=admin_user_id)
        payload = {
            "is_active": True,
            "updated_by": admin_user_id,
            "updated_at": self.core.now(),
            "deactivated_at": None,
        }
        if change_reason:
            payload["change_reason"] = change_reason
        self.prompt_db.update(payload, id=prompt_id)

    def deactivate_prompt(self, prompt_id, admin_user_id="", change_reason=""):
        payload = {
            "is_active": False,
            "updated_by": admin_user_id,
            "updated_at": self.core.now(),
            "deactivated_at": self.core.now(),
        }
        if change_reason:
            payload["change_reason"] = change_reason
        self.prompt_db.update(payload, id=prompt_id)

    def prompt_rows(self, prompt_key="", is_active=None, page=1, dump=20):
        filters = {}
        if prompt_key:
            filters["prompt_key"] = self.normalize_prompt_key(prompt_key)
        if is_active in [True, False]:
            filters["is_active"] = is_active
        rows = self.prompt_db.rows(page=page, dump=dump, orderby="updated_at", order="DESC", **filters)
        total = self.prompt_db.count(**filters) or 0
        return rows, total

    def attach_prompt_version(self, data):
        data = dict(data or {})
        prompt_key = data.pop("prompt_key", "")
        prompt_version = data.get("prompt_version", "")
        if prompt_version:
            if self.get_prompt_by_version(prompt_version) is None:
                raise Exception("등록되지 않은 프롬프트 버전입니다.")
            return data
        if prompt_key:
            active = self.active_prompt(prompt_key)
            if active is None:
                raise Exception("활성 프롬프트 버전이 없습니다.")
            data["prompt_version"] = active.get("prompt_version", "")
        return data

    def ensure_recipe_summary_prompt(self, admin_user_id=""):
        prompt_key = self.constants.AI_PROMPT_TYPES["RECIPE_SUMMARY"]
        active = self.prompt_db.get(prompt_key=prompt_key, is_active=True)
        if active:
            return active
        fallback_version = "heuristic-v1"
        fallback_prompt_version = self.prompt_version_key(prompt_key, fallback_version)
        existing = self.get_prompt_by_version(fallback_prompt_version)
        if existing:
            self.activate_prompt(existing.get("id"), admin_user_id, "Built-in recipe summary fallback activated")
            return self.get_prompt(existing.get("id"))
        prompt_id = self.create_prompt({
            "prompt_key": prompt_key,
            "version": fallback_version,
            "title": "내장 레시피 요약 휴리스틱",
            "description": "외부 자료나 직접 입력 텍스트에서 재료, 조리 단계, 팁 후보를 추출하는 기본 규칙 기반 프롬프트",
            "template": "입력 텍스트에서 레시피 제목, 재료 후보, 조리 순서 후보, 팁 후보를 추출하고 불확실한 항목은 확인 필요로 표시한다.",
            "input_schema": {"sourceType": "string", "text": "string", "sourceUrl": "string"},
            "output_schema": {"summary": "string", "ingredients": "array", "steps": "array", "uncertainties": "array"},
            "model_hint": "internal-heuristic",
            "is_active": True,
            "change_reason": "Built-in fallback for MVP recipe summary pipeline",
        }, admin_user_id=admin_user_id)
        return self.get_prompt(prompt_id)

    def clean_lines(self, text):
        text = (text or "").replace("\r", "\n")
        text = re.sub(r"[;。]+", "\n", text)
        lines = []
        for line in text.split("\n"):
            line = re.sub(r"^[\s\-•*]+", "", line.strip())
            if line:
                lines.append(line)
        if len(lines) <= 1 and len(text) > 120:
            lines = [item.strip() for item in re.split(r"(?<=[.!?。])\s+", text) if item.strip()]
        return lines

    def first_text(self, values, default=""):
        for value in values:
            if value:
                text = str(value).strip()
                if text:
                    return text
        return default

    def contains_any(self, text, keywords):
        lowered = (text or "").lower()
        for keyword in keywords:
            if keyword.lower() in lowered:
                return True
        return False

    def is_ingredient_line(self, line):
        units = ["g", "kg", "ml", "l", "큰술", "작은술", "스푼", "숟가락", "컵", "개", "대", "장", "쪽", "줌", "약간", "꼬집"]
        return bool(re.search(r"\d", line)) and self.contains_any(line, units)

    def is_step_line(self, line):
        if re.match(r"^\d+[\).\s]", line):
            return True
        return self.contains_any(line, ["끓", "볶", "굽", "삶", "섞", "넣", "썰", "다지", "데치", "익히", "졸이", "버무리", "간한다"])

    def extract_allergens(self, text):
        allergens = ["대두", "달걀", "계란", "우유", "유제품", "밀", "땅콩", "견과", "새우", "게", "고등어", "조개", "오징어", "돼지고기", "복숭아", "토마토"]
        found = []
        for allergen in allergens:
            if allergen in text and allergen not in found:
                found.append(allergen)
        return found

    def estimate_cooking_time(self, text):
        match = re.search(r"(\d{1,3})\s*(분|minute|minutes)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def extract_serving_size(self, text):
        match = re.search(r"(\d+\s*(인분|회분|serving|servings))", text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""

    def extract_recipe_candidate(self, text, title=""):
        lines = self.clean_lines(text)
        ingredients = []
        steps = []
        cooking_tips = []
        failure_tips = []
        substitution_tips = []
        uncertainties = []
        section = ""
        ingredient_headers = ["재료", "준비물", "ingredients"]
        step_headers = ["만드는 법", "만드는법", "조리", "순서", "방법", "steps", "recipe"]
        tip_keywords = ["팁", "tip", "주의", "보관", "실패", "대체", "꿀팁"]

        for line in lines:
            if self.contains_any(line, ingredient_headers) and len(line) <= 40:
                section = "ingredients"
                continue
            if self.contains_any(line, step_headers) and len(line) <= 50:
                section = "steps"
                continue
            if self.contains_any(line, tip_keywords):
                if "대체" in line:
                    substitution_tips.append(line)
                elif "실패" in line or "주의" in line:
                    failure_tips.append(line)
                else:
                    cooking_tips.append(line)
                continue
            if section == "ingredients" or self.is_ingredient_line(line):
                ingredients.append(line)
                continue
            if section == "steps" or self.is_step_line(line):
                steps.append(line)
                continue
            if len(line) > 12 and len(cooking_tips) < 3:
                cooking_tips.append(line)

        if not ingredients:
            uncertainties.append("재료 후보를 자동 확정하지 못했습니다. 원문에서 재료 목록을 확인해주세요.")
        if not steps:
            uncertainties.append("조리 순서 후보를 자동 확정하지 못했습니다. 원문에서 단계 정보를 확인해주세요.")
        if len(ingredients) > 12:
            ingredients = ingredients[:12]
            uncertainties.append("재료 후보가 많아 상위 12개만 저장했습니다.")
        if len(steps) > 12:
            steps = steps[:12]
            uncertainties.append("조리 단계 후보가 많아 상위 12개만 저장했습니다.")

        summary_source = self.first_text([title] + lines[:2], "AI 요약 레시피 후보")
        summary = summary_source[:280]
        return {
            "summary": summary,
            "ingredients": ingredients,
            "steps": steps,
            "cooking_tips": cooking_tips[:8],
            "failure_prevention_tips": failure_tips[:8] + uncertainties,
            "substitution_tips": substitution_tips[:8],
            "allergen_info": self.extract_allergens(text),
            "cooking_time": self.estimate_cooking_time(text),
            "serving_size": self.extract_serving_size(text),
            "uncertainties": uncertainties,
        }

    def source_context(self, data):
        source_service = self.core.source
        source_id = data.get("source_id", "")
        source = None
        if source_id:
            source = source_service.source_db.get(id=source_id)
            if source is None:
                raise Exception("출처를 찾을 수 없습니다.")
        source_url = source_service.normalize_url(data.get("source_url") or (source or {}).get("source_url") or "")
        if source_url and source is None:
            source = source_service.get_by_url(source_url)
            if source:
                source_id = source.get("id", "")
        source_type = data.get("source_type") or (source or {}).get("source_type", "")
        if not source_type:
            source_type = source_service.detect_source_type(source_url) if source_url else self.constants.SOURCE_TYPES["DIRECT"]
        source_title = self.first_text([data.get("source_title"), data.get("title"), (source or {}).get("title")])
        source_author = self.first_text([data.get("source_author"), data.get("author"), data.get("channel"), (source or {}).get("author")])
        source_summary = self.first_text([data.get("source_summary"), data.get("description"), (source or {}).get("collected_text_summary")])
        if source_url and source is None:
            source_id = source_service.create({
                "source_type": source_type,
                "source_url": source_url,
                "title": source_title,
                "author": source_author,
                "thumbnail_url": data.get("thumbnail_url", ""),
                "collected_text_summary": source_summary,
                "robots_allowed": self.bool_value(data.get("robots_allowed"), False),
                "crawl_status": self.constants.CRAWLING_STATUSES["PENDING"],
            })
            source = source_service.source_db.get(id=source_id)
        return source_id, source, source_type, source_url, source_title, source_author, source_summary

    def parse_recipe_summary(self, data, admin_user_id=""):
        data = dict(data or {})
        source_id, source, source_type, source_url, source_title, source_author, source_summary = self.source_context(data)
        text = self.first_text([data.get("text"), data.get("content"), data.get("raw_text"), source_summary, source_title])
        if not text:
            raise Exception("요약할 원문 또는 수집 요약을 입력해주세요.")
        prompt_version = data.get("prompt_version", "")
        if not prompt_version:
            prompt = self.ensure_recipe_summary_prompt(admin_user_id)
            prompt_version = prompt.get("prompt_version", "")
        log_id = ""
        try:
            log_id = self.create_log({
                "request_type": self.constants.AI_PROMPT_TYPES["RECIPE_SUMMARY"],
                "target_id": source_id,
                "prompt_version": prompt_version,
                "input_summary": text[:1000],
            })
            title = self.first_text([data.get("dish_name"), data.get("name"), data.get("title"), source_title], "AI 요약 레시피")
            candidate = self.extract_recipe_candidate(text, title=title)
            dish_id = data.get("dish_id", "")
            if dish_id:
                dish = self.core.recipe.get_dish(dish_id, public=False)
                if dish is None:
                    raise Exception("레시피를 찾을 수 없습니다.")
            else:
                dish_id = self.core.recipe.create_dish({
                    "name": title[:160],
                    "description": candidate["summary"],
                    "category": data.get("category", "일반"),
                    "tags": self.core.json_dumps(data.get("tags") or ["AI요약", source_type]),
                    "thumbnail_url": data.get("thumbnail_url") or (source or {}).get("thumbnail_url", ""),
                    "status": self.constants.RECIPE_STATUSES["PENDING_REVIEW"],
                })
                dish = self.core.recipe.get_dish(dish_id, public=False)
            version_id = self.core.recipe.create_version(dish_id, {
                "title": data.get("version_title") or title[:200],
                "source_type": source_type,
                "source_url": source_url,
                "source_title": source_title,
                "source_author": source_author,
                "source_collected_at": (source or {}).get("collected_at") or self.core.now(),
                "summary": candidate["summary"],
                "ingredients": self.core.json_dumps(candidate["ingredients"]),
                "steps": self.core.json_dumps(candidate["steps"]),
                "cooking_tips": self.core.json_dumps(candidate["cooking_tips"]),
                "failure_prevention_tips": self.core.json_dumps(candidate["failure_prevention_tips"]),
                "substitution_tips": self.core.json_dumps(candidate["substitution_tips"]),
                "nutrition_info": self.core.json_dumps({}),
                "sodium_info": self.core.json_dumps({}),
                "allergen_info": self.core.json_dumps(candidate["allergen_info"]),
                "difficulty": data.get("difficulty", "normal"),
                "cooking_time": candidate["cooking_time"],
                "serving_size": candidate["serving_size"],
                "ai_modified": False,
                "status": self.constants.RECIPE_STATUSES["PENDING_REVIEW"],
            })
            version = self.core.recipe.get_version(version_id, public=False)
            if source_id:
                self.core.source.update(source_id, {
                    "crawl_status": self.constants.CRAWLING_STATUSES["SUMMARIZED"],
                    "collected_text_summary": candidate["summary"],
                    "collected_at": self.core.now(),
                    "error_message": "",
                })
                source = self.core.source.source_db.get(id=source_id)
            self.log_db.update({"target_id": version_id}, id=log_id)
            self.finish_log(log_id, output_summary=f"{title} / {version_id}")
            log = self.log_db.get(id=log_id)
        except Exception as error:
            if log_id:
                self.fail_log(log_id, str(error))
            raise
        return {
            "dish": dish,
            "version": version,
            "source": source,
            "candidate": candidate,
            "log": log,
        }

    def create_modification(self, data):
        now = self.core.now()
        data = dict(data or {})
        data.setdefault("status", self.constants.AI_STATUSES["PENDING_REVIEW"])
        data.setdefault("purpose", self.constants.AI_PURPOSES["TASTIER"])
        data.setdefault("risk_flags", "[]")
        data["confidence_score"] = self.normalize_confidence_score(data.get("confidence_score"), self.estimate_confidence_score(data))
        data["created_at"] = now
        data["updated_at"] = now
        modification_id = self.modification_db.insert(data)
        self.auto_approve_if_confident(modification_id)
        return modification_id

    def update_modification(self, modification_id, data):
        data = dict(data or {})
        data["updated_at"] = self.core.now()
        self.modification_db.update(data, id=modification_id)

    def approve_modification(self, modification_id, reviewer_user_id, reason=""):
        self.update_modification(modification_id, {
            "status": self.constants.AI_STATUSES["APPROVED"],
            "reviewed_by": reviewer_user_id,
            "reviewed_at": self.core.now(),
        })

    def reject_modification(self, modification_id, reviewer_user_id, reason=""):
        self.update_modification(modification_id, {
            "status": self.constants.AI_STATUSES["REJECTED"],
            "reviewed_by": reviewer_user_id,
            "rejected_reason": reason,
            "reviewed_at": self.core.now(),
        })

    def auto_approve_if_confident(self, modification_id):
        item = self.modification_db.get(id=modification_id)
        if not item or item.get("status") != self.constants.AI_STATUSES["PENDING_REVIEW"]:
            return False
        threshold = self.get_settings().get("auto_approve_threshold", AI_SETTINGS_DEFAULT["auto_approve_threshold"])
        score = self.normalize_confidence_score(item.get("confidence_score"))
        if score < threshold:
            return False
        self.update_modification(modification_id, {
            "status": self.constants.AI_STATUSES["APPROVED"],
            "reviewed_by": "auto",
            "reviewed_at": self.core.now(),
        })
        return True

    def pending_reviews(self, page=1, dump=20):
        filters = {"status": self.constants.AI_STATUSES["PENDING_REVIEW"]}
        rows = self.modification_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.modification_db.count(**filters) or 0
        return rows, total

    def create_log(self, data):
        now = self.core.now()
        data = self.attach_prompt_version(data)
        data.setdefault("status", self.constants.AI_PROCESSING_STATUSES["PROCESSING"])
        data.setdefault("error_message", "")
        data.setdefault("input_summary", "")
        data.setdefault("output_summary", "")
        data.setdefault("token_usage", "{}")
        data["started_at"] = data.get("started_at") or now
        data["created_at"] = now
        return self.log_db.insert(data)

    def finish_log(self, log_id, output_summary=""):
        data = {
            "status": self.constants.AI_PROCESSING_STATUSES["COMPLETED"],
            "finished_at": self.core.now(),
        }
        if output_summary:
            data["output_summary"] = output_summary
        self.log_db.update(data, id=log_id)

    def fail_log(self, log_id, error_message):
        self.log_db.update({
            "status": self.constants.AI_PROCESSING_STATUSES["FAILED"],
            "finished_at": self.core.now(),
            "error_message": error_message,
        }, id=log_id)

    def generate_recipe_meta(self, dish_id):
        dish = self.core.recipe.get_dish(dish_id, public=False)
        if dish is None:
            raise Exception("레시피를 찾을 수 없습니다.")
        versions, total = self.core.recipe.versions(dish_id, public=False, page=1, dump=1)
        version = versions[0] if versions else {}
        tags = self.core.json_loads(dish.get("tags"), [])
        ingredients = self.core.json_loads(version.get("ingredients"), [])
        steps = self.core.json_loads(version.get("steps"), [])
        category = dish.get("category") or "일반"
        base_name = dish.get("name") or version.get("title") or "레시피"
        title_bits = []
        if category and category not in base_name:
            title_bits.append(category)
        if tags:
            title_bits.append(tags[0])
        title_bits.append(base_name)
        title = " ".join([item for item in title_bits if item])[:80]
        if dish.get("description"):
            description = dish.get("description")
        else:
            main_ingredients = ", ".join(ingredients[:3]) if ingredients else "기본 재료"
            description = f"{main_ingredients}를 중심으로 준비해 맛과 조리 흐름을 한눈에 확인할 수 있는 {category} 레시피입니다."
        step_lines = steps[:5] or ["재료를 손질합니다.", "목적에 맞게 조리하고 간을 조절합니다.", "완성 후 맛과 식감을 확인합니다."]
        script_lines = [
            f"오늘은 {title}를 만들어봅니다.",
            f"핵심 재료는 {', '.join(ingredients[:4]) if ingredients else '준비한 재료'}입니다.",
        ]
        for index, step in enumerate(step_lines, start=1):
            script_lines.append(f"{index}단계, {step}")
        script_lines.append("마지막으로 간과 식감을 확인한 뒤 따뜻할 때 담아냅니다.")
        return {
            "title": title,
            "description": description[:300],
            "script": "\n".join(script_lines),
        }

Model = AI

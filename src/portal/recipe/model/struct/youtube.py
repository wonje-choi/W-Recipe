import json
import os

YOUTUBE_SETTINGS_DEFAULT = {
    "api_key": "",
}

class Youtube:
    UPLOAD_ENDPOINT = "https://www.googleapis.com/upload/youtube/v3/videos"

    def __init__(self, core):
        self.core = core
        self.constants = core.constants

    def fs(self):
        return wiz.project.fs("config")

    def settings_path(self):
        try:
            return wiz.project.path(os.path.join("config", "youtube_settings.json"))
        except Exception:
            return os.path.join("config", "youtube_settings.json")

    def get_settings(self):
        settings = dict(YOUTUBE_SETTINGS_DEFAULT)
        try:
            raw = self.fs().read("youtube_settings.json", "")
            loaded = json.loads(raw) if raw else {}
            if isinstance(loaded, dict):
                settings.update(loaded)
        except Exception:
            try:
                with open(self.settings_path(), "r", encoding="utf-8") as fp:
                    loaded = json.load(fp)
                if isinstance(loaded, dict):
                    settings.update(loaded)
            except Exception:
                pass
        settings["api_key"] = str(settings.get("api_key") or "")
        return settings

    def save_settings(self, data):
        settings = self.get_settings()
        settings["api_key"] = str((data or {}).get("api_key", settings.get("api_key", ""))).strip()
        try:
            self.fs().write.json("youtube_settings.json", settings)
        except Exception:
            path = self.settings_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(settings, fp, ensure_ascii=False, indent=2)
        return settings

    def masked_settings(self):
        settings = self.get_settings()
        api_key = settings.get("api_key", "")
        return {
            "apiKeyConfigured": bool(api_key),
            "apiKey": api_key if not api_key else f"{api_key[:4]}...{api_key[-4:]}",
        }

    def build_upload_metadata(self, dish_id):
        dish = self.core.recipe.get_dish(dish_id, public=False)
        if dish is None:
            raise Exception("레시피를 찾을 수 없습니다.")
        versions, _ = self.core.recipe.versions(dish_id, public=False, page=1, dump=1)
        version = versions[0] if versions else {}
        generated = self.core.ai.generate_recipe_meta(dish_id)
        tags = self.core.json_loads(dish.get("tags"), [])
        category = dish.get("category") or "레시피"
        ingredients = self.core.json_loads(version.get("ingredients"), [])
        steps = self.core.json_loads(version.get("steps"), [])
        title = generated.get("title") or dish.get("name") or version.get("title") or "레시피 영상"
        description_parts = [
            generated.get("description") or dish.get("description") or version.get("summary") or "",
            "",
            "[영상 대본]",
            generated.get("script") or "",
        ]
        if ingredients:
            description_parts += ["", "[재료]", "\n".join([f"- {item}" for item in ingredients[:12]])]
        if steps:
            description_parts += ["", "[조리 순서]", "\n".join([f"{idx + 1}. {step}" for idx, step in enumerate(steps[:10])])]
        tag_values = []
        for value in tags + [category, "레시피", "요리"]:
            value = str(value or "").strip()
            if value and value not in tag_values:
                tag_values.append(value)
        settings = self.get_settings()
        return {
            "title": title[:100],
            "description": "\n".join(description_parts).strip()[:4500],
            "tags": tag_values[:15],
            "categoryId": "26",
            "privacyStatus": "private",
            "script": generated.get("script", ""),
            "uploadEndpoint": self.UPLOAD_ENDPOINT,
            "apiKeyConfigured": bool(settings.get("api_key")),
            "apiKeyRequired": not bool(settings.get("api_key")),
        }

Model = Youtube

class User:
    def __init__(self, core):
        self.core = core
        self.user_db = core.db("user")
        self.preference_db = core.db("user_preference")
        self.constants = core.constants

    def get(self, user_id=None, email=None):
        if user_id:
            return self.user_db.get(id=user_id)
        if email:
            return self.user_db.get(email=email)
        return None

    def create(self, data):
        now = self.core.now()
        data = dict(data or {})
        data.setdefault("role", self.constants.USER_ROLES["USER"])
        data.setdefault("status", self.constants.USER_STATUSES["ACTIVE"])
        data.setdefault("login_failed_count", 0)
        data["created_at"] = now
        data["updated_at"] = now
        return self.user_db.insert(data)

    def update(self, user_id, data):
        data = dict(data or {})
        data["updated_at"] = self.core.now()
        self.user_db.update(data, id=user_id)

    def update_profile(self, user_id, data):
        allowed = {}
        nickname = (data.get("nickname") or "").strip()
        if nickname:
            allowed["nickname"] = nickname[:64]
        if allowed:
            self.update(user_id, allowed)
        return self.get(user_id=user_id)

    def record_login_success(self, user_id):
        self.user_db.update({
            "login_failed_count": 0,
            "last_login_at": self.core.now(),
            "locked_until": None,
            "updated_at": self.core.now(),
        }, id=user_id)

    def record_login_failure(self, user_id, locked_until=None):
        user = self.get(user_id=user_id) or {}
        failed_count = int(user.get("login_failed_count") or 0) + 1
        data = {
            "login_failed_count": failed_count,
            "updated_at": self.core.now(),
        }
        if locked_until is not None:
            data["locked_until"] = locked_until
        self.user_db.update(data, id=user_id)
        return failed_count

    def safe_profile(self, user):
        if not user:
            return None
        return {
            "id": user.get("id"),
            "email": user.get("email", ""),
            "nickname": user.get("nickname", ""),
            "role": user.get("role", self.constants.USER_ROLES["USER"]),
            "status": user.get("status", self.constants.USER_STATUSES["ACTIVE"]),
            "subscriptionPlan": user.get("subscription_plan", self.constants.SUBSCRIPTION_PLANS["FREE"]),
            "subscriptionExpiresAt": self.date_text(user.get("subscription_expires_at")),
            "lastLoginAt": user.get("last_login_at") or "",
            "createdAt": user.get("created_at") or "",
            "updatedAt": user.get("updated_at") or "",
        }

    def date_text(self, value):
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value or "").split(" ")[0]

    def to_list(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        parsed = self.core.json_loads(value, default=[])
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, str) and parsed:
            return [parsed]
        return []

    def to_int(self, value, default=0):
        try:
            if value is None or value == "":
                return default
            return int(value)
        except Exception:
            return default

    def preference(self, user_id):
        return self.preference_db.get(user_id=user_id)

    def preference_payload(self, preference):
        preference = preference or {}
        return {
            "id": preference.get("id", ""),
            "userId": preference.get("user_id", ""),
            "preferredDietTypes": self.to_list(preference.get("preferred_diet_types", "[]")),
            "allergies": self.to_list(preference.get("allergies", "[]")),
            "dislikedIngredients": self.to_list(preference.get("disliked_ingredients", "[]")),
            "preferredCookingTime": self.to_int(preference.get("preferred_cooking_time"), 0),
            "cookingTools": self.to_list(preference.get("cooking_tools", "[]")),
            "babyAgeMonth": preference.get("baby_age_month"),
            "sodiumPreference": preference.get("sodium_preference", "normal"),
            "texturePreference": preference.get("texture_preference", "normal"),
            "createdAt": preference.get("created_at") or "",
            "updatedAt": preference.get("updated_at") or "",
        }

    def normalize_preference(self, data):
        data = dict(data or {})
        preferred_cooking_time = self.to_int(data.get("preferredCookingTime", data.get("preferred_cooking_time", 0)), 0)
        baby_age_month = data.get("babyAgeMonth", data.get("baby_age_month", None))
        if baby_age_month == "":
            baby_age_month = None
        elif baby_age_month is not None:
            baby_age_month = self.to_int(baby_age_month, 0)
        return {
            "preferred_diet_types": self.core.json_dumps(self.to_list(data.get("preferredDietTypes", data.get("preferred_diet_types", [])))),
            "allergies": self.core.json_dumps(self.to_list(data.get("allergies", []))),
            "disliked_ingredients": self.core.json_dumps(self.to_list(data.get("dislikedIngredients", data.get("disliked_ingredients", [])))),
            "preferred_cooking_time": preferred_cooking_time,
            "cooking_tools": self.core.json_dumps(self.to_list(data.get("cookingTools", data.get("cooking_tools", [])))),
            "baby_age_month": baby_age_month,
            "sodium_preference": (data.get("sodiumPreference", data.get("sodium_preference", "normal")) or "normal")[:32],
            "texture_preference": (data.get("texturePreference", data.get("texture_preference", "normal")) or "normal")[:32],
        }

    def save_preference(self, user_id, data):
        now = self.core.now()
        data = self.normalize_preference(data)
        data["user_id"] = user_id
        data["updated_at"] = now
        current = self.preference(user_id)
        if current:
            self.preference_db.update(data, user_id=user_id)
            return current.get("id")
        data["created_at"] = now
        return self.preference_db.insert(data)

    def mask_profile(self, data):
        return self.core.mask_sensitive(data)

Model = User

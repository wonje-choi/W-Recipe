class Recipe:
    URL_FIELDS = {
        "thumbnail_url": "대표 이미지 URL",
        "source_url": "원본 출처 URL",
    }

    def __init__(self, core):
        self.core = core
        self.dish_db = core.db("recipe_dish")
        self.version_db = core.db("recipe_version")
        self.constants = core.constants

    def secure_payload(self, data):
        data = dict(data or {})
        for field, label in self.URL_FIELDS.items():
            if field in data:
                data[field] = self.core.source.validate_optional_url(data.get(field), label)
        return data

    def create_dish(self, data):
        now = self.core.now()
        data = self.secure_payload(data)
        data.setdefault("status", self.constants.RECIPE_STATUSES["DRAFT"])
        data.setdefault("view_count", 0)
        data["created_at"] = now
        data["updated_at"] = now
        return self.dish_db.insert(data)

    def update_dish(self, dish_id, data):
        data = self.secure_payload(data)
        data["updated_at"] = self.core.now()
        self.dish_db.update(data, id=dish_id)

    def get_dish(self, dish_id, public=False):
        dish = self.dish_db.get(id=dish_id)
        if not dish:
            return None
        if public and dish.get("status") != self.core.public_status():
            return None
        return dish

    def search_dishes(self, text="", category="", tag="", status=None, page=1, dump=20, sort="latest"):
        filters = {}
        like_fields = []
        if status is None:
            status = self.core.public_status()
        if status:
            filters["status"] = status
        if category:
            filters["category"] = category
        if text:
            filters["name"] = text
            like_fields.append("name")
        if tag:
            filters["tags"] = tag
            like_fields.append("tags")

        orderby = "created_at"
        order = "DESC"
        if sort in ["view_count", "popular"]:
            orderby = "view_count"
        like = ",".join(like_fields) if like_fields else None
        rows = self.dish_db.rows(page=page, dump=dump, orderby=orderby, order=order, like=like, **filters)
        total = self.dish_db.count(like=like, **filters) or 0
        return rows, total

    def admin_search_dishes(self, text="", category="", tag="", status="", page=1, dump=20, sort="latest"):
        self.core.require_admin()
        return self.search_dishes(
            text=text,
            category=category,
            tag=tag,
            status=status,
            page=page,
            dump=dump,
            sort=sort,
        )

    def create_version(self, dish_id, data):
        now = self.core.now()
        data = self.secure_payload(data)
        data["dish_id"] = dish_id
        data.setdefault("status", self.constants.RECIPE_STATUSES["DRAFT"])
        data.setdefault("view_count", 0)
        data.setdefault("ai_modified", False)
        data["created_at"] = now
        data["updated_at"] = now
        return self.version_db.insert(data)

    def update_version(self, version_id, data):
        data = self.secure_payload(data)
        data["updated_at"] = self.core.now()
        self.version_db.update(data, id=version_id)

    def get_version(self, version_id, public=False):
        version = self.version_db.get(id=version_id)
        if not version:
            return None
        if public and version.get("status") != self.core.public_status():
            return None
        return version

    def versions(self, dish_id, public=False, page=1, dump=20):
        filters = {"dish_id": dish_id}
        if public:
            filters["status"] = self.core.public_status()
        rows = self.version_db.rows(page=page, dump=dump, orderby="view_count", order="DESC", **filters)
        total = self.version_db.count(**filters) or 0
        return rows, total

    def admin_versions(self, dish_id, page=1, dump=20):
        self.core.require_admin()
        return self.versions(dish_id, public=False, page=page, dump=dump)

    def increment_dish_view(self, dish_id):
        dish = self.get_dish(dish_id) or {}
        view_count = int(dish.get("view_count") or 0) + 1
        self.dish_db.update({"view_count": view_count, "updated_at": self.core.now()}, id=dish_id)
        return view_count

    def increment_version_view(self, version_id):
        version = self.get_version(version_id) or {}
        view_count = int(version.get("view_count") or 0) + 1
        self.version_db.update({"view_count": view_count, "updated_at": self.core.now()}, id=version_id)
        return view_count

    def get_recommended(self, user_id, limit=6):
        if not user_id:
            return []
        favorite_rows = self.core.comment.favorite_db.rows(user_id=user_id, page=1, dump=100, orderby="created_at", order="DESC")
        recent_rows = self.core.comment.recent_view_db.rows(user_id=user_id, page=1, dump=100, orderby="viewed_at", order="DESC")
        tag_scores = {}
        seen_dish_ids = set()

        def add_score(key, score):
            key = str(key or "").strip()
            if not key:
                return
            tag_scores[key] = tag_scores.get(key, 0) + score

        def learn_from_version(recipe_version_id, score):
            version = self.get_version(recipe_version_id, public=True)
            if not version:
                return
            dish = self.get_dish(version.get("dish_id"), public=True)
            if not dish:
                return
            seen_dish_ids.add(dish.get("id"))
            add_score(dish.get("category"), score)
            for tag in self.core.json_loads(dish.get("tags"), []):
                add_score(tag, score)

        for row in favorite_rows:
            learn_from_version(row.get("recipe_version_id"), 4)
        for row in recent_rows:
            score = min(3, max(1, int(row.get("view_count") or 1)))
            learn_from_version(row.get("recipe_version_id"), score)

        preference = self.core.user.preference(user_id) or {}
        for tag in self.core.json_loads(preference.get("preferred_diet_types"), []):
            add_score(tag, 3)
        if preference.get("sodium_preference") in ["low", "very_low"]:
            add_score("저염", 3)
        if preference.get("baby_age_month") is not None:
            add_score("이유식", 3)
        if not tag_scores:
            return []

        candidates = self.dish_db.rows(
            status=self.core.public_status(),
            page=1,
            dump=200,
            orderby="view_count",
            order="DESC",
        )
        scored = []
        fallback = []
        for dish in candidates:
            score = 0
            tags = self.core.json_loads(dish.get("tags"), [])
            score += tag_scores.get(dish.get("category", ""), 0)
            for tag in tags:
                score += tag_scores.get(tag, 0)
            if score <= 0:
                continue
            item = (score, int(dish.get("view_count") or 0), dish)
            if dish.get("id") in seen_dish_ids:
                fallback.append(item)
            else:
                scored.append(item)
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        fallback.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in (scored + fallback)[:limit]]

Model = Recipe

class Comment:
    def __init__(self, core):
        self.core = core
        self.comment_db = core.db("comment")
        self.favorite_db = core.db("favorite_recipe")
        self.recent_view_db = core.db("recent_view")
        self.edit_request_db = core.db("recipe_edit_request")
        self.report_db = core.db("report")
        self.constants = core.constants

    def create(self, user_id, recipe_version_id, content, parent_id=""):
        now = self.core.now()
        return self.comment_db.insert({
            "recipe_version_id": recipe_version_id,
            "user_id": user_id,
            "parent_id": parent_id,
            "content": self.core.clean_user_text(content, "댓글 내용"),
            "status": self.constants.COMMENT_STATUSES["VISIBLE"],
            "created_at": now,
            "updated_at": now,
        })

    def rows(self, recipe_version_id, page=1, dump=20, visible_only=True):
        filters = {"recipe_version_id": recipe_version_id}
        if visible_only:
            filters["status"] = self.constants.COMMENT_STATUSES["VISIBLE"]
        rows = self.comment_db.rows(page=page, dump=dump, orderby="created_at", order="ASC", **filters)
        total = self.comment_db.count(**filters) or 0
        return rows, total

    def hide(self, comment_id, moderator_user_id, reason=""):
        self.comment_db.update({
            "status": self.constants.COMMENT_STATUSES["HIDDEN"],
            "moderated_by": moderator_user_id,
            "moderation_reason": reason,
            "moderated_at": self.core.now(),
            "updated_at": self.core.now(),
        }, id=comment_id)

    def add_favorite(self, user_id, recipe_version_id):
        existing = self.favorite_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        if existing:
            return existing.get("id")
        return self.favorite_db.insert({
            "user_id": user_id,
            "recipe_version_id": recipe_version_id,
            "created_at": self.core.now(),
        })

    def remove_favorite(self, user_id, recipe_version_id):
        favorite = self.favorite_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        if not favorite:
            return False
        self.favorite_db.delete(id=favorite.get("id"))
        return True

    def toggle_favorite(self, user_id, recipe_version_id):
        favorite = self.favorite_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        if favorite:
            self.favorite_db.delete(id=favorite.get("id"))
            return {"favorited": False}
        favorite_id = self.add_favorite(user_id, recipe_version_id)
        return {"favorited": True, "id": favorite_id}

    def favorites(self, user_id, page=1, dump=20):
        rows = self.favorite_db.rows(user_id=user_id, page=page, dump=dump, orderby="created_at", order="DESC")
        total = self.favorite_db.count(user_id=user_id) or 0
        return rows, total

    def recent_views(self, user_id, page=1, dump=20):
        rows = self.recent_view_db.rows(user_id=user_id, page=page, dump=dump, orderby="viewed_at", order="DESC")
        total = self.recent_view_db.count(user_id=user_id) or 0
        return rows, total

    def request_edit(self, user_id, recipe_version_id, content, reason=""):
        now = self.core.now()
        return self.edit_request_db.insert({
            "recipe_version_id": recipe_version_id,
            "user_id": user_id,
            "content": self.core.clean_user_text(content, "수정 요청 내용"),
            "reason": reason,
            "status": self.constants.EDIT_REQUEST_STATUSES["OPEN"],
            "created_at": now,
            "updated_at": now,
        })

    def edit_requests(self, user_id, page=1, dump=20):
        rows = self.edit_request_db.rows(user_id=user_id, page=page, dump=dump, orderby="created_at", order="DESC")
        total = self.edit_request_db.count(user_id=user_id) or 0
        return rows, total

    def create_report(self, reporter_user_id, target_type, target_id, reason, detail=""):
        existing = self.report_db.get(
            reporter_user_id=reporter_user_id,
            target_type=target_type,
            target_id=target_id,
        )
        if existing:
            return existing.get("id")
        now = self.core.now()
        detail = self.core.clean_user_text(detail, "신고 상세 내용")
        return self.report_db.insert({
            "reporter_user_id": reporter_user_id,
            "target_type": target_type,
            "target_id": target_id,
            "reason": reason,
            "detail": detail,
            "status": self.constants.REPORT_STATUSES["OPEN"],
            "created_at": now,
            "updated_at": now,
        })

    def resolve_report(self, report_id, resolver_user_id, status, resolution_note=""):
        self.report_db.update({
            "status": status,
            "resolver_user_id": resolver_user_id,
            "resolution_note": resolution_note,
            "resolved_at": self.core.now(),
            "updated_at": self.core.now(),
        }, id=report_id)

Model = Comment

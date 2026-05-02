import datetime

class Comment:
    COMMENT_RATE_LIMIT_SECONDS = 20

    def __init__(self, core):
        self.core = core
        self.comment_db = core.db("comment")
        self.favorite_db = core.db("favorite_recipe")
        self.recent_view_db = core.db("recent_view")
        self.edit_request_db = core.db("recipe_edit_request")
        self.report_db = core.db("report")
        self.constants = core.constants

    def parse_datetime(self, value):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    def require_public_version(self, recipe_version_id):
        version = self.core.recipe.get_version(recipe_version_id, public=True)
        if version is None:
            raise Exception("공개 레시피 버전을 찾을 수 없습니다.")
        return version

    def ensure_comment_rate_limit(self, user_id):
        rows = self.comment_db.rows(user_id=user_id, page=1, dump=1, orderby="created_at", order="DESC")
        if not rows:
            return
        created_at = self.parse_datetime(rows[0].get("created_at"))
        if created_at is None:
            return
        elapsed = (datetime.datetime.now() - created_at).total_seconds()
        if elapsed < self.COMMENT_RATE_LIMIT_SECONDS:
            raise Exception("댓글은 잠시 후 다시 작성해주세요.")

    def create(self, user_id, recipe_version_id, content):
        self.require_public_version(recipe_version_id)
        content = self.core.clean_user_text(content, "댓글 내용")
        if len(content) < 2:
            raise Exception("댓글 내용을 2자 이상 입력해주세요.")
        if len(content) > 1000:
            raise Exception("댓글은 1000자 이하로 입력해주세요.")
        self.ensure_comment_rate_limit(user_id)
        now = self.core.now()
        return self.comment_db.insert({
            "recipe_version_id": recipe_version_id,
            "user_id": user_id,
            "content": content,
            "status": self.constants.COMMENT_STATUSES["VISIBLE"],
            "created_at": now,
            "updated_at": now,
        })

    def rows(self, recipe_version_id, page=1, dump=20, visible_only=True):
        self.require_public_version(recipe_version_id)
        filters = {"recipe_version_id": recipe_version_id}
        if visible_only:
            filters["status"] = self.constants.COMMENT_STATUSES["VISIBLE"]
        rows = self.comment_db.rows(page=page, dump=dump, orderby="created_at", order="ASC", **filters)
        total = self.comment_db.count(**filters) or 0
        return rows, total

    def delete(self, comment_id, user_id):
        comment = self.comment_db.get(id=comment_id)
        if not comment:
            raise Exception("댓글을 찾을 수 없습니다.")
        if comment.get("user_id") != user_id and self.core.is_admin() == False:
            raise Exception("댓글을 삭제할 권한이 없습니다.")
        self.comment_db.update({
            "status": self.constants.COMMENT_STATUSES["DELETED"],
            "updated_at": self.core.now(),
        }, id=comment_id)
        return self.comment_db.get(id=comment_id)

    def hide(self, comment_id, moderator_user_id, reason=""):
        self.comment_db.update({
            "status": self.constants.COMMENT_STATUSES["HIDDEN"],
            "updated_at": self.core.now(),
        }, id=comment_id)

    def add_favorite(self, user_id, recipe_version_id):
        self.require_public_version(recipe_version_id)
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
        self.require_public_version(recipe_version_id)
        favorite = self.favorite_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        if favorite:
            self.favorite_db.delete(id=favorite.get("id"))
            return {"favorited": False}
        favorite_id = self.add_favorite(user_id, recipe_version_id)
        return {"favorited": True, "id": favorite_id}

    def favorite_status(self, user_id, recipe_version_id):
        favorite = self.favorite_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        return {"favorited": favorite is not None, "id": (favorite or {}).get("id", "")}

    def favorites(self, user_id, page=1, dump=20):
        rows = self.favorite_db.rows(user_id=user_id, page=page, dump=dump, orderby="created_at", order="DESC")
        total = self.favorite_db.count(user_id=user_id) or 0
        return rows, total

    def record_recent_view(self, user_id, recipe_version_id):
        self.require_public_version(recipe_version_id)
        now = self.core.now()
        existing = self.recent_view_db.get(user_id=user_id, recipe_version_id=recipe_version_id)
        if existing:
            view_count = int(existing.get("view_count") or 0) + 1
            self.recent_view_db.update({
                "view_count": view_count,
                "viewed_at": now,
                "updated_at": now,
            }, id=existing.get("id"))
            return self.recent_view_db.get(id=existing.get("id"))
        recent_id = self.recent_view_db.insert({
            "user_id": user_id,
            "recipe_version_id": recipe_version_id,
            "view_count": 1,
            "viewed_at": now,
            "created_at": now,
            "updated_at": now,
        })
        return self.recent_view_db.get(id=recent_id)

    def recent_views(self, user_id, page=1, dump=20):
        rows = self.recent_view_db.rows(user_id=user_id, page=page, dump=dump, orderby="viewed_at", order="DESC")
        total = self.recent_view_db.count(user_id=user_id) or 0
        return rows, total

    def validate_edit_request_type(self, request_type):
        request_type = (request_type or "").strip()
        if not self.constants.has_value("EDIT_REQUEST_TYPES", request_type):
            raise Exception("지원하지 않는 수정 요청 유형입니다.")
        return request_type

    def request_edit(self, user_id, recipe_version_id, request_type, content, attachment_url=""):
        self.require_public_version(recipe_version_id)
        request_type = self.validate_edit_request_type(request_type)
        content = self.core.clean_user_text(content, "수정 요청 내용")
        attachment_url = self.core.source.validate_optional_url(attachment_url, "첨부 URL")
        if len(content) < 5:
            raise Exception("수정 요청 내용을 5자 이상 입력해주세요.")
        if len(content) > 2000:
            raise Exception("수정 요청은 2000자 이하로 입력해주세요.")
        existing = self.edit_request_db.get(
            user_id=user_id,
            recipe_version_id=recipe_version_id,
            request_type=request_type,
            status=self.constants.EDIT_REQUEST_STATUSES["OPEN"],
        )
        if existing:
            return existing.get("id")
        now = self.core.now()
        return self.edit_request_db.insert({
            "recipe_version_id": recipe_version_id,
            "user_id": user_id,
            "request_type": request_type,
            "content": content,
            "attachment_url": attachment_url,
            "status": self.constants.EDIT_REQUEST_STATUSES["OPEN"],
            "created_at": now,
            "updated_at": now,
        })

    def edit_requests(self, status="", user_id="", page=1, dump=20):
        filters = {}
        if status:
            filters["status"] = status
        if user_id:
            filters["user_id"] = user_id
        rows = self.edit_request_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.edit_request_db.count(**filters) or 0
        return rows, total

    def handle_edit_request(self, request_id, admin_user_id, status, admin_memo=""):
        self.core.require_admin()
        if not self.constants.has_value("EDIT_REQUEST_STATUSES", status):
            raise Exception("지원하지 않는 수정 요청 상태입니다.")
        item = self.edit_request_db.get(id=request_id)
        if not item:
            raise Exception("수정 요청을 찾을 수 없습니다.")
        self.edit_request_db.update({
            "status": status,
            "admin_memo": admin_memo or "",
            "handled_by": admin_user_id,
            "handled_at": self.core.now(),
            "updated_at": self.core.now(),
        }, id=request_id)
        return self.edit_request_db.get(id=request_id)

    def validate_report_target(self, target_type, target_id):
        target_type = (target_type or "").strip()
        if not self.constants.has_value("REPORT_TARGET_TYPES", target_type):
            raise Exception("지원하지 않는 신고 대상입니다.")
        if target_type == self.constants.REPORT_TARGET_TYPES["COMMENT"]:
            target = self.comment_db.get(id=target_id)
        elif target_type == self.constants.REPORT_TARGET_TYPES["RECIPE_VERSION"]:
            target = self.core.recipe.get_version(target_id, public=True)
        else:
            target = self.core.recipe.get_dish(target_id, public=True)
        if not target:
            raise Exception("신고 대상을 찾을 수 없습니다.")
        return target_type

    def validate_report_reason(self, reason):
        reason = (reason or "").strip()
        if not self.constants.has_value("REPORT_REASONS", reason):
            raise Exception("지원하지 않는 신고 사유입니다.")
        return reason

    def create_report(self, reporter_user_id, target_type, target_id, reason, detail=""):
        target_type = self.validate_report_target(target_type, target_id)
        reason = self.validate_report_reason(reason)
        detail = self.core.clean_user_text(detail, "신고 상세 내용")
        if len(detail) > 2000:
            raise Exception("신고 상세 내용은 2000자 이하로 입력해주세요.")
        existing = self.report_db.get(
            reporter_user_id=reporter_user_id,
            target_type=target_type,
            target_id=target_id,
        )
        if existing:
            return existing.get("id")
        now = self.core.now()
        report_id = self.report_db.insert({
            "reporter_user_id": reporter_user_id,
            "target_type": target_type,
            "target_id": target_id,
            "reason": reason,
            "detail": detail,
            "status": self.constants.REPORT_STATUSES["OPEN"],
            "created_at": now,
            "updated_at": now,
        })
        if target_type == self.constants.REPORT_TARGET_TYPES["COMMENT"]:
            comment = self.comment_db.get(id=target_id) or {}
            report_count = int(comment.get("report_count") or 0) + 1
            self.comment_db.update({
                "report_count": report_count,
                "status": self.constants.COMMENT_STATUSES["REPORTED"],
                "updated_at": now,
            }, id=target_id)
        return report_id

    def reports(self, status="", target_type="", page=1, dump=20):
        filters = {}
        if status:
            filters["status"] = status
        if target_type:
            filters["target_type"] = target_type
        rows = self.report_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.report_db.count(**filters) or 0
        return rows, total

    def resolve_report(self, report_id, resolver_user_id, status, admin_memo=""):
        self.core.require_admin()
        if not self.constants.has_value("REPORT_STATUSES", status):
            raise Exception("지원하지 않는 신고 처리 상태입니다.")
        item = self.report_db.get(id=report_id)
        if not item:
            raise Exception("신고를 찾을 수 없습니다.")
        self.report_db.update({
            "status": status,
            "admin_memo": admin_memo or "",
            "handled_by": resolver_user_id,
            "handled_at": self.core.now(),
            "updated_at": self.core.now(),
        }, id=report_id)
        return self.report_db.get(id=report_id)

Model = Comment

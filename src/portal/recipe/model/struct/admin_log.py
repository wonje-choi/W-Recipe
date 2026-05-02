class AdminLog:
    def __init__(self, core):
        self.core = core
        self.log_db = core.db("admin_action_log")

    def create(self, action_type, target_type, target_id="", before_value=None, after_value=None, admin_user_id=""):
        before_value = self.core.mask_sensitive(before_value or {})
        after_value = self.core.mask_sensitive(after_value or {})
        if not admin_user_id:
            admin_user_id = self.core.session_user_id()
        return self.log_db.insert({
            "admin_user_id": admin_user_id,
            "action_type": action_type,
            "target_type": target_type,
            "target_id": target_id or "",
            "before_value": self.core.json_dumps(before_value),
            "after_value": self.core.json_dumps(after_value),
            "ip_address": wiz.request.ip(),
            "user_agent": wiz.request.headers("User-Agent", ""),
            "created_at": self.core.now(),
        })

    def rows(self, action_type="", target_type="", admin_user_id="", page=1, dump=20):
        self.core.require_admin()
        filters = {}
        if action_type:
            filters["action_type"] = action_type
        if target_type:
            filters["target_type"] = target_type
        if admin_user_id:
            filters["admin_user_id"] = admin_user_id
        rows = self.log_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.log_db.count(**filters) or 0
        return rows, total

Model = AdminLog

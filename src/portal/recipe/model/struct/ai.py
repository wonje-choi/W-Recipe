class AI:
    def __init__(self, core):
        self.core = core
        self.modification_db = core.db("ai_recipe_modification")
        self.log_db = core.db("ai_processing_log")
        self.constants = core.constants

    def create_modification(self, data):
        now = self.core.now()
        data = dict(data or {})
        data.setdefault("status", self.constants.AI_STATUSES["PENDING_REVIEW"])
        data.setdefault("purpose", self.constants.AI_PURPOSES["TASTIER"])
        data.setdefault("risk_flags", "[]")
        data["created_at"] = now
        data["updated_at"] = now
        return self.modification_db.insert(data)

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

    def pending_reviews(self, page=1, dump=20):
        filters = {"status": self.constants.AI_STATUSES["PENDING_REVIEW"]}
        rows = self.modification_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.modification_db.count(**filters) or 0
        return rows, total

    def create_log(self, data):
        now = self.core.now()
        data = dict(data or {})
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

Model = AI

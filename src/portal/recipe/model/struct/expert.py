class Expert:
    def __init__(self, core):
        self.core = core
        self.expert_db = core.db("expert")
        self.assignment_db = core.db("expert_assignment")
        self.constants = core.constants

    def validate_status(self, status):
        status = (status or self.constants.EXPERT_STATUSES["ACTIVE"]).strip()
        if not self.constants.has_value("EXPERT_STATUSES", status):
            raise Exception("지원하지 않는 전문가 상태입니다.")
        return status

    def validate_assignment_status(self, status):
        status = (status or self.constants.EXPERT_ASSIGNMENT_STATUSES["ASSIGNED"]).strip()
        if not self.constants.has_value("EXPERT_ASSIGNMENT_STATUSES", status):
            raise Exception("지원하지 않는 배정 상태입니다.")
        return status

    def validate_target_type(self, target_type):
        target_type = (target_type or "").strip()
        if not self.constants.has_value("EXPERT_ASSIGNMENT_TARGET_TYPES", target_type):
            raise Exception("지원하지 않는 전문가 배정 대상입니다.")
        return target_type

    def validate_target(self, target_type, target_id):
        target_type = self.validate_target_type(target_type)
        if target_type == self.constants.EXPERT_ASSIGNMENT_TARGET_TYPES["EDIT_REQUEST"]:
            target = self.core.comment.edit_request_db.get(id=target_id)
        else:
            target = self.core.db("ai_recipe_modification").get(id=target_id)
        if not target:
            raise Exception("전문가 배정 대상을 찾을 수 없습니다.")
        return target_type

    def list(self, status="", page=1, dump=100):
        filters = {}
        if status:
            filters["status"] = self.validate_status(status)
        rows = self.expert_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.expert_db.count(**filters) or 0
        return rows, total

    def active_options(self):
        rows, _ = self.list(status=self.constants.EXPERT_STATUSES["ACTIVE"], page=1, dump=100)
        return rows

    def get(self, expert_id):
        if not expert_id:
            return None
        return self.expert_db.get(id=expert_id)

    def save(self, data):
        data = dict(data or {})
        name = self.core.clean_user_text(data.get("name", ""), "전문가 이름")[:64]
        if len(name) < 2:
            raise Exception("전문가 이름을 2자 이상 입력해주세요.")
        email = (data.get("email") or "").strip()[:190]
        specialty = self.core.clean_user_text(data.get("specialty", ""), "전문 분야")[:128]
        status = self.validate_status(data.get("status"))
        now = self.core.now()
        expert_id = data.get("id", "")
        payload = {
            "name": name,
            "email": email,
            "specialty": specialty,
            "status": status,
            "updated_at": now,
        }
        if expert_id:
            if not self.expert_db.get(id=expert_id):
                raise Exception("전문가를 찾을 수 없습니다.")
            self.expert_db.update(payload, id=expert_id)
            return self.expert_db.get(id=expert_id)
        payload["created_at"] = now
        expert_id = self.expert_db.insert(payload)
        return self.expert_db.get(id=expert_id)

    def assignment_for(self, target_type, target_id):
        target_type = self.validate_target_type(target_type)
        return self.assignment_db.get(target_type=target_type, target_id=target_id)

    def assignment_map(self, target_type, target_ids):
        target_type = self.validate_target_type(target_type)
        target_ids = set([item for item in target_ids if item])
        if not target_ids:
            return {}
        rows = self.assignment_db.rows(target_type=target_type, page=1, dump=1000, orderby="assigned_at", order="DESC")
        result = {}
        for row in rows:
            target_id = row.get("target_id")
            if target_id in target_ids and target_id not in result:
                result[target_id] = row
        return result

    def assign(self, target_type, target_id, expert_id, status="assigned", review_note=""):
        target_type = self.validate_target(target_type, target_id)
        expert = self.get(expert_id)
        if not expert or expert.get("status") != self.constants.EXPERT_STATUSES["ACTIVE"]:
            raise Exception("활성 전문가를 선택해주세요.")
        status = self.validate_assignment_status(status)
        review_note = self.core.clean_user_text(review_note or "", "검수 의견")[:2000]
        now = self.core.now()
        existing = self.assignment_for(target_type, target_id)
        payload = {
            "expert_id": expert_id,
            "status": status,
            "review_note": review_note,
            "updated_at": now,
        }
        if status == self.constants.EXPERT_ASSIGNMENT_STATUSES["REVIEWED"]:
            payload["reviewed_at"] = now
        if existing:
            self.assignment_db.update(payload, id=existing.get("id"))
            return self.assignment_db.get(id=existing.get("id"))
        payload.update({
            "target_type": target_type,
            "target_id": target_id,
            "assigned_at": now,
            "created_at": now,
        })
        assignment_id = self.assignment_db.insert(payload)
        return self.assignment_db.get(id=assignment_id)

Model = Expert

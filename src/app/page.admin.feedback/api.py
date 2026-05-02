import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

COMMENT_STATUS_LABELS = {
    "visible": "표시",
    "hidden": "숨김",
    "deleted": "삭제",
    "reported": "신고됨",
}

EDIT_STATUS_LABELS = {
    "open": "접수",
    "in_review": "검토 중",
    "resolved": "해결",
    "rejected": "반려",
}

EDIT_TYPE_LABELS = {
    "error": "오류 제보",
    "measurement_issue": "계량 문제",
    "source_issue": "출처 문제",
    "taste_improvement": "맛 개선",
    "other": "기타",
}

REPORT_STATUS_LABELS = {
    "open": "접수",
    "in_review": "검토 중",
    "actioned": "조치 완료",
    "rejected": "반려",
}

REPORT_TARGET_LABELS = {
    "comment": "댓글",
    "recipe_version": "레시피 버전",
    "recipe_dish": "레시피",
}

REPORT_REASON_LABELS = {
    "spam": "스팸",
    "inappropriate": "부적절한 내용",
    "wrong_info": "잘못된 정보",
    "safety_issue": "안전 문제",
    "copyright": "저작권",
    "other": "기타",
}

USER_STATUS_LABELS = {
    "active": "활성",
    "suspended": "정지",
    "deleted": "탈퇴",
    "pending": "대기",
}

SUBSCRIPTION_PLAN_LABELS = {
    "free": "Free",
    "premium": "Premium",
}

EXPERT_STATUS_LABELS = {
    "active": "활성",
    "inactive": "비활성",
}

EXPERT_ASSIGNMENT_STATUS_LABELS = {
    "assigned": "배정",
    "in_review": "검수 중",
    "reviewed": "검수 완료",
}


def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value in ["true", "True", "1", 1]:
        return True
    if value in ["false", "False", "0", 0]:
        return False
    return default


def clamp_dump(value):
    dump = to_int(value, constants.DEFAULT_DUMP)
    if dump < 1:
        return constants.DEFAULT_DUMP
    if dump > constants.MAX_DUMP:
        return constants.MAX_DUMP
    return dump


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def date_only(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return str(value or "").split(" ")[0]


def request_data():
    raw = wiz.request.query("data", "")
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            raise Exception("data는 JSON 객체 문자열이어야 합니다.")
    data = wiz.request.query()
    if isinstance(data, dict):
        return data
    return {}


def option_items(values, labels):
    return [{"value": value, "label": labels.get(value, value)} for value in values]


def paginate(rows, page, dump):
    total = len(rows)
    start = max(0, (page - 1) * dump)
    return rows[start:start + dump], total


def safe_count(db, **filters):
    try:
        return db.count(**filters) or 0
    except Exception:
        return 0


def reported_comment_count():
    total = 0
    rows = struct.comment.comment_db.rows(page=1, dump=1000, orderby="created_at", order="DESC")
    for row in rows:
        report_count = int(row.get("report_count") or 0)
        if report_count > 0 or row.get("status") == constants.COMMENT_STATUSES["REPORTED"]:
            total += 1
    return total


def summary_counts():
    comment_db = struct.comment.comment_db
    edit_request_db = struct.comment.edit_request_db
    report_db = struct.comment.report_db
    user_db = struct.db("user")
    return {
        "comments": safe_count(comment_db),
        "reportedComments": reported_comment_count(),
        "openReports": safe_count(report_db, status=constants.REPORT_STATUSES["OPEN"]),
        "openEditRequests": safe_count(edit_request_db, status=constants.EDIT_REQUEST_STATUSES["OPEN"]),
        "premiumMembers": safe_count(user_db, subscription_plan=constants.SUBSCRIPTION_PLANS["PREMIUM"]),
    }


def user_dto(user_id):
    if not user_id:
        return {"id": "", "email": "", "nickname": "", "status": ""}
    user = struct.user.get(user_id=user_id) or {}
    status = user.get("status", "")
    subscription_plan = user.get("subscription_plan", constants.SUBSCRIPTION_PLANS["FREE"])
    return {
        "id": user.get("id", user_id),
        "email": user.get("email", ""),
        "nickname": user.get("nickname", ""),
        "role": user.get("role", ""),
        "status": status,
        "statusLabel": USER_STATUS_LABELS.get(status, status),
        "subscriptionPlan": subscription_plan,
        "subscriptionPlanLabel": SUBSCRIPTION_PLAN_LABELS.get(subscription_plan, subscription_plan),
        "subscriptionExpiresAt": date_only(user.get("subscription_expires_at")),
    }


def member_dto(user):
    return user_dto(user.get("id", ""))


def expert_dto(expert):
    if not expert:
        return None
    status = expert.get("status", constants.EXPERT_STATUSES["ACTIVE"])
    return {
        "id": expert.get("id", ""),
        "name": expert.get("name", ""),
        "email": expert.get("email", ""),
        "specialty": expert.get("specialty", ""),
        "status": status,
        "statusLabel": EXPERT_STATUS_LABELS.get(status, status),
        "createdAt": date_text(expert.get("created_at")),
        "updatedAt": date_text(expert.get("updated_at")),
    }


def assignment_dto(assignment):
    if not assignment:
        return {
            "id": "",
            "targetType": constants.EXPERT_ASSIGNMENT_TARGET_TYPES["EDIT_REQUEST"],
            "targetId": "",
            "expertId": "",
            "expert": None,
            "status": "",
            "statusLabel": "미배정",
            "reviewNote": "",
            "assignedAt": "",
            "reviewedAt": "",
        }
    status = assignment.get("status", "")
    expert = struct.expert.get(assignment.get("expert_id", ""))
    return {
        "id": assignment.get("id", ""),
        "targetType": assignment.get("target_type", ""),
        "targetId": assignment.get("target_id", ""),
        "expertId": assignment.get("expert_id", ""),
        "expert": expert_dto(expert),
        "status": status,
        "statusLabel": EXPERT_ASSIGNMENT_STATUS_LABELS.get(status, status),
        "reviewNote": assignment.get("review_note", ""),
        "assignedAt": date_text(assignment.get("assigned_at")),
        "reviewedAt": date_text(assignment.get("reviewed_at")),
    }


def recipe_context(recipe_version_id):
    version = struct.db("recipe_version").get(id=recipe_version_id) or {}
    dish = {}
    if version.get("dish_id"):
        dish = struct.db("recipe_dish").get(id=version.get("dish_id")) or {}
    return {
        "recipeVersionId": recipe_version_id,
        "versionTitle": version.get("title", ""),
        "dishId": version.get("dish_id", ""),
        "dishName": dish.get("name", ""),
        "status": version.get("status", ""),
    }


def comment_dto(comment):
    status = comment.get("status", "")
    report_count = int(comment.get("report_count") or 0)
    return {
        "id": comment.get("id"),
        "userId": comment.get("user_id", ""),
        "user": user_dto(comment.get("user_id", "")),
        "recipeVersionId": comment.get("recipe_version_id", ""),
        "recipe": recipe_context(comment.get("recipe_version_id", "")),
        "content": comment.get("content", ""),
        "status": status,
        "statusLabel": COMMENT_STATUS_LABELS.get(status, status),
        "reportCount": report_count,
        "reported": report_count > 0 or status == constants.COMMENT_STATUSES["REPORTED"],
        "createdAt": date_text(comment.get("created_at")),
        "updatedAt": date_text(comment.get("updated_at")),
    }


def target_dto(target_type, target_id):
    if target_type == constants.REPORT_TARGET_TYPES["COMMENT"]:
        comment = struct.comment.comment_db.get(id=target_id) or {}
        dto = comment_dto(comment) if comment else {}
        return {
            "id": target_id,
            "type": target_type,
            "label": REPORT_TARGET_LABELS.get(target_type, target_type),
            "title": (comment.get("content", "")[:80] if comment else "댓글 없음"),
            "comment": dto,
            "user": dto.get("user", {}) if dto else {},
        }
    if target_type == constants.REPORT_TARGET_TYPES["RECIPE_VERSION"]:
        recipe = recipe_context(target_id)
        return {
            "id": target_id,
            "type": target_type,
            "label": REPORT_TARGET_LABELS.get(target_type, target_type),
            "title": recipe.get("versionTitle") or recipe.get("dishName") or target_id,
            "recipe": recipe,
        }
    dish = struct.db("recipe_dish").get(id=target_id) or {}
    return {
        "id": target_id,
        "type": target_type,
        "label": REPORT_TARGET_LABELS.get(target_type, target_type),
        "title": dish.get("name", target_id),
        "dish": dish,
    }


def report_dto(report):
    status = report.get("status", "")
    target_type = report.get("target_type", "")
    reason = report.get("reason", "")
    return {
        "id": report.get("id"),
        "reporterUserId": report.get("reporter_user_id", ""),
        "reporter": user_dto(report.get("reporter_user_id", "")),
        "targetType": target_type,
        "targetTypeLabel": REPORT_TARGET_LABELS.get(target_type, target_type),
        "targetId": report.get("target_id", ""),
        "target": target_dto(target_type, report.get("target_id", "")),
        "reason": reason,
        "reasonLabel": REPORT_REASON_LABELS.get(reason, reason),
        "detail": report.get("detail", ""),
        "status": status,
        "statusLabel": REPORT_STATUS_LABELS.get(status, status),
        "adminMemo": report.get("admin_memo", ""),
        "handledBy": report.get("handled_by", ""),
        "handledAt": date_text(report.get("handled_at")),
        "createdAt": date_text(report.get("created_at")),
        "updatedAt": date_text(report.get("updated_at")),
    }


def edit_request_dto(item, assignment=None):
    status = item.get("status", "")
    request_type = item.get("request_type", "")
    return {
        "id": item.get("id"),
        "userId": item.get("user_id", ""),
        "user": user_dto(item.get("user_id", "")),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "recipe": recipe_context(item.get("recipe_version_id", "")),
        "requestType": request_type,
        "requestTypeLabel": EDIT_TYPE_LABELS.get(request_type, request_type),
        "content": item.get("content", ""),
        "attachmentUrl": item.get("attachment_url", ""),
        "status": status,
        "statusLabel": EDIT_STATUS_LABELS.get(status, status),
        "adminMemo": item.get("admin_memo", ""),
        "handledBy": item.get("handled_by", ""),
        "handledAt": date_text(item.get("handled_at")),
        "expertAssignment": assignment_dto(assignment),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def comment_matches(row, text, reported_only):
    if reported_only:
        report_count = int(row.get("report_count") or 0)
        if report_count <= 0 and row.get("status") != constants.COMMENT_STATUSES["REPORTED"]:
            return False
    if not text:
        return True
    needle = text.lower()
    haystack = " ".join([
        row.get("id", ""),
        row.get("user_id", ""),
        row.get("recipe_version_id", ""),
        row.get("content", ""),
        row.get("status", ""),
    ]).lower()
    return needle in haystack


def report_matches(row, text):
    if not text:
        return True
    needle = text.lower()
    haystack = " ".join([
        row.get("id", ""),
        row.get("reporter_user_id", ""),
        row.get("target_type", ""),
        row.get("target_id", ""),
        row.get("reason", ""),
        row.get("detail", ""),
        row.get("status", ""),
        row.get("admin_memo", ""),
    ]).lower()
    return needle in haystack


def edit_request_matches(row, text):
    if not text:
        return True
    needle = text.lower()
    haystack = " ".join([
        row.get("id", ""),
        row.get("user_id", ""),
        row.get("recipe_version_id", ""),
        row.get("request_type", ""),
        row.get("content", ""),
        row.get("status", ""),
        row.get("admin_memo", ""),
    ]).lower()
    return needle in haystack


def member_matches(row, text, plan):
    if plan and row.get("subscription_plan", constants.SUBSCRIPTION_PLANS["FREE"]) != plan:
        return False
    if not text:
        return True
    needle = text.lower()
    haystack = " ".join([
        row.get("id", ""),
        row.get("email", ""),
        row.get("nickname", ""),
        row.get("role", ""),
        row.get("status", ""),
        row.get("subscription_plan", constants.SUBSCRIPTION_PLANS["FREE"]),
    ]).lower()
    return needle in haystack


def expert_matches(row, text, status):
    if status and row.get("status", constants.EXPERT_STATUSES["ACTIVE"]) != status:
        return False
    if not text:
        return True
    needle = text.lower()
    haystack = " ".join([
        row.get("id", ""),
        row.get("name", ""),
        row.get("email", ""),
        row.get("specialty", ""),
        row.get("status", ""),
    ]).lower()
    return needle in haystack


def filtered_comments(page, dump, status="", text="", reported_only=False):
    filters = {}
    if status:
        filters["status"] = status
    rows = struct.comment.comment_db.rows(page=1, dump=1000, orderby="created_at", order="DESC", **filters)
    rows = [row for row in rows if comment_matches(row, text, reported_only)]
    return paginate(rows, page, dump)


def filtered_reports(page, dump, status="", target_type="", text=""):
    filters = {}
    if status:
        filters["status"] = status
    if target_type:
        filters["target_type"] = target_type
    rows = struct.comment.report_db.rows(page=1, dump=1000, orderby="created_at", order="DESC", **filters)
    rows = [row for row in rows if report_matches(row, text)]
    return paginate(rows, page, dump)


def filtered_edit_requests(page, dump, status="", request_type="", text=""):
    filters = {}
    if status:
        filters["status"] = status
    if request_type:
        filters["request_type"] = request_type
    rows = struct.comment.edit_request_db.rows(page=1, dump=1000, orderby="created_at", order="DESC", **filters)
    rows = [row for row in rows if edit_request_matches(row, text)]
    return paginate(rows, page, dump)


def filtered_members(page, dump, plan="", text=""):
    rows = struct.db("user").rows(page=1, dump=1000, orderby="created_at", order="DESC")
    rows = [row for row in rows if member_matches(row, text, plan)]
    return paginate(rows, page, dump)


def filtered_experts(page, dump, status="", text=""):
    rows = struct.expert.expert_db.rows(page=1, dump=1000, orderby="created_at", order="DESC")
    rows = [row for row in rows if expert_matches(row, text, status)]
    return paginate(rows, page, dump)


def options():
    try:
        struct.require_admin()
        option_data = {
            "commentStatuses": option_items(constants.values("COMMENT_STATUSES"), COMMENT_STATUS_LABELS),
            "editRequestStatuses": option_items(constants.values("EDIT_REQUEST_STATUSES"), EDIT_STATUS_LABELS),
            "editRequestTypes": option_items(constants.values("EDIT_REQUEST_TYPES"), EDIT_TYPE_LABELS),
            "reportStatuses": option_items(constants.values("REPORT_STATUSES"), REPORT_STATUS_LABELS),
            "reportTargetTypes": option_items(constants.values("REPORT_TARGET_TYPES"), REPORT_TARGET_LABELS),
            "reportReasons": option_items(constants.values("REPORT_REASONS"), REPORT_REASON_LABELS),
            "userStatuses": option_items(constants.values("USER_STATUSES"), USER_STATUS_LABELS),
            "subscriptionPlans": option_items(constants.values("SUBSCRIPTION_PLANS"), SUBSCRIPTION_PLAN_LABELS),
            "expertStatuses": option_items(constants.values("EXPERT_STATUSES"), EXPERT_STATUS_LABELS),
            "expertAssignmentStatuses": option_items(constants.values("EXPERT_ASSIGNMENT_STATUSES"), EXPERT_ASSIGNMENT_STATUS_LABELS),
            "experts": [expert_dto(row) for row in struct.expert.active_options()],
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **option_data)


def comments():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    text = wiz.request.query("text", "")
    reported_only = to_bool(wiz.request.query("reportedOnly", "false"), False)
    try:
        struct.require_admin()
        rows, total = filtered_comments(page, dump, status=status, text=text, reported_only=reported_only)
        items = [comment_dto(row) for row in rows]
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))


def reports():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    target_type = wiz.request.query("targetType", wiz.request.query("target_type", ""))
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = filtered_reports(page, dump, status=status, target_type=target_type, text=text)
        items = [report_dto(row) for row in rows]
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))


def edit_requests():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    request_type = wiz.request.query("requestType", wiz.request.query("request_type", ""))
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = filtered_edit_requests(page, dump, status=status, request_type=request_type, text=text)
        assignments = struct.expert.assignment_map(
            constants.EXPERT_ASSIGNMENT_TARGET_TYPES["EDIT_REQUEST"],
            [row.get("id") for row in rows],
        )
        items = [edit_request_dto(row, assignments.get(row.get("id"))) for row in rows]
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))


def members():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    plan = wiz.request.query("plan", "")
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        if plan and not constants.has_value("SUBSCRIPTION_PLANS", plan):
            raise Exception("지원하지 않는 구독 플랜입니다.")
        rows, total = filtered_members(page, dump, plan=plan, text=text)
        items = [member_dto(row) for row in rows]
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))


def experts():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = filtered_experts(page, dump, status=status, text=text)
        items = [expert_dto(row) for row in rows]
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))


def comment_action():
    data = request_data()
    comment_id = data.get("id", "")
    action = data.get("action", "")
    reason = data.get("reason", "")
    try:
        struct.require_admin()
        before = struct.comment.comment_db.get(id=comment_id)
        if before is None:
            raise Exception("댓글을 찾을 수 없습니다.")
        if action == "hide":
            struct.comment.hide(comment_id, struct.session_user_id(), reason)
            action_type = "comment_hide"
        elif action == "delete":
            struct.comment.comment_db.update({
                "status": constants.COMMENT_STATUSES["DELETED"],
                "updated_at": struct.now(),
            }, id=comment_id)
            action_type = "comment_delete"
        elif action == "restore":
            struct.comment.comment_db.update({
                "status": constants.COMMENT_STATUSES["VISIBLE"],
                "updated_at": struct.now(),
            }, id=comment_id)
            action_type = "comment_restore"
        else:
            raise Exception("지원하지 않는 댓글 액션입니다.")
        after = struct.comment.comment_db.get(id=comment_id)
        struct.admin_log.create(action_type, "comment", comment_id, before, after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, comment=comment_dto(after), summary=summary_counts())


def edit_request_action():
    data = request_data()
    request_id = data.get("id", "")
    status = data.get("status", "")
    admin_memo = data.get("adminMemo", data.get("admin_memo", ""))
    try:
        struct.require_admin()
        before = struct.comment.edit_request_db.get(id=request_id) or {}
        if not before:
            raise Exception("수정 요청을 찾을 수 없습니다.")
        item = struct.comment.handle_edit_request(request_id, struct.session_user_id(), status, admin_memo)
        struct.admin_log.create("edit_request_status_update", "recipe_edit_request", request_id, before, item)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, editRequest=edit_request_dto(item), summary=summary_counts())


def report_action():
    data = request_data()
    report_id = data.get("id", "")
    status = data.get("status", "")
    admin_memo = data.get("adminMemo", data.get("admin_memo", ""))
    try:
        struct.require_admin()
        before = struct.comment.report_db.get(id=report_id) or {}
        if not before:
            raise Exception("신고를 찾을 수 없습니다.")
        item = struct.comment.resolve_report(report_id, struct.session_user_id(), status, admin_memo)
        struct.admin_log.create("report_status_update", "recipe_report", report_id, before, item)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, report=report_dto(item), summary=summary_counts())


def user_action():
    data = request_data()
    user_id = data.get("userId", data.get("user_id", ""))
    status = data.get("status", constants.USER_STATUSES["SUSPENDED"])
    try:
        struct.require_admin()
        if not constants.has_value("USER_STATUSES", status):
            raise Exception("지원하지 않는 사용자 상태입니다.")
        if user_id == struct.session_user_id():
            raise Exception("현재 관리자 계정은 이 화면에서 제재할 수 없습니다.")
        before = struct.user.get(user_id=user_id)
        if before is None:
            raise Exception("사용자를 찾을 수 없습니다.")
        struct.user.update(user_id, {"status": status})
        after = struct.user.get(user_id=user_id)
        struct.admin_log.create("user_status_update", "user", user_id, before, after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, user=user_dto(user_id), summary=summary_counts())


def subscription_action():
    data = request_data()
    user_id = data.get("userId", data.get("user_id", ""))
    plan = data.get("plan", constants.SUBSCRIPTION_PLANS["FREE"])
    expires_at = data.get("expiresAt", data.get("expires_at", ""))
    try:
        struct.require_admin()
        if user_id == struct.session_user_id():
            raise Exception("현재 관리자 계정의 구독 플랜은 이 화면에서 변경할 수 없습니다.")
        before = struct.user.get(user_id=user_id)
        if before is None:
            raise Exception("사용자를 찾을 수 없습니다.")
        user = struct.auth.upgrade_subscription(user_id, plan, expires_at)
        after = struct.user.get(user_id=user_id)
        struct.admin_log.create("user_subscription_update", "user", user_id, before, after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, user=user, member=user_dto(user_id), summary=summary_counts())


def expert_action():
    data = request_data()
    try:
        struct.require_admin()
        before = struct.expert.get(data.get("id", "")) if data.get("id") else None
        expert = struct.expert.save(data)
        action = "expert_update" if before else "expert_create"
        struct.admin_log.create(action, "expert", expert.get("id"), before, expert)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, expert=expert_dto(expert), options={
        "experts": [expert_dto(row) for row in struct.expert.active_options()]
    })


def assignment_action():
    data = request_data()
    target_type = data.get("targetType", data.get("target_type", constants.EXPERT_ASSIGNMENT_TARGET_TYPES["EDIT_REQUEST"]))
    target_id = data.get("targetId", data.get("target_id", ""))
    expert_id = data.get("expertId", data.get("expert_id", ""))
    status = data.get("status", constants.EXPERT_ASSIGNMENT_STATUSES["ASSIGNED"])
    review_note = data.get("reviewNote", data.get("review_note", ""))
    target = None
    try:
        struct.require_admin()
        before = struct.expert.assignment_for(target_type, target_id)
        assignment = struct.expert.assign(target_type, target_id, expert_id, status=status, review_note=review_note)
        struct.admin_log.create("expert_assignment_update", target_type, target_id, before, assignment)
        target = struct.comment.edit_request_db.get(id=target_id) if target_type == constants.EXPERT_ASSIGNMENT_TARGET_TYPES["EDIT_REQUEST"] else None
    except Exception as error:
        wiz.response.status(400, message=str(error))
    payload = {"assignment": assignment_dto(assignment), "summary": summary_counts()}
    if target:
        payload["editRequest"] = edit_request_dto(target, assignment)
    wiz.response.status(200, **payload)

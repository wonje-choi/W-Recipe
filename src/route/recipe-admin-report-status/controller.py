import datetime
import json

struct = wiz.model("portal/recipe/struct")


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


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


def report_dto(item):
    return {
        "id": item.get("id"),
        "reporterUserId": item.get("reporter_user_id", ""),
        "targetType": item.get("target_type", ""),
        "targetId": item.get("target_id", ""),
        "reason": item.get("reason", ""),
        "detail": item.get("detail", ""),
        "status": item.get("status", ""),
        "adminMemo": item.get("admin_memo", ""),
        "handledBy": item.get("handled_by", ""),
        "handledAt": date_text(item.get("handled_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


method = wiz.request.method()
segment = wiz.request.match("/api/admin/reports/<report_id>/status")
if segment is not None:
    if method in ["PUT", "POST"]:
        try:
            data = request_data()
            before = struct.comment.report_db.get(id=segment.report_id) or {}
            item = struct.comment.resolve_report(
                segment.report_id,
                struct.session_user_id(),
                data.get("status", ""),
                data.get("adminMemo", data.get("admin_memo", "")),
            )
            struct.admin_log.create(
                "report_status_update",
                "recipe_report",
                segment.report_id,
                before_value=before,
                after_value=item,
            )
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, report=report_dto(item))

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 신고 처리 API 경로입니다.")

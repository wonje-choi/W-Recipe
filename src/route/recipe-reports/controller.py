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
if method == "POST":
    try:
        data = request_data()
        target_type = data.get("targetType") or data.get("target_type") or ""
        target_id = data.get("targetId") or data.get("target_id") or ""
        report_id = struct.comment.create_report(
            struct.session_user_id(),
            target_type,
            target_id,
            data.get("reason", ""),
            data.get("detail", ""),
        )
        item = struct.comment.report_db.get(id=report_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, report=report_dto(item))

wiz.response.status(405, message="Method not allowed")

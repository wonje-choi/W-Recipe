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


def edit_request_dto(item):
    return {
        "id": item.get("id"),
        "userId": item.get("user_id", ""),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestType": item.get("request_type", ""),
        "content": item.get("content", ""),
        "attachmentUrl": item.get("attachment_url", ""),
        "status": item.get("status", ""),
        "adminMemo": item.get("admin_memo", ""),
        "handledBy": item.get("handled_by", ""),
        "handledAt": date_text(item.get("handled_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


method = wiz.request.method()
segment = wiz.request.match("/api/recipes/<version_id>/edit-requests")
if segment is not None:
    if method == "POST":
        try:
            data = request_data()
            request_type = data.get("requestType") or data.get("request_type") or ""
            attachment_url = data.get("attachmentUrl") or data.get("attachment_url") or ""
            request_id = struct.comment.request_edit(
                struct.session_user_id(),
                segment.version_id,
                request_type,
                data.get("content", ""),
                attachment_url,
            )
            item = struct.comment.edit_request_db.get(id=request_id)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(201, editRequest=edit_request_dto(item))

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 수정 요청 API 경로입니다.")

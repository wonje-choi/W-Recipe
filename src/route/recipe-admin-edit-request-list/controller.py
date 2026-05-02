import datetime

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


def to_int(value, default):
    try:
        return int(value)
    except Exception:
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
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    user_id = wiz.request.query("userId", wiz.request.query("user_id", ""))
    try:
        rows, total = struct.comment.edit_requests(status=status, user_id=user_id, page=page, dump=dump)
        items = [edit_request_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))

wiz.response.status(405, message="Method not allowed")

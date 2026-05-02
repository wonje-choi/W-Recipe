import datetime
import json

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


def version_dto(version):
    if not version:
        return None
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "summary": version.get("summary", ""),
        "sourceType": version.get("source_type", ""),
        "status": version.get("status", ""),
        "aiModified": bool(version.get("ai_modified")),
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }


def recent_dto(row):
    version = struct.recipe.get_version(row.get("recipe_version_id", ""), public=True)
    return {
        "id": row.get("id"),
        "recipeVersionId": row.get("recipe_version_id", ""),
        "viewCount": int(row.get("view_count") or 0),
        "viewedAt": date_text(row.get("viewed_at")),
        "createdAt": date_text(row.get("created_at")),
        "updatedAt": date_text(row.get("updated_at")),
        "version": version_dto(version),
    }


method = wiz.request.method()
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    try:
        rows, total = struct.comment.recent_views(struct.session_user_id(), page=page, dump=dump)
        items = [recent_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))

if method == "POST":
    try:
        data = request_data()
        version_id = data.get("recipeVersionId") or data.get("recipe_version_id") or ""
        if not version_id:
            raise Exception("레시피 버전을 선택해주세요.")
        item = struct.comment.record_recent_view(struct.session_user_id(), version_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, item=recent_dto(item))

wiz.response.status(405, message="Method not allowed")

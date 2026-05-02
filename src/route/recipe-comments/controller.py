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


def comment_dto(comment):
    return {
        "id": comment.get("id"),
        "recipeVersionId": comment.get("recipe_version_id", ""),
        "userId": comment.get("user_id", ""),
        "content": comment.get("content", ""),
        "status": comment.get("status", ""),
        "reportCount": int(comment.get("report_count") or 0),
        "createdAt": date_text(comment.get("created_at")),
        "updatedAt": date_text(comment.get("updated_at")),
    }


method = wiz.request.method()
segment = wiz.request.match("/api/recipes/<version_id>/comments")
if segment is not None:
    if method == "GET":
        page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
        dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
        try:
            rows, total = struct.comment.rows(segment.version_id, page=page, dump=dump, visible_only=True)
            comments = [comment_dto(row) for row in rows]
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, comments=comments, page=page, dump=dump, total=total, empty=(total == 0))

    if method == "POST":
        try:
            user = struct.auth.require_login()
            data = request_data()
            comment_id = struct.comment.create(user.get("id"), segment.version_id, data.get("content", ""))
            comment = struct.comment.comment_db.get(id=comment_id)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(201, comment=comment_dto(comment))

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 댓글 API 경로입니다.")

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


def comment_dto(item):
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "content": item.get("content", ""),
        "status": item.get("status", ""),
        "reportCount": int(item.get("report_count") or 0),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def edit_request_dto(item):
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestType": item.get("request_type", ""),
        "content": item.get("content", ""),
        "attachmentUrl": item.get("attachment_url", ""),
        "status": item.get("status", ""),
        "adminMemo": item.get("admin_memo", ""),
        "handledAt": date_text(item.get("handled_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def favorite_dto(item):
    version = struct.recipe.get_version(item.get("recipe_version_id", ""), public=True)
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "createdAt": date_text(item.get("created_at")),
        "version": version_dto(version),
    }


def recent_dto(item):
    version = struct.recipe.get_version(item.get("recipe_version_id", ""), public=True)
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "viewCount": int(item.get("view_count") or 0),
        "viewedAt": date_text(item.get("viewed_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
        "version": version_dto(version),
    }


def ai_modification_dto(item):
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "purpose": item.get("purpose", ""),
        "targetUserType": item.get("target_user_type", ""),
        "status": item.get("status", ""),
        "riskFlags": struct.json_loads(item.get("risk_flags", "[]"), default=[]),
        "reviewedAt": date_text(item.get("reviewed_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


method = wiz.request.method()
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", 10))
    user_id = struct.session_user_id()
    try:
        comment_rows = struct.comment.comment_db.rows(user_id=user_id, page=page, dump=dump, orderby="created_at", order="DESC")
        comment_total = struct.comment.comment_db.count(user_id=user_id) or 0
        edit_rows, edit_total = struct.comment.edit_requests(user_id=user_id, page=page, dump=dump)
        favorite_rows, favorite_total = struct.comment.favorites(user_id=user_id, page=page, dump=dump)
        recent_rows, recent_total = struct.comment.recent_views(user_id=user_id, page=page, dump=dump)
        ai_db = struct.db("ai_recipe_modification")
        ai_rows = ai_db.rows(requested_by=user_id, page=page, dump=dump, orderby="created_at", order="DESC")
        ai_total = ai_db.count(requested_by=user_id) or 0
        activity = {
            "comments": {"items": [comment_dto(row) for row in comment_rows], "total": comment_total},
            "editRequests": {"items": [edit_request_dto(row) for row in edit_rows], "total": edit_total},
            "aiModifications": {"items": [ai_modification_dto(row) for row in ai_rows], "total": ai_total},
            "favorites": {"items": [favorite_dto(row) for row in favorite_rows], "total": favorite_total},
            "recentViews": {"items": [recent_dto(row) for row in recent_rows], "total": recent_total},
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, page=page, dump=dump, activity=activity)

wiz.response.status(405, message="Method not allowed")

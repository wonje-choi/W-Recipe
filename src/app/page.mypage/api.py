import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def parse_data():
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


def profile_dto(user):
    profile = struct.user.safe_profile(user) or {}
    profile["lastLoginAt"] = date_text(profile.get("lastLoginAt"))
    profile["createdAt"] = date_text(profile.get("createdAt"))
    profile["updatedAt"] = date_text(profile.get("updatedAt"))
    return profile


def preference_dto(preference):
    payload = struct.user.preference_payload(preference)
    payload["createdAt"] = date_text(payload.get("createdAt"))
    payload["updatedAt"] = date_text(payload.get("updatedAt"))
    return payload


def version_dto(version):
    if not version:
        return None
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "summary": version.get("summary", ""),
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
        "createdAt": date_text(item.get("created_at")),
    }


def edit_request_dto(item):
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestType": item.get("request_type", ""),
        "content": item.get("content", ""),
        "status": item.get("status", ""),
        "adminMemo": item.get("admin_memo", ""),
        "createdAt": date_text(item.get("created_at")),
        "handledAt": date_text(item.get("handled_at")),
    }


def ai_modification_dto(item):
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "purpose": item.get("purpose", ""),
        "targetUserType": item.get("target_user_type", ""),
        "status": item.get("status", ""),
        "riskFlags": struct.json_loads(item.get("risk_flags", "[]"), default=[]),
        "createdAt": date_text(item.get("created_at")),
        "reviewedAt": date_text(item.get("reviewed_at")),
    }


def favorite_dto(item):
    try:
        version = struct.recipe.get_version(item.get("recipe_version_id", ""), public=True)
    except Exception:
        version = None
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "createdAt": date_text(item.get("created_at")),
        "version": version_dto(version),
    }


def recent_dto(item):
    try:
        version = struct.recipe.get_version(item.get("recipe_version_id", ""), public=True)
    except Exception:
        version = None
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "viewCount": int(item.get("view_count") or 0),
        "viewedAt": date_text(item.get("viewed_at")),
        "version": version_dto(version),
    }


def activity_payload(user_id):
    dump = 8
    comment_rows = struct.comment.comment_db.rows(user_id=user_id, page=1, dump=dump, orderby="created_at", order="DESC")
    comment_total = struct.comment.comment_db.count(user_id=user_id) or 0
    edit_rows, edit_total = struct.comment.edit_requests(user_id=user_id, page=1, dump=dump)
    favorite_rows, favorite_total = struct.comment.favorites(user_id=user_id, page=1, dump=dump)
    recent_rows, recent_total = struct.comment.recent_views(user_id=user_id, page=1, dump=dump)
    ai_db = struct.db("ai_recipe_modification")
    ai_rows = ai_db.rows(requested_by=user_id, page=1, dump=dump, orderby="created_at", order="DESC")
    ai_total = ai_db.count(requested_by=user_id) or 0
    return {
        "comments": {"items": [comment_dto(row) for row in comment_rows], "total": comment_total},
        "editRequests": {"items": [edit_request_dto(row) for row in edit_rows], "total": edit_total},
        "aiModifications": {"items": [ai_modification_dto(row) for row in ai_rows], "total": ai_total},
        "favorites": {"items": [favorite_dto(row) for row in favorite_rows], "total": favorite_total},
        "recentViews": {"items": [recent_dto(row) for row in recent_rows], "total": recent_total},
    }


def empty_activity():
    return {
        "comments": {"items": [], "total": 0},
        "editRequests": {"items": [], "total": 0},
        "aiModifications": {"items": [], "total": 0},
        "favorites": {"items": [], "total": 0},
        "recentViews": {"items": [], "total": 0},
    }


def option_payload():
    return {
        "dietTypes": ["저염", "이유식", "다이어트", "고단백", "채식", "저당"],
        "tools": ["전자레인지", "에어프라이어", "오븐", "압력솥", "믹서", "찜기"],
        "sodiumPreferences": [
            {"label": "보통", "value": "normal"},
            {"label": "저염", "value": "low"},
            {"label": "가능한 더 낮게", "value": "very_low"},
        ],
        "texturePreferences": [
            {"label": "보통", "value": "normal"},
            {"label": "부드럽게", "value": "soft"},
            {"label": "씹는 식감", "value": "chewy"},
            {"label": "곱게 갈기", "value": "smooth"},
        ],
    }


def load():
    user_id = struct.session_user_id()
    try:
        if not user_id:
            raise Exception("로그인이 필요합니다.")
        user = struct.user.get(user_id=user_id)
        if not user:
            raise Exception("사용자를 찾을 수 없습니다.")
        preference = struct.user.preference(user_id) or {}
        activity = activity_payload(user_id) or empty_activity()
    except Exception as error:
        return wiz.response.status(400, message=str(error))
    return wiz.response.status(
        200,
        profile=profile_dto(user),
        preference=preference_dto(preference),
        activity=activity,
        options=option_payload(),
    )


def save_profile():
    user_id = struct.session_user_id()
    data = parse_data()
    try:
        user = struct.user.update_profile(user_id, data)
        if data.get("nickname"):
            struct.session.set(nickname=data.get("nickname"))
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, profile=profile_dto(user))


def save_preference():
    user_id = struct.session_user_id()
    data = parse_data()
    try:
        preference_id = struct.user.save_preference(user_id, data)
        preference = struct.user.preference_db.get(id=preference_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, preference=preference_dto(preference))

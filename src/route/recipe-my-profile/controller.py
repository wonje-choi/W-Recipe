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


def profile_dto(user):
    profile = struct.user.safe_profile(user) or {}
    return {
        "id": profile.get("id", ""),
        "email": profile.get("email", ""),
        "nickname": profile.get("nickname", ""),
        "role": profile.get("role", ""),
        "status": profile.get("status", ""),
        "lastLoginAt": date_text(profile.get("lastLoginAt")),
        "createdAt": date_text(profile.get("createdAt")),
        "updatedAt": date_text(profile.get("updatedAt")),
    }


method = wiz.request.method()
user_id = struct.session_user_id()

if method == "GET":
    try:
        user = struct.user.get(user_id=user_id)
        if not user:
            raise Exception("사용자를 찾을 수 없습니다.")
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, profile=profile_dto(user))

if method in ["PUT", "POST"]:
    try:
        data = request_data()
        user = struct.user.update_profile(user_id, data)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, profile=profile_dto(user))

wiz.response.status(405, message="Method not allowed")

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


def preference_dto(preference):
    payload = struct.user.preference_payload(preference)
    payload["createdAt"] = date_text(payload.get("createdAt"))
    payload["updatedAt"] = date_text(payload.get("updatedAt"))
    return payload


method = wiz.request.method()
user_id = struct.session_user_id()

if method == "GET":
    try:
        preference = struct.user.preference(user_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, preference=preference_dto(preference))

if method in ["PUT", "POST"]:
    try:
        data = request_data()
        preference_id = struct.user.save_preference(user_id, data)
        preference = struct.user.preference_db.get(id=preference_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, preference=preference_dto(preference))

wiz.response.status(405, message="Method not allowed")

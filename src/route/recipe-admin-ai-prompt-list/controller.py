import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default

def to_bool(value, default=None):
    if isinstance(value, bool):
        return value
    if value in ["true", "True", "1", 1]:
        return True
    if value in ["false", "False", "0", 0]:
        return False
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

def prompt_dto(prompt):
    return {
        "id": prompt.get("id"),
        "promptKey": prompt.get("prompt_key", ""),
        "version": prompt.get("version", ""),
        "promptVersion": prompt.get("prompt_version", ""),
        "title": prompt.get("title", ""),
        "description": prompt.get("description", ""),
        "template": prompt.get("template", ""),
        "inputSchema": struct.json_loads(prompt.get("input_schema"), {}),
        "outputSchema": struct.json_loads(prompt.get("output_schema"), {}),
        "modelHint": prompt.get("model_hint", ""),
        "isActive": bool(prompt.get("is_active")),
        "changeReason": prompt.get("change_reason", ""),
        "createdBy": prompt.get("created_by", ""),
        "updatedBy": prompt.get("updated_by", ""),
        "deactivatedAt": date_text(prompt.get("deactivated_at")),
        "createdAt": date_text(prompt.get("created_at")),
        "updatedAt": date_text(prompt.get("updated_at")),
    }

def prompt_payload(data):
    payload = {}
    mapping = {
        "promptKey": "prompt_key",
        "prompt_key": "prompt_key",
        "version": "version",
        "title": "title",
        "description": "description",
        "template": "template",
        "inputSchema": "input_schema",
        "input_schema": "input_schema",
        "outputSchema": "output_schema",
        "output_schema": "output_schema",
        "modelHint": "model_hint",
        "model_hint": "model_hint",
        "changeReason": "change_reason",
        "change_reason": "change_reason",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key)
    if "isActive" in data:
        payload["is_active"] = to_bool(data.get("isActive"), False)
    if "is_active" in data:
        payload["is_active"] = to_bool(data.get("is_active"), False)
    return payload

method = wiz.request.method()
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    prompt_key = wiz.request.query("promptKey", wiz.request.query("prompt_key", ""))
    active_value = wiz.request.query("isActive", wiz.request.query("is_active", ""))
    is_active = to_bool(active_value, None)
    try:
        rows, total = struct.ai.prompt_rows(prompt_key=prompt_key, is_active=is_active, page=page, dump=dump)
        items = [prompt_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, promptTypes=constants.AI_PROMPT_TYPES, page=page, dump=dump, total=total, empty=(total == 0))

if method == "POST":
    try:
        data = request_data()
        payload = prompt_payload(data)
        prompt_id = struct.ai.create_prompt(payload, admin_user_id=struct.session_user_id())
        prompt = struct.ai.get_prompt(prompt_id)
        struct.admin_log.create("ai_prompt_create", "ai_prompt_template", prompt_id, {}, prompt)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, prompt=prompt_dto(prompt))

wiz.response.status(405, message="Method not allowed")

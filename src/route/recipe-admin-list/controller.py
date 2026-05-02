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

def json_text(value, default):
    if value is None or value == "":
        return struct.json_dumps(default)
    if isinstance(value, (list, dict)):
        return struct.json_dumps(value)
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") or text.startswith("{"):
            try:
                json.loads(text)
                return text
            except Exception:
                return struct.json_dumps(default)
        if isinstance(default, list):
            return struct.json_dumps([item.strip() for item in text.split(",") if item.strip()])
    return struct.json_dumps(default)

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

def dish_payload(data):
    payload = {}
    for key in ["name", "description", "category", "status"]:
        if key in data:
            payload[key] = data.get(key)
    if "thumbnailUrl" in data:
        payload["thumbnail_url"] = data.get("thumbnailUrl", "")
    if "thumbnail_url" in data:
        payload["thumbnail_url"] = data.get("thumbnail_url", "")
    if "tags" in data:
        payload["tags"] = json_text(data.get("tags"), [])
    if "viewCount" in data:
        payload["view_count"] = to_int(data.get("viewCount"), 0)
    return payload

def dish_dto(dish):
    thumbnail_url = dish.get("thumbnail_url", "")
    return {
        "id": dish.get("id"),
        "name": dish.get("name", ""),
        "description": dish.get("description", ""),
        "category": dish.get("category", ""),
        "tags": struct.json_loads(dish.get("tags"), []),
        "thumbnailUrl": thumbnail_url,
        "hasImage": bool(thumbnail_url),
        "viewCount": int(dish.get("view_count") or 0),
        "status": dish.get("status", ""),
        "createdAt": date_text(dish.get("created_at")),
        "updatedAt": date_text(dish.get("updated_at")),
    }

method = wiz.request.method()
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    text = wiz.request.query("text", "")
    category = wiz.request.query("category", "")
    tag = wiz.request.query("tag", "")
    status = wiz.request.query("status", "")
    sort = wiz.request.query("sort", constants.RECIPE_SORTS["LATEST"])
    try:
        rows, total = struct.recipe.admin_search_dishes(
            text=text,
            category=category,
            tag=tag,
            status=status,
            page=page,
            dump=dump,
            sort=sort,
        )
        items = [dish_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))

if method == "POST":
    try:
        data = request_data()
        payload = dish_payload(data)
        if not payload.get("name"):
            raise Exception("레시피 이름을 입력해주세요.")
        dish_id = struct.recipe.create_dish(payload)
        dish = struct.recipe.get_dish(dish_id)
        struct.admin_log.create("recipe_dish_create", "recipe_dish", dish_id, {}, dish)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, dish=dish_dto(dish))

wiz.response.status(405, message="Method not allowed")

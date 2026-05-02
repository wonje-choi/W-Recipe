import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default

def to_bool(value, default=False):
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

def parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    for pattern in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(str(value), pattern)
        except Exception:
            pass
    try:
        return datetime.datetime.fromisoformat(str(value))
    except Exception:
        return None

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

def version_payload(data, for_create=False):
    payload = {}
    mapping = {
        "title": "title",
        "sourceType": "source_type",
        "source_type": "source_type",
        "sourceUrl": "source_url",
        "source_url": "source_url",
        "sourceTitle": "source_title",
        "source_title": "source_title",
        "sourceAuthor": "source_author",
        "source_author": "source_author",
        "summary": "summary",
        "difficulty": "difficulty",
        "servingSize": "serving_size",
        "serving_size": "serving_size",
        "status": "status",
        "reviewedBy": "reviewed_by",
        "reviewed_by": "reviewed_by",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key)
    if "sourceCollectedAt" in data:
        payload["source_collected_at"] = parse_datetime(data.get("sourceCollectedAt"))
    if "source_collected_at" in data:
        payload["source_collected_at"] = parse_datetime(data.get("source_collected_at"))
    if "reviewedAt" in data:
        payload["reviewed_at"] = parse_datetime(data.get("reviewedAt"))
    if "reviewed_at" in data:
        payload["reviewed_at"] = parse_datetime(data.get("reviewed_at"))
    if "ingredients" in data:
        payload["ingredients"] = json_text(data.get("ingredients"), [])
    if "steps" in data:
        payload["steps"] = json_text(data.get("steps"), [])
    if "cookingTips" in data:
        payload["cooking_tips"] = json_text(data.get("cookingTips"), [])
    if "failurePreventionTips" in data:
        payload["failure_prevention_tips"] = json_text(data.get("failurePreventionTips"), [])
    if "substitutionTips" in data:
        payload["substitution_tips"] = json_text(data.get("substitutionTips"), [])
    if "nutritionInfo" in data:
        payload["nutrition_info"] = json_text(data.get("nutritionInfo"), {})
    if "sodiumInfo" in data:
        payload["sodium_info"] = json_text(data.get("sodiumInfo"), {})
    if "allergenInfo" in data:
        payload["allergen_info"] = json_text(data.get("allergenInfo"), [])
    if "cookingTime" in data:
        payload["cooking_time"] = to_int(data.get("cookingTime"), 0)
    if "viewCount" in data:
        payload["view_count"] = to_int(data.get("viewCount"), 0)
    if "aiModified" in data:
        payload["ai_modified"] = to_bool(data.get("aiModified"), False)
    if for_create:
        payload.setdefault("source_type", constants.SOURCE_TYPES["DIRECT"])
        payload.setdefault("status", constants.RECIPE_STATUSES["DRAFT"])
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

def version_dto(version):
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "sourceType": version.get("source_type", ""),
        "sourceUrl": version.get("source_url", ""),
        "sourceTitle": version.get("source_title", ""),
        "sourceAuthor": version.get("source_author", ""),
        "sourceCollectedAt": date_text(version.get("source_collected_at")),
        "summary": version.get("summary", ""),
        "ingredients": struct.json_loads(version.get("ingredients"), []),
        "steps": struct.json_loads(version.get("steps"), []),
        "cookingTips": struct.json_loads(version.get("cooking_tips"), []),
        "failurePreventionTips": struct.json_loads(version.get("failure_prevention_tips"), []),
        "substitutionTips": struct.json_loads(version.get("substitution_tips"), []),
        "nutritionInfo": struct.json_loads(version.get("nutrition_info"), {}),
        "sodiumInfo": struct.json_loads(version.get("sodium_info"), {}),
        "allergenInfo": struct.json_loads(version.get("allergen_info"), []),
        "difficulty": version.get("difficulty", ""),
        "cookingTime": int(version.get("cooking_time") or 0),
        "servingSize": version.get("serving_size", ""),
        "viewCount": int(version.get("view_count") or 0),
        "aiModified": bool(version.get("ai_modified")),
        "status": version.get("status", ""),
        "reviewedBy": version.get("reviewed_by", ""),
        "reviewedAt": date_text(version.get("reviewed_at")),
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }

def fetch_dish(dish_id):
    dish = struct.recipe.get_dish(dish_id, public=False)
    if dish is None:
        wiz.response.status(404, message="레시피를 찾을 수 없습니다.")
    return dish

def fetch_version(dish_id, version_id):
    version = struct.recipe.get_version(version_id, public=False)
    if version is None or version.get("dish_id") != dish_id:
        wiz.response.status(404, message="레시피 버전을 찾을 수 없습니다.")
    return version

def admin_recipe_list():
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

def admin_recipe_create():
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

method = wiz.request.method()
request_path = wiz.request.uri().split("?", 1)[0].rstrip("/")
if request_path == "/api/admin/recipes":
    if method == "GET":
        admin_recipe_list()
    if method == "POST":
        admin_recipe_create()
    wiz.response.status(405, message="Method not allowed")

segment = wiz.request.match("/api/admin/recipes/<dish_id>/versions/<version_id>")
if segment is not None:
    dish = fetch_dish(segment.dish_id)
    version = fetch_version(segment.dish_id, segment.version_id)

    if method == "GET":
        wiz.response.status(200, dish=dish_dto(dish), version=version_dto(version))

    if method == "PUT":
        try:
            data = request_data()
            payload = version_payload(data)
            struct.recipe.update_version(segment.version_id, payload)
            updated = struct.recipe.get_version(segment.version_id, public=False)
            struct.admin_log.create("recipe_version_update", "recipe_version", segment.version_id, version, updated)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, version=version_dto(updated))

    if method == "DELETE":
        try:
            struct.recipe.update_version(segment.version_id, {"status": constants.RECIPE_STATUSES["HIDDEN"]})
            updated = struct.recipe.get_version(segment.version_id, public=False)
            struct.admin_log.create("recipe_version_hide", "recipe_version", segment.version_id, version, updated)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, version=version_dto(updated))

    wiz.response.status(405, message="Method not allowed")

segment = wiz.request.match("/api/admin/recipes/<dish_id>/versions")
if segment is not None:
    dish = fetch_dish(segment.dish_id)

    if method == "GET":
        page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
        dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
        try:
            rows, total = struct.recipe.admin_versions(segment.dish_id, page=page, dump=dump)
            versions = [version_dto(row) for row in rows]
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, dish=dish_dto(dish), versions=versions, page=page, dump=dump, total=total, empty=(total == 0))

    if method == "POST":
        try:
            data = request_data()
            payload = version_payload(data, for_create=True)
            if not payload.get("title"):
                raise Exception("버전 제목을 입력해주세요.")
            version_id = struct.recipe.create_version(segment.dish_id, payload)
            version = struct.recipe.get_version(version_id, public=False)
            struct.admin_log.create("recipe_version_create", "recipe_version", version_id, {}, version)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(201, version=version_dto(version))

    wiz.response.status(405, message="Method not allowed")

segment = wiz.request.match("/api/admin/recipes/<dish_id>")
if segment is not None:
    dish = fetch_dish(segment.dish_id)

    if method == "GET":
        wiz.response.status(200, dish=dish_dto(dish))

    if method == "PUT":
        try:
            data = request_data()
            payload = dish_payload(data)
            struct.recipe.update_dish(segment.dish_id, payload)
            updated = struct.recipe.get_dish(segment.dish_id, public=False)
            struct.admin_log.create("recipe_dish_update", "recipe_dish", segment.dish_id, dish, updated)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, dish=dish_dto(updated))

    if method == "DELETE":
        try:
            struct.recipe.update_dish(segment.dish_id, {"status": constants.RECIPE_STATUSES["HIDDEN"]})
            updated = struct.recipe.get_dish(segment.dish_id, public=False)
            struct.admin_log.create("recipe_dish_hide", "recipe_dish", segment.dish_id, dish, updated)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, dish=dish_dto(updated))

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 관리자 레시피 API 경로입니다.")

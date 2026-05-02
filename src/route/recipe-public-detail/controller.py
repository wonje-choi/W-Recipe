import datetime

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")
session = wiz.model("portal/season/session").use()

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
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }

def source_dto(version):
    source_url = version.get("source_url", "")
    return {
        "available": bool(source_url),
        "sourceType": version.get("source_type", ""),
        "sourceUrl": source_url,
        "sourceTitle": version.get("source_title", ""),
        "sourceAuthor": version.get("source_author", ""),
        "sourceCollectedAt": date_text(version.get("source_collected_at")),
        "message": "" if source_url else "등록된 원본 출처 링크가 없습니다.",
    }

def fetch_public_dish(dish_id):
    dish = struct.recipe.get_dish(dish_id, public=True)
    if dish is None:
        wiz.response.status(404, message="레시피를 찾을 수 없습니다.")
    return dish

def fetch_public_version(dish_id, version_id):
    version = struct.recipe.get_version(version_id, public=True)
    if version is None or version.get("dish_id") != dish_id:
        wiz.response.status(404, message="레시피 버전을 찾을 수 없습니다.")
    return version

def mark_view_once(target_type, target_id):
    today = datetime.datetime.now().strftime("%Y%m%d")
    key = f"recipe_view_{target_type}_{target_id}_{today}"
    if session.has(key):
        return False
    session.set(**{key: True})
    return True

def find_base_version(dish_id, target_version_id):
    rows, total = struct.recipe.versions(dish_id, public=True, page=1, dump=20)
    for version in rows:
        if version.get("id") != target_version_id and not version.get("ai_modified"):
            return version
    for version in rows:
        if version.get("id") != target_version_id:
            return version
    return None

def compare_versions(base_version, target_version):
    base = version_dto(base_version)
    target = version_dto(target_version)
    return {
        "baseVersion": base,
        "targetVersion": target,
        "comparison": {
            "ingredientsChanged": base["ingredients"] != target["ingredients"],
            "stepsChanged": base["steps"] != target["steps"],
            "nutritionChanged": base["nutritionInfo"] != target["nutritionInfo"],
            "sodiumChanged": base["sodiumInfo"] != target["sodiumInfo"],
            "targetAiModified": target["aiModified"],
            "sourceTypeChanged": base["sourceType"] != target["sourceType"],
        },
    }

def public_recipe_list():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    text = wiz.request.query("text", "")
    category = wiz.request.query("category", "")
    tag = wiz.request.query("tag", "")
    sort = wiz.request.query("sort", constants.RECIPE_SORTS["LATEST"])
    try:
        rows, total = struct.recipe.search_dishes(
            text=text,
            category=category,
            tag=tag,
            page=page,
            dump=dump,
            sort=sort,
        )
        items = [dish_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    message = "" if total else "승인된 레시피가 없습니다."
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0), message=message)

method = wiz.request.method()
if method not in ["GET", "POST"]:
    wiz.response.status(405, message="Method not allowed")

request_path = wiz.request.uri().split("?", 1)[0].rstrip("/")
if method == "GET" and request_path == "/api/recipes":
    public_recipe_list()

if method == "POST":
    segment = wiz.request.match("/api/recipes/<dish_id>/versions/<version_id>/views")
    if segment is not None:
        fetch_public_dish(segment.dish_id)
        version = fetch_public_version(segment.dish_id, segment.version_id)
        counted = mark_view_once("version", segment.version_id)
        if counted:
            view_count = struct.recipe.increment_version_view(segment.version_id)
        else:
            view_count = int(version.get("view_count") or 0)
        wiz.response.status(200, counted=counted, viewCount=view_count)

    segment = wiz.request.match("/api/recipes/<dish_id>/views")
    if segment is not None:
        dish = fetch_public_dish(segment.dish_id)
        counted = mark_view_once("dish", segment.dish_id)
        if counted:
            view_count = struct.recipe.increment_dish_view(segment.dish_id)
        else:
            view_count = int(dish.get("view_count") or 0)
        wiz.response.status(200, counted=counted, viewCount=view_count)

    wiz.response.status(404, message="지원하지 않는 조회수 API 경로입니다.")

segment = wiz.request.match("/api/recipes/<dish_id>/versions/<version_id>/source")
if segment is not None:
    fetch_public_dish(segment.dish_id)
    version = fetch_public_version(segment.dish_id, segment.version_id)
    wiz.response.status(200, source=source_dto(version))

segment = wiz.request.match("/api/recipes/<dish_id>/versions/<version_id>/compare")
if segment is not None:
    fetch_public_dish(segment.dish_id)
    target_version = fetch_public_version(segment.dish_id, segment.version_id)
    base_version_id = wiz.request.query("baseVersionId", "")
    if base_version_id:
        base_version = fetch_public_version(segment.dish_id, base_version_id)
    else:
        base_version = find_base_version(segment.dish_id, segment.version_id)
    if base_version is None:
        wiz.response.status(404, message="비교할 기준 버전을 찾을 수 없습니다.")
    data = compare_versions(base_version, target_version)
    wiz.response.status(200, **data)

segment = wiz.request.match("/api/recipes/<dish_id>/versions/<version_id>")
if segment is not None:
    dish = fetch_public_dish(segment.dish_id)
    version = fetch_public_version(segment.dish_id, segment.version_id)
    wiz.response.status(200, dish=dish_dto(dish), version=version_dto(version), source=source_dto(version))

segment = wiz.request.match("/api/recipes/<dish_id>/versions")
if segment is not None:
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    dish = fetch_public_dish(segment.dish_id)
    try:
        rows, total = struct.recipe.versions(segment.dish_id, public=True, page=page, dump=dump)
        versions = [version_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    message = "" if total else "승인된 레시피 버전이 없습니다."
    wiz.response.status(200, dish=dish_dto(dish), versions=versions, page=page, dump=dump, total=total, empty=(total == 0), message=message)

segment = wiz.request.match("/api/recipes/<dish_id>")
if segment is not None:
    dish = fetch_public_dish(segment.dish_id)
    try:
        rows, total = struct.recipe.versions(segment.dish_id, public=True, page=1, dump=1)
        representative = version_dto(rows[0]) if rows else None
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, dish=dish_dto(dish), representativeVersion=representative, versionCount=total, hasVersion=(total > 0))

wiz.response.status(404, message="지원하지 않는 레시피 API 경로입니다.")

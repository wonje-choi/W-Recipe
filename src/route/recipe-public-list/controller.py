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

if wiz.request.method() != "GET":
    wiz.response.status(405, message="Method not allowed")

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

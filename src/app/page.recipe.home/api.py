import datetime
import random


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def dish_dto(struct, dish):
    dish = dish or {}
    thumbnail_url = dish.get("thumbnail_url", "")
    return {
        "id": dish.get("id"),
        "name": dish.get("name", ""),
        "description": dish.get("description", ""),
        "category": dish.get("category", ""),
        "tags": struct.json_loads(dish.get("tags", "[]"), default=[]),
        "thumbnailUrl": thumbnail_url,
        "hasImage": bool(thumbnail_url),
        "viewCount": int(dish.get("view_count") or 0),
        "status": dish.get("status", ""),
        "createdAt": date_text(dish.get("created_at")),
        "updatedAt": date_text(dish.get("updated_at")),
    }


def empty_payload():
    return {
        "recommended": [],
        "popular": [],
        "randomItems": [],
        "latest": [],
        "totals": {
            "popular": 0,
            "latest": 0,
            "pool": 0,
        },
        "keywords": ["저염", "이유식", "간단요리", "고단백", "부드러운 식감"],
    }


def safe_dishes(struct, rows):
    items = []
    for row in rows or []:
        try:
            items.append(dish_dto(struct, row))
        except Exception:
            pass
    return items


def load():
    payload = empty_payload()
    try:
        struct = wiz.model("portal/recipe/struct")
        constants = wiz.model("portal/recipe/constants")
        user_id = struct.session.get("id", "")
        popular_rows, popular_total = struct.recipe.search_dishes(page=1, dump=3, sort=constants.RECIPE_SORTS["VIEW_COUNT"])
        latest_rows, latest_total = struct.recipe.search_dishes(page=1, dump=6, sort=constants.RECIPE_SORTS["LATEST"])
        pool_rows, pool_total = struct.recipe.search_dishes(page=1, dump=20, sort=constants.RECIPE_SORTS["LATEST"])
        pool = list(pool_rows or [])
        if len(pool) > 2:
            random_rows = random.sample(pool, 2)
        else:
            random_rows = pool
        payload["popular"] = safe_dishes(struct, popular_rows)
        payload["latest"] = safe_dishes(struct, latest_rows)
        payload["randomItems"] = safe_dishes(struct, random_rows)
        payload["totals"] = {
            "popular": popular_total,
            "latest": latest_total,
            "pool": pool_total,
        }
        if user_id:
            try:
                payload["recommended"] = safe_dishes(struct, struct.recipe.get_recommended(user_id, limit=6))
            except Exception:
                payload["recommended"] = []
    except Exception as error:
        payload["message"] = str(error)

    return wiz.response.status(200, **payload)

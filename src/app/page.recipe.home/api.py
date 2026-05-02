import datetime
import random

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


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
        "tags": struct.json_loads(dish.get("tags", "[]"), default=[]),
        "thumbnailUrl": thumbnail_url,
        "hasImage": bool(thumbnail_url),
        "viewCount": int(dish.get("view_count") or 0),
        "status": dish.get("status", ""),
        "createdAt": date_text(dish.get("created_at")),
        "updatedAt": date_text(dish.get("updated_at")),
    }


def load():
    try:
        user_id = struct.session.get("id", "")
        popular_rows, popular_total = struct.recipe.search_dishes(page=1, dump=3, sort=constants.RECIPE_SORTS["VIEW_COUNT"])
        latest_rows, latest_total = struct.recipe.search_dishes(page=1, dump=6, sort=constants.RECIPE_SORTS["LATEST"])
        pool_rows, pool_total = struct.recipe.search_dishes(page=1, dump=20, sort=constants.RECIPE_SORTS["LATEST"])
        pool = list(pool_rows or [])
        if len(pool) > 2:
            random_rows = random.sample(pool, 2)
        else:
            random_rows = pool
        popular = [dish_dto(row) for row in popular_rows]
        latest = [dish_dto(row) for row in latest_rows]
        random_items = [dish_dto(row) for row in random_rows]
        recommended = [dish_dto(row) for row in struct.recipe.get_recommended(user_id, limit=6)] if user_id else []
    except Exception as error:
        wiz.response.status(400, message=str(error))

    wiz.response.status(
        200,
        recommended=recommended,
        popular=popular,
        randomItems=random_items,
        latest=latest,
        totals={
            "popular": popular_total,
            "latest": latest_total,
            "pool": pool_total,
        },
        keywords=["저염", "이유식", "간단요리", "고단백", "부드러운 식감"],
    )

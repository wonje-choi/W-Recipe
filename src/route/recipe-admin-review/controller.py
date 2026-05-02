import datetime
import json

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


def admin_id():
    return session.get("id", "")


def dish_dto(dish):
    return {
        "targetType": "recipe_dish",
        "id": dish.get("id"),
        "title": dish.get("name", ""),
        "category": dish.get("category", ""),
        "status": dish.get("status", ""),
        "riskFlags": [],
        "safety": {"hasRisk": False, "riskFlags": [], "issues": [], "summary": "Dish 단독 검수 대상"},
        "createdAt": date_text(dish.get("created_at")),
        "updatedAt": date_text(dish.get("updated_at")),
    }


def version_dto(version):
    safety = struct.safety.check_version(version)
    return {
        "targetType": "recipe_version",
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "summary": version.get("summary", ""),
        "sourceType": version.get("source_type", ""),
        "status": version.get("status", ""),
        "aiModified": bool(version.get("ai_modified")),
        "riskFlags": safety.get("riskFlags", []),
        "safety": safety,
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }


def ai_dto(item):
    safety = struct.safety.check_modification(item)
    return {
        "targetType": "ai_modification",
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "purpose": item.get("purpose", ""),
        "targetUserType": item.get("target_user_type", ""),
        "originalSummary": item.get("original_summary", ""),
        "improvementReason": item.get("improvement_reason", ""),
        "status": item.get("status", ""),
        "riskFlags": safety.get("riskFlags", []),
        "safety": safety,
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def normalize_target_type(target_type):
    if target_type in ["dish", "recipe", "recipe_dish"]:
        return "recipe_dish"
    if target_type in ["version", "recipe_version"]:
        return "recipe_version"
    if target_type in ["ai", "ai_modification", "ai_recipe_modification"]:
        return "ai_modification"
    return ""


def fetch_target(target_type, target_id):
    target_type = normalize_target_type(target_type)
    if target_type == "recipe_dish":
        item = struct.recipe.get_dish(target_id, public=False)
    elif target_type == "recipe_version":
        item = struct.recipe.get_version(target_id, public=False)
    elif target_type == "ai_modification":
        item = struct.db("ai_recipe_modification").get(id=target_id)
    else:
        item = None
    if item is None:
        wiz.response.status(404, message="검수 대상을 찾을 수 없습니다.")
    return target_type, item


def target_dto(target_type, item):
    if target_type == "recipe_dish":
        return dish_dto(item)
    if target_type == "recipe_version":
        return version_dto(item)
    return ai_dto(item)


def pending_rows(page, dump):
    pending = constants.RECIPE_STATUSES["PENDING_REVIEW"]
    ai_pending = constants.AI_STATUSES["PENDING_REVIEW"]
    dish_db = struct.db("recipe_dish")
    version_db = struct.db("recipe_version")
    ai_db = struct.db("ai_recipe_modification")
    dishes = dish_db.rows(status=pending, page=page, dump=dump, orderby="created_at", order="DESC")
    versions = version_db.rows(status=pending, page=page, dump=dump, orderby="created_at", order="DESC")
    ai_items = ai_db.rows(status=ai_pending, page=page, dump=dump, orderby="created_at", order="DESC")
    return {
        "dishes": [dish_dto(item) for item in dishes],
        "versions": [version_dto(item) for item in versions],
        "aiModifications": [ai_dto(item) for item in ai_items],
        "counts": {
            "dishes": dish_db.count(status=pending) or 0,
            "versions": version_db.count(status=pending) or 0,
            "aiModifications": ai_db.count(status=ai_pending) or 0,
        },
    }


def approve_target(target_type, target_id, before, reason=""):
    reviewer = admin_id()
    now = datetime.datetime.now()
    if target_type == "recipe_dish":
        struct.recipe.update_dish(target_id, {"status": constants.RECIPE_STATUSES["APPROVED"]})
        return struct.recipe.get_dish(target_id, public=False)
    if target_type == "recipe_version":
        struct.recipe.update_version(target_id, {
            "status": constants.RECIPE_STATUSES["APPROVED"],
            "reviewed_by": reviewer,
            "reviewed_at": now,
        })
        return struct.recipe.get_version(target_id, public=False)
    struct.ai.approve_modification(target_id, reviewer, reason)
    return struct.db("ai_recipe_modification").get(id=target_id)


def reject_target(target_type, target_id, before, reason=""):
    reviewer = admin_id()
    now = datetime.datetime.now()
    if target_type == "recipe_dish":
        struct.recipe.update_dish(target_id, {"status": constants.RECIPE_STATUSES["REJECTED"]})
        item = struct.recipe.get_dish(target_id, public=False)
        item["rejectedReason"] = reason
        return item
    if target_type == "recipe_version":
        struct.recipe.update_version(target_id, {
            "status": constants.RECIPE_STATUSES["REJECTED"],
            "reviewed_by": reviewer,
            "reviewed_at": now,
        })
        item = struct.recipe.get_version(target_id, public=False)
        item["rejectedReason"] = reason
        return item
    struct.ai.reject_modification(target_id, reviewer, reason)
    return struct.db("ai_recipe_modification").get(id=target_id)


method = wiz.request.method()

segment = wiz.request.match("/api/admin/reviews/pending")
if segment is not None:
    if method != "GET":
        wiz.response.status(405, message="Method not allowed")
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    try:
        data = pending_rows(page, dump)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, page=page, dump=dump, **data)

segment = wiz.request.match("/api/admin/reviews/<target_type>/<target_id>/approve")
if segment is not None:
    if method != "POST":
        wiz.response.status(405, message="Method not allowed")
    target_type, before = fetch_target(segment.target_type, segment.target_id)
    try:
        data = request_data()
        reason = data.get("reason", "")
        after = approve_target(target_type, segment.target_id, before, reason)
        struct.admin_log.create("review_approve", target_type, segment.target_id, before, after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, item=target_dto(target_type, after))

segment = wiz.request.match("/api/admin/reviews/<target_type>/<target_id>/reject")
if segment is not None:
    if method != "POST":
        wiz.response.status(405, message="Method not allowed")
    target_type, before = fetch_target(segment.target_type, segment.target_id)
    try:
        data = request_data()
        reason = data.get("reason", "")
        after = reject_target(target_type, segment.target_id, before, reason)
        log_after = dict(after)
        if reason:
            log_after["reviewReason"] = reason
        struct.admin_log.create("review_reject", target_type, segment.target_id, before, log_after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, item=target_dto(target_type, after))

wiz.response.status(404, message="지원하지 않는 관리자 검수 API 경로입니다.")

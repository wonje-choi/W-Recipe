import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


def to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


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


def payload_data(data):
    payload = {}
    mapping = {
        "recipeVersionId": "recipe_version_id",
        "recipe_version_id": "recipe_version_id",
        "purpose": "purpose",
        "targetUserType": "target_user_type",
        "target_user_type": "target_user_type",
        "tasteDirection": "taste_direction",
        "taste_direction": "taste_direction",
        "promptVersion": "prompt_version",
        "prompt_version": "prompt_version",
        "sodiumPreference": "sodium_preference",
        "sodium_preference": "sodium_preference",
        "texturePreference": "texture_preference",
        "texture_preference": "texture_preference",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key)
    if "excludedIngredients" in data:
        payload["excluded_ingredients"] = data.get("excludedIngredients")
    if "excluded_ingredients" in data:
        payload["excluded_ingredients"] = data.get("excluded_ingredients")
    if "allergies" in data:
        payload["allergies"] = data.get("allergies")
    if "desiredCookingTime" in data:
        payload["desired_cooking_time"] = to_int(data.get("desiredCookingTime"), 0)
    if "desired_cooking_time" in data:
        payload["desired_cooking_time"] = to_int(data.get("desired_cooking_time"), 0)
    if "babyAgeMonth" in data:
        payload["baby_age_month"] = to_int(data.get("babyAgeMonth"), 0)
    if "baby_age_month" in data:
        payload["baby_age_month"] = to_int(data.get("baby_age_month"), 0)
    return payload


def version_dto(version):
    if not version:
        return None
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "summary": version.get("summary", ""),
        "sourceType": version.get("source_type", ""),
        "status": version.get("status", ""),
        "aiModified": bool(version.get("ai_modified")),
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }


def modification_dto(item):
    if not item:
        return None
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestedBy": item.get("requested_by", ""),
        "purpose": item.get("purpose", ""),
        "targetUserType": item.get("target_user_type", ""),
        "originalSummary": item.get("original_summary", ""),
        "modifiedIngredients": struct.json_loads(item.get("modified_ingredients"), []),
        "modifiedSteps": struct.json_loads(item.get("modified_steps"), []),
        "improvementReason": item.get("improvement_reason", ""),
        "tasteImprovementPoint": item.get("taste_improvement_point", ""),
        "sodiumReductionPoint": item.get("sodium_reduction_point", ""),
        "babyFoodSafetyNotes": item.get("baby_food_safety_notes", ""),
        "allergenWarnings": struct.json_loads(item.get("allergen_warnings"), []),
        "cautionNotes": struct.json_loads(item.get("caution_notes"), []),
        "riskFlags": struct.json_loads(item.get("risk_flags"), []),
        "status": item.get("status", ""),
        "reviewedBy": item.get("reviewed_by", ""),
        "reviewedAt": date_text(item.get("reviewed_at")),
        "rejectedReason": item.get("rejected_reason", ""),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def log_dto(log):
    if not log:
        return None
    return {
        "id": log.get("id"),
        "requestType": log.get("request_type", ""),
        "targetId": log.get("target_id", ""),
        "promptVersion": log.get("prompt_version", ""),
        "status": log.get("status", ""),
        "inputSummary": log.get("input_summary", ""),
        "outputSummary": log.get("output_summary", ""),
        "errorMessage": log.get("error_message", ""),
        "tokenUsage": struct.json_loads(log.get("token_usage"), {}),
        "costEstimate": str(log.get("cost_estimate") or "0"),
        "durationMs": int(log.get("duration_ms") or 0),
        "startedAt": date_text(log.get("started_at")),
        "finishedAt": date_text(log.get("finished_at")),
        "createdAt": date_text(log.get("created_at")),
    }


method = wiz.request.method()
if method == "POST":
    try:
        data = request_data()
        payload = payload_data(data)
        result = struct.ai_diet.create(payload, requester_user_id=struct.session_user_id())
        modification = result.get("modification")
        after_value = {
            "version": version_dto(result.get("version")),
            "modification": modification_dto(modification),
            "log": log_dto(result.get("log")),
        }
        if struct.is_admin():
            struct.admin_log.create("ai_diet_modification_create", "ai_recipe_modification", modification.get("id", ""), {}, after_value)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(
        201,
        version=version_dto(result.get("version")),
        modification=modification_dto(result.get("modification")),
        log=log_dto(result.get("log")),
        purposes=constants.AI_PURPOSES,
    )

wiz.response.status(405, message="Method not allowed")

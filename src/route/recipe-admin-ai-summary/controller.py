import datetime
import json

struct = wiz.model("portal/recipe/struct")


def to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value in ["true", "True", "1", 1]:
        return True
    if value in ["false", "False", "0", 0]:
        return False
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


def parse_payload(data):
    payload = {}
    mapping = {
        "sourceId": "source_id",
        "source_id": "source_id",
        "sourceType": "source_type",
        "source_type": "source_type",
        "sourceUrl": "source_url",
        "source_url": "source_url",
        "sourceTitle": "source_title",
        "source_title": "source_title",
        "sourceAuthor": "source_author",
        "source_author": "source_author",
        "sourceSummary": "source_summary",
        "source_summary": "source_summary",
        "dishId": "dish_id",
        "dish_id": "dish_id",
        "dishName": "dish_name",
        "dish_name": "dish_name",
        "name": "name",
        "title": "title",
        "versionTitle": "version_title",
        "version_title": "version_title",
        "text": "text",
        "content": "content",
        "rawText": "raw_text",
        "raw_text": "raw_text",
        "description": "description",
        "category": "category",
        "difficulty": "difficulty",
        "promptVersion": "prompt_version",
        "prompt_version": "prompt_version",
        "thumbnailUrl": "thumbnail_url",
        "thumbnail_url": "thumbnail_url",
        "channel": "channel",
        "author": "author",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key)
    if "tags" in data:
        payload["tags"] = data.get("tags")
    if "robotsAllowed" in data:
        payload["robots_allowed"] = to_bool(data.get("robotsAllowed"), False)
    if "robots_allowed" in data:
        payload["robots_allowed"] = to_bool(data.get("robots_allowed"), False)
    return payload


def dish_dto(dish):
    if not dish:
        return None
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
    if not version:
        return None
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


def source_dto(source):
    if not source:
        return None
    return {
        "id": source.get("id"),
        "sourceType": source.get("source_type", ""),
        "sourceUrl": source.get("source_url", ""),
        "sourceUrlHash": source.get("source_url_hash", ""),
        "title": source.get("title", ""),
        "author": source.get("author", ""),
        "thumbnailUrl": source.get("thumbnail_url", ""),
        "collectedTextSummary": source.get("collected_text_summary", ""),
        "rawContentStoragePolicy": source.get("raw_content_storage_policy", "summary_only"),
        "crawlStatus": source.get("crawl_status", ""),
        "robotsAllowed": bool(source.get("robots_allowed")),
        "duplicateOf": source.get("duplicate_of", ""),
        "collectedAt": date_text(source.get("collected_at")),
        "retryCount": int(source.get("retry_count") or 0),
        "lastCheckedAt": date_text(source.get("last_checked_at")),
        "errorMessage": source.get("error_message", ""),
        "createdAt": date_text(source.get("created_at")),
        "updatedAt": date_text(source.get("updated_at")),
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
        payload = parse_payload(data)
        result = struct.ai.parse_recipe_summary(payload, admin_user_id=struct.session_user_id())
        version = result.get("version")
        after_value = {
            "dish": dish_dto(result.get("dish")),
            "version": version_dto(version),
            "source": source_dto(result.get("source")),
            "log": log_dto(result.get("log")),
        }
        struct.admin_log.create("ai_recipe_summary_create", "recipe_version", version.get("id", ""), {}, after_value)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(
        201,
        dish=dish_dto(result.get("dish")),
        version=version_dto(result.get("version")),
        source=source_dto(result.get("source")),
        candidate=result.get("candidate", {}),
        log=log_dto(result.get("log")),
    )

wiz.response.status(405, message="Method not allowed")

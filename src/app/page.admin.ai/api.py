import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

AI_STATUS_LABELS = {
    "queued": "대기",
    "processing": "처리 중",
    "pending_review": "검수 대기",
    "approved": "승인",
    "rejected": "반려",
    "failed": "실패",
    "completed": "완료",
}

PURPOSE_LABELS = {
    "tastier": "맛 개선",
    "low_sodium": "저염식",
    "baby_food": "이유식",
    "diet": "다이어트",
    "high_protein": "고단백",
    "shorter_time": "시간 단축",
    "simpler_ingredients": "재료 단순화",
    "softer_texture": "부드러운 식감",
}

PROMPT_TYPE_LABELS = {
    "recipe_summary": "레시피 요약",
    "low_sodium": "저염식",
    "baby_food": "이유식",
    "taste_improvement": "맛 개선",
    "review_summary": "검수 요약",
}


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


def option_items(values, labels):
    return [{"value": value, "label": labels.get(value, value)} for value in values]


def parse_json_text(value, default):
    if value in [None, ""]:
        return struct.json_dumps(default)
    if isinstance(value, (list, dict)):
        return struct.json_dumps(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, type(default)):
                return struct.json_dumps(parsed)
        except Exception:
            pass
        return struct.json_dumps(default)
    return struct.json_dumps(default)


def token_total(token_usage):
    if not isinstance(token_usage, dict):
        return 0
    total = 0
    for key in ["total", "total_tokens", "tokens", "input_tokens", "output_tokens", "prompt_tokens", "completion_tokens"]:
        try:
            total += int(token_usage.get(key) or 0)
        except Exception:
            pass
    return total


def dish_dto(dish):
    if not dish:
        return None
    return {
        "id": dish.get("id"),
        "name": dish.get("name", ""),
        "status": dish.get("status", ""),
        "category": dish.get("category", ""),
    }


def version_dto(version):
    if not version:
        return None
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "summary": version.get("summary", ""),
        "status": version.get("status", ""),
        "sourceType": version.get("source_type", ""),
        "sourceUrl": version.get("source_url", ""),
        "allergenInfo": struct.json_loads(version.get("allergen_info"), []),
    }


def modification_dto(item):
    version = None
    dish = None
    try:
        version = struct.recipe.get_version(item.get("recipe_version_id", ""), public=False)
        if version:
            dish = struct.recipe.get_dish(version.get("dish_id", ""), public=False)
    except Exception:
        version = None
    safety = struct.safety.check_modification(item)
    allergen_warnings = struct.json_loads(item.get("allergen_warnings"), [])
    caution_notes = struct.json_loads(item.get("caution_notes"), [])
    risk_flags = safety.get("riskFlags", [])
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestedBy": item.get("requested_by", ""),
        "purpose": item.get("purpose", ""),
        "purposeLabel": PURPOSE_LABELS.get(item.get("purpose", ""), item.get("purpose", "")),
        "targetUserType": item.get("target_user_type", ""),
        "originalSummary": item.get("original_summary", ""),
        "modifiedIngredients": struct.json_loads(item.get("modified_ingredients"), []),
        "modifiedSteps": struct.json_loads(item.get("modified_steps"), []),
        "improvementReason": item.get("improvement_reason", ""),
        "tasteImprovementPoint": item.get("taste_improvement_point", ""),
        "sodiumReductionPoint": item.get("sodium_reduction_point", ""),
        "babyFoodSafetyNotes": item.get("baby_food_safety_notes", ""),
        "allergenWarnings": allergen_warnings,
        "cautionNotes": caution_notes,
        "riskFlags": risk_flags,
        "confidenceScore": float(item.get("confidence_score") or 0.0),
        "safety": safety,
        "status": item.get("status", ""),
        "statusLabel": AI_STATUS_LABELS.get(item.get("status", ""), item.get("status", "")),
        "reviewedBy": item.get("reviewed_by", ""),
        "reviewedAt": date_text(item.get("reviewed_at")),
        "rejectedReason": item.get("rejected_reason", ""),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
        "version": version_dto(version),
        "dish": dish_dto(dish),
    }


def prompt_dto(prompt):
    return {
        "id": prompt.get("id"),
        "promptKey": prompt.get("prompt_key", ""),
        "promptKeyLabel": PROMPT_TYPE_LABELS.get(prompt.get("prompt_key", ""), prompt.get("prompt_key", "")),
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
        "version": "version",
        "title": "title",
        "description": "description",
        "template": "template",
        "modelHint": "model_hint",
        "changeReason": "change_reason",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key)
    if "inputSchema" in data:
        payload["input_schema"] = parse_json_text(data.get("inputSchema"), {})
    if "outputSchema" in data:
        payload["output_schema"] = parse_json_text(data.get("outputSchema"), {})
    if "isActive" in data:
        payload["is_active"] = to_bool(data.get("isActive"), False)
    return payload


def log_dto(log):
    token_usage = struct.json_loads(log.get("token_usage"), {})
    return {
        "id": log.get("id"),
        "requestType": log.get("request_type", ""),
        "requestTypeLabel": PURPOSE_LABELS.get(log.get("request_type", ""), PROMPT_TYPE_LABELS.get(log.get("request_type", ""), log.get("request_type", ""))),
        "targetId": log.get("target_id", ""),
        "promptVersion": log.get("prompt_version", ""),
        "status": log.get("status", ""),
        "statusLabel": AI_STATUS_LABELS.get(log.get("status", ""), log.get("status", "")),
        "inputSummary": log.get("input_summary", ""),
        "outputSummary": log.get("output_summary", ""),
        "errorMessage": log.get("error_message", ""),
        "tokenUsage": token_usage,
        "tokenTotal": token_total(token_usage),
        "costEstimate": str(log.get("cost_estimate") or "0"),
        "durationMs": int(log.get("duration_ms") or 0),
        "startedAt": date_text(log.get("started_at")),
        "finishedAt": date_text(log.get("finished_at")),
        "createdAt": date_text(log.get("created_at")),
    }


def options():
    try:
        struct.require_admin()
        data = {
            "aiStatuses": option_items(constants.values("AI_STATUSES"), AI_STATUS_LABELS),
            "logStatuses": option_items(constants.values("AI_PROCESSING_STATUSES"), AI_STATUS_LABELS),
            "purposes": option_items(constants.values("AI_PURPOSES"), PURPOSE_LABELS),
            "promptTypes": option_items(constants.values("AI_PROMPT_TYPES"), PROMPT_TYPE_LABELS),
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **data)


def get_settings():
    try:
        struct.require_admin()
        settings = struct.ai.get_settings()
        youtube = struct.youtube.masked_settings()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, settings={
        "autoApproveThreshold": settings.get("auto_approve_threshold", 0.85),
        "youtubeApiKeyConfigured": youtube.get("apiKeyConfigured", False),
        "youtubeApiKeyMasked": youtube.get("apiKey", ""),
        "youtubeApiKey": "",
    })


def save_settings():
    data = request_data()
    try:
        struct.require_admin()
        before = struct.ai.get_settings()
        youtube_before = struct.youtube.masked_settings()
        settings = struct.ai.save_settings({
            "auto_approve_threshold": data.get("autoApproveThreshold", data.get("auto_approve_threshold", before.get("auto_approve_threshold"))),
        })
        youtube_key = data.get("youtubeApiKey", data.get("youtube_api_key", ""))
        youtube = youtube_before
        if youtube_key:
            struct.youtube.save_settings({"api_key": youtube_key})
            youtube = struct.youtube.masked_settings()
            struct.admin_log.create("youtube_settings_update", "youtube_settings", "api_key", youtube_before, youtube)
        struct.admin_log.create("ai_settings_update", "ai_settings", "auto_approve_threshold", before, settings)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, settings={
        "autoApproveThreshold": settings.get("auto_approve_threshold", 0.85),
        "youtubeApiKeyConfigured": youtube.get("apiKeyConfigured", False),
        "youtubeApiKeyMasked": youtube.get("apiKey", ""),
        "youtubeApiKey": "",
    })


def reviews():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", 20))
    status = wiz.request.query("status", constants.AI_STATUSES["PENDING_REVIEW"])
    purpose = wiz.request.query("purpose", "")
    try:
        struct.require_admin()
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if purpose:
            filters["purpose"] = purpose
        db = struct.db("ai_recipe_modification")
        rows = db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = db.count(**filters) or 0
        items = [modification_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))


def review_action():
    data = request_data()
    modification_id = data.get("modificationId") or data.get("id")
    action = data.get("action", "")
    reason = data.get("reason", "")
    try:
        struct.require_admin()
        db = struct.db("ai_recipe_modification")
        before = db.get(id=modification_id)
        if before is None:
            raise Exception("AI 검수 대상을 찾을 수 없습니다.")
        if action == "approve":
            struct.ai.approve_modification(modification_id, struct.session_user_id(), reason)
            log_action = "ai_modification_approve"
        elif action == "reject":
            struct.ai.reject_modification(modification_id, struct.session_user_id(), reason)
            log_action = "ai_modification_reject"
        else:
            raise Exception("지원하지 않는 검수 액션입니다.")
        after = db.get(id=modification_id)
        log_after = dict(after)
        if reason:
            log_after["reviewReason"] = reason
        struct.admin_log.create(log_action, "ai_recipe_modification", modification_id, before, log_after)
        item = modification_dto(after)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, item=item)


def regenerate():
    data = request_data()
    modification_id = data.get("modificationId") or data.get("id")
    try:
        struct.require_admin()
        db = struct.db("ai_recipe_modification")
        before = db.get(id=modification_id)
        if before is None:
            raise Exception("재생성할 AI 결과를 찾을 수 없습니다.")
        result = struct.ai_diet.create({
            "recipe_version_id": before.get("recipe_version_id", ""),
            "purpose": before.get("purpose", ""),
            "target_user_type": before.get("target_user_type", ""),
        }, requester_user_id=struct.session_user_id())
        modification = result.get("modification")
        struct.admin_log.create("ai_modification_regenerate", "ai_recipe_modification", modification_id, before, modification)
        item = modification_dto(modification)
        log = log_dto(result.get("log")) if result.get("log") else None
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, item=item, log=log)


def prompts():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", 20))
    prompt_key = wiz.request.query("promptKey", "")
    active_value = wiz.request.query("isActive", "")
    is_active = to_bool(active_value, None)
    try:
        struct.require_admin()
        rows, total = struct.ai.prompt_rows(prompt_key=prompt_key, is_active=is_active, page=page, dump=dump)
        items = [prompt_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))


def save_prompt():
    data = request_data()
    prompt_id = data.get("id", "")
    try:
        struct.require_admin()
        payload = prompt_payload(data)
        if prompt_id:
            before = struct.ai.get_prompt(prompt_id)
            struct.ai.update_prompt(prompt_id, payload, admin_user_id=struct.session_user_id())
            prompt = struct.ai.get_prompt(prompt_id)
            struct.admin_log.create("ai_prompt_update", "ai_prompt_template", prompt_id, before, prompt)
        else:
            prompt_id = struct.ai.create_prompt(payload, admin_user_id=struct.session_user_id())
            prompt = struct.ai.get_prompt(prompt_id)
            struct.admin_log.create("ai_prompt_create", "ai_prompt_template", prompt_id, {}, prompt)
        item = prompt_dto(prompt)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, prompt=item)


def prompt_action():
    data = request_data()
    prompt_id = data.get("promptId") or data.get("id")
    action = data.get("action", "")
    reason = data.get("reason", "")
    try:
        struct.require_admin()
        before = struct.ai.get_prompt(prompt_id)
        if action == "activate":
            struct.ai.activate_prompt(prompt_id, admin_user_id=struct.session_user_id(), change_reason=reason)
            log_action = "ai_prompt_activate"
        elif action == "deactivate":
            struct.ai.deactivate_prompt(prompt_id, admin_user_id=struct.session_user_id(), change_reason=reason)
            log_action = "ai_prompt_deactivate"
        else:
            raise Exception("지원하지 않는 프롬프트 액션입니다.")
        prompt = struct.ai.get_prompt(prompt_id)
        struct.admin_log.create(log_action, "ai_prompt_template", prompt_id, before, prompt)
        item = prompt_dto(prompt)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, prompt=item)


def logs():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", 20))
    status = wiz.request.query("status", "")
    request_type = wiz.request.query("requestType", "")
    try:
        struct.require_admin()
        filters = {}
        if status and status != "all":
            filters["status"] = status
        if request_type:
            filters["request_type"] = request_type
        db = struct.db("ai_processing_log")
        rows = db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = db.count(**filters) or 0
        items = [log_dto(row) for row in rows]
        cost_total = "0"
        token_sum = 0
        for item in items:
            token_sum += int(item.get("tokenTotal") or 0)
            try:
                cost_total = str(float(cost_total) + float(item.get("costEstimate") or 0))
            except Exception:
                pass
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, tokenTotal=token_sum, costTotal=cost_total, empty=(total == 0))

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


def parse_data():
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


def current_user():
    try:
        return struct.auth.current_user()
    except Exception:
        return None


def purpose_options():
    return [
        {"label": "저염식", "value": constants.AI_PURPOSES["LOW_SODIUM"], "description": "나트륨 부담을 낮추고 향과 감칠맛으로 보완"},
        {"label": "이유식", "value": constants.AI_PURPOSES["BABY_FOOD"], "description": "월령, 입자 크기, 알레르기 주의 중심으로 조정"},
        {"label": "더 맛있게", "value": constants.AI_PURPOSES["TASTIER"], "description": "풍미, 식감, 조리 안정성을 개선"},
        {"label": "조리시간 단축", "value": constants.AI_PURPOSES["SHORTER_TIME"], "description": "단계와 대기 시간을 줄이는 방향"},
        {"label": "재료 단순화", "value": constants.AI_PURPOSES["SIMPLER_INGREDIENTS"], "description": "핵심 재료 중심으로 간소화"},
        {"label": "고단백", "value": constants.AI_PURPOSES["HIGH_PROTEIN"], "description": "단백질 재료와 균형을 보강"},
    ]


def version_option(dish, version):
    return {
        "dishId": dish.get("id"),
        "recipeVersionId": version.get("id"),
        "name": dish.get("name", ""),
        "category": dish.get("category", ""),
        "tags": struct.json_loads(dish.get("tags"), []),
        "versionTitle": version.get("title", ""),
        "summary": version.get("summary", ""),
        "aiModified": bool(version.get("ai_modified")),
        "viewCount": int(version.get("view_count") or 0),
    }


def recipe_options(text="", dump=12):
    rows, total = struct.recipe.search_dishes(text=text, page=1, dump=dump, sort="popular")
    options = []
    for dish in rows:
        versions, version_total = struct.recipe.versions(dish.get("id"), public=True, page=1, dump=1)
        if versions:
            options.append(version_option(dish, versions[0]))
    return options, total


def modification_dto(item):
    if not item:
        return None
    return {
        "id": item.get("id"),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "purpose": item.get("purpose", ""),
        "targetUserType": item.get("target_user_type", ""),
        "status": item.get("status", ""),
        "improvementReason": item.get("improvement_reason", ""),
        "tasteImprovementPoint": item.get("taste_improvement_point", ""),
        "sodiumReductionPoint": item.get("sodium_reduction_point", ""),
        "babyFoodSafetyNotes": item.get("baby_food_safety_notes", ""),
        "riskFlags": struct.json_loads(item.get("risk_flags"), []),
        "createdAt": date_text(item.get("created_at")),
    }


def payload_data(data):
    payload = {
        "recipe_version_id": data.get("recipeVersionId", ""),
        "purpose": data.get("purpose", constants.AI_PURPOSES["TASTIER"]),
        "target_user_type": data.get("targetUserType", ""),
        "excluded_ingredients": data.get("excludedIngredients", ""),
        "allergies": data.get("allergies", ""),
        "desired_cooking_time": to_int(data.get("desiredCookingTime"), 0),
        "baby_age_month": to_int(data.get("babyAgeMonth"), 0),
        "sodium_preference": data.get("sodiumPreference", ""),
        "texture_preference": data.get("texturePreference", ""),
    }
    taste_direction = data.get("tasteDirection", "")
    additional_request = data.get("additionalRequest", "")
    if additional_request:
        taste_direction = f"{taste_direction}\n추가 요청: {additional_request}".strip()
    payload["taste_direction"] = taste_direction
    return payload


def load():
    text = wiz.request.query("text", "")
    try:
        options, total = recipe_options(text=text)
        user = current_user()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(
        200,
        user=user,
        recipeOptions=options,
        total=total,
        purposes=purpose_options(),
        targetUserTypes=["일반", "저염식 필요", "영유아", "운동/고단백", "간단 조리 선호"],
        policy={
            "status": constants.AI_STATUSES["PENDING_REVIEW"],
            "message": "AI 개량 요청은 검수 대기로 저장되며 관리자 승인 전에는 공개되지 않습니다.",
        },
    )


def search_recipes():
    text = wiz.request.query("text", "")
    try:
        options, total = recipe_options(text=text)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, recipeOptions=options, total=total)


def submit():
    data = parse_data()
    user = current_user()
    if user is None:
        wiz.response.status(401, message="로그인이 필요합니다.")
    try:
        payload = payload_data(data)
        result = struct.ai_diet.create(payload, requester_user_id=user.get("id"))
        modification = result.get("modification")
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, modification=modification_dto(modification), policy={"status": constants.AI_STATUSES["PENDING_REVIEW"]})

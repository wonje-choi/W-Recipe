import datetime

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


LOW_SODIUM_INGREDIENT_KEYWORDS = ["소금", "간장", "된장", "고추장", "액젓", "젓갈", "치즈", "햄", "베이컨", "소시지", "라면스프"]
BABY_FOOD_STAGES = {
    "early": {"label": "초기", "age": "만 4~6개월", "particle": "곱게 간 미음", "storage": "조리 후 빠르게 식혀 24시간 내 냉장 섭취", "freezing": "소분 냉동 가능"},
    "middle": {"label": "중기", "age": "만 7~8개월", "particle": "작게 으깬 죽", "storage": "냉장 1일, 재가열은 1회만 권장", "freezing": "소분 냉동 가능"},
    "late": {"label": "후기", "age": "만 9~11개월", "particle": "잇몸으로 으깰 수 있는 무른 입자", "storage": "냉장 1일 보관 후 충분히 재가열", "freezing": "재료별 식감 변화를 확인"},
    "complete": {"label": "완료기", "age": "만 12개월 이후", "particle": "작게 자른 부드러운 고형식", "storage": "성인식보다 짧게 보관", "freezing": "양념 전 상태로 냉동 권장"},
}
BABY_WARNING_KEYWORDS = {
    "꿀": "꿀은 12개월 전 영아에게 제공하지 않습니다.",
    "견과": "견과류는 알레르기와 질식 위험이 있어 형태와 시기를 확인하세요.",
    "땅콩": "땅콩은 알레르기와 질식 위험이 있어 보호자 확인이 필요합니다.",
    "생식": "생식 재료는 위생과 소화 부담을 확인하세요.",
    "회": "생선회 등 익히지 않은 식재료는 이유식에 적합하지 않습니다.",
    "포도": "포도와 작은 둥근 식재료는 질식 위험이 있어 잘게 손질하세요.",
    "방울토마토": "방울토마토는 질식 위험이 있어 껍질과 크기를 조절하세요.",
    "떡": "떡처럼 끈적한 식감은 질식 위험이 있어 주의가 필요합니다.",
    "소금": "이유식에는 과도한 간을 피하고 재료 본연의 맛을 우선합니다.",
    "간장": "간장 사용량은 월령과 나트륨 부담을 기준으로 줄여야 합니다.",
}


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


def stringify_item(item):
    if item is None:
        return ""
    if isinstance(item, str):
        return item
    if isinstance(item, (int, float)):
        return str(item)
    if isinstance(item, dict):
        if item.get("name") and item.get("amount"):
            return f"{item.get('name')} {item.get('amount')}"
        if item.get("ingredient") and item.get("amount"):
            return f"{item.get('ingredient')} {item.get('amount')}"
        return ", ".join([f"{key}: {value}" for key, value in item.items() if value not in [None, ""]])
    return str(item)


def first_items(value, limit=3):
    if not value:
        return []
    if isinstance(value, dict):
        items = [f"{key}: {value[key]}" for key in value.keys() if value[key] not in [None, ""]]
    elif isinstance(value, list):
        items = [stringify_item(item) for item in value]
    else:
        items = [stringify_item(value)]
    return [item for item in items if item][:limit]


def sodium_ingredients(ingredients):
    result = []
    for item in ingredients or []:
        text = stringify_item(item)
        if not text:
            continue
        for keyword in LOW_SODIUM_INGREDIENT_KEYWORDS:
            if keyword in text:
                result.append(text)
                break
        if len(result) >= 3:
            break
    return result


def low_sodium_preview(dish_id):
    try:
        rows, total = struct.recipe.versions(dish_id, public=True, page=1, dump=1)
    except Exception:
        rows = []
    if not rows:
        return {
            "available": False,
            "sodiumPoints": ["승인된 저염 버전 정보가 준비 중입니다."],
            "sodiumIngredients": [],
            "flavorTips": ["향신채, 산미, 감칠맛 재료로 간의 빈자리를 보완해보세요."],
            "aiModified": False,
        }
    version = rows[0]
    ingredients = struct.json_loads(version.get("ingredients"), [])
    sodium_info = struct.json_loads(version.get("sodium_info"), {})
    cooking_tips = struct.json_loads(version.get("cooking_tips"), [])
    substitution_tips = struct.json_loads(version.get("substitution_tips"), [])
    points = first_items(sodium_info, 3)
    if not points:
        points = ["소금·장류 사용량과 가공식품 포함 여부를 확인하세요."]
    flavor_tips = first_items(cooking_tips, 2) + first_items(substitution_tips, 2)
    if not flavor_tips:
        flavor_tips = ["마늘, 양파, 레몬즙, 식초, 버섯처럼 향과 감칠맛을 주는 재료를 활용하세요."]
    return {
        "available": True,
        "versionId": version.get("id"),
        "sodiumPoints": points[:3],
        "sodiumIngredients": sodium_ingredients(ingredients),
        "flavorTips": flavor_tips[:3],
        "aiModified": bool(version.get("ai_modified")),
    }


def detect_baby_stage(dish, version, requested_stage=""):
    if requested_stage in BABY_FOOD_STAGES:
        return requested_stage
    haystack = " ".join([
        dish.get("name", ""),
        dish.get("description", ""),
        " ".join(struct.json_loads(dish.get("tags", "[]"), default=[])),
        version.get("title", "") if version else "",
        version.get("summary", "") if version else "",
    ])
    for key, rule in BABY_FOOD_STAGES.items():
        if rule["label"] in haystack or rule["age"] in haystack:
            return key
    return "middle"


def baby_warnings(values):
    warnings = []
    for value in values:
        text = stringify_item(value)
        if not text:
            continue
        for keyword, message in BABY_WARNING_KEYWORDS.items():
            if keyword in text and message not in warnings:
                warnings.append(message)
        if len(warnings) >= 4:
            break
    if not warnings:
        warnings.append("월령, 알레르기 이력, 입자 크기는 보호자가 최종 확인해야 합니다.")
    return warnings[:4]


def allergen_candidates(ingredients):
    keywords = ["달걀", "계란", "우유", "밀", "대두", "콩", "땅콩", "견과", "새우", "게", "생선", "참깨"]
    result = []
    for item in ingredients or []:
        text = stringify_item(item)
        for keyword in keywords:
            if keyword in text and keyword not in result:
                result.append(keyword)
        if len(result) >= 5:
            break
    return result


def baby_food_preview(dish, stage=""):
    try:
        rows, total = struct.recipe.versions(dish.get("id"), public=True, page=1, dump=1)
    except Exception:
        rows = []
    version = rows[0] if rows else None
    detected_stage = detect_baby_stage(dish, version, stage)
    rule = BABY_FOOD_STAGES.get(detected_stage, BABY_FOOD_STAGES["middle"])
    ingredients = struct.json_loads(version.get("ingredients"), []) if version else []
    steps = struct.json_loads(version.get("steps"), []) if version else []
    cooking_tips = struct.json_loads(version.get("cooking_tips"), []) if version else []
    safety_values = ingredients + steps + cooking_tips
    return {
        "available": version is not None,
        "versionId": version.get("id") if version else "",
        "stage": detected_stage,
        "stageLabel": rule["label"],
        "recommendedAge": rule["age"],
        "particleSize": rule["particle"],
        "storage": rule["storage"],
        "freezing": rule["freezing"],
        "allergens": allergen_candidates(ingredients),
        "warnings": baby_warnings(safety_values),
        "aiModified": bool(version.get("ai_modified")) if version else False,
    }


def dish_dto(dish, low_sodium=False, baby_food=False, baby_stage=""):
    thumbnail_url = dish.get("thumbnail_url", "")
    data = {
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
    if low_sodium:
        data["lowSodiumPreview"] = low_sodium_preview(dish.get("id"))
    if baby_food:
        data["babyPreview"] = baby_food_preview(dish, stage=baby_stage)
    return data


def preset_filters(preset):
    if preset == "low-sodium":
        return {"category": "저염", "tag": "저염"}
    if preset == "baby-food":
        return {"category": "이유식", "tag": "이유식"}
    return {"category": "", "tag": ""}


def search():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    text = wiz.request.query("text", "")
    preset = wiz.request.query("preset", "")
    category = wiz.request.query("category", "")
    tag = wiz.request.query("tag", "")
    sort = wiz.request.query("sort", constants.RECIPE_SORTS["LATEST"])
    baby_stage = wiz.request.query("babyStage", "")
    preset_data = preset_filters(preset)
    if not category:
        category = preset_data["category"]
    if not tag:
        tag = preset_data["tag"]
    low_sodium = preset == "low-sodium"
    baby_food = preset == "baby-food"

    try:
        rows, total = struct.recipe.search_dishes(
            text=text,
            category=category,
            tag=tag,
            page=page,
            dump=dump,
            sort=sort,
        )
        items = [dish_dto(row, low_sodium=low_sodium, baby_food=baby_food, baby_stage=baby_stage) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))

    wiz.response.status(
        200,
        items=items,
        page=page,
        dump=dump,
        total=total,
        empty=(total == 0),
        filters={"text": text, "preset": preset, "category": category, "tag": tag, "sort": sort, "babyStage": baby_stage},
        categories=constants.DEFAULT_CATEGORIES,
        tags=constants.DEFAULT_TAGS,
        sorts=constants.RECIPE_SORTS,
        lowSodium={
            "enabled": low_sodium,
            "healthNotice": "저염 정보는 요리 선택을 돕기 위한 표시이며 개인 질환의 진단이나 치료 지침이 아닙니다.",
            "flavorComplements": ["레몬즙", "식초", "마늘", "양파", "버섯", "참깨", "허브"],
        },
        babyFood={
            "enabled": baby_food,
            "stages": BABY_FOOD_STAGES,
            "selectedStage": baby_stage,
            "guardianNotice": "월령, 알레르기 이력, 질식 위험은 보호자가 최종 확인하고 필요하면 전문가와 상담하세요.",
            "safetyKeywords": ["꿀", "견과류", "생식", "질식 위험", "과도한 간"],
        },
    )

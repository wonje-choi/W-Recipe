struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


STATUS_LABELS = {
    "draft": "초안",
    "crawled": "수집됨",
    "ai_parsed": "AI 요약",
    "ai_modified": "AI 개량",
    "pending_review": "검수 대기",
    "approved": "공개",
    "rejected": "반려",
    "hidden": "숨김",
}

SOURCE_TYPE_LABELS = {
    "youtube": "YouTube",
    "blog": "블로그",
    "web": "웹",
    "direct": "직접 등록",
    "ai_modified": "AI 개량",
}

DIFFICULTY_OPTIONS = [
    {"value": "easy", "label": "쉬움"},
    {"value": "normal", "label": "보통"},
    {"value": "hard", "label": "어려움"},
]


def option_items(values, labels):
    return [{"value": value, "label": labels.get(value, value)} for value in values]


def request_data():
    try:
        data = wiz.request.query()
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def options():
    try:
        struct.require_admin()
        recipe_statuses = option_items(constants.values("RECIPE_STATUSES"), STATUS_LABELS)
        source_types = option_items(constants.values("SOURCE_TYPES"), SOURCE_TYPE_LABELS)
        categories = constants.DEFAULT_CATEGORIES
        tags = constants.DEFAULT_TAGS
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(
        200,
        recipeStatuses=recipe_statuses,
        sourceTypes=source_types,
        difficultyOptions=DIFFICULTY_OPTIONS,
        categories=categories,
        tags=tags,
    )


def generate_meta():
    data = request_data()
    dish_id = data.get("dishId") or data.get("dish_id") or wiz.request.query("dishId", "")
    try:
        struct.require_admin()
        if not dish_id:
            raise Exception("AI 생성할 레시피를 먼저 저장해주세요.")
        generated = struct.ai.generate_recipe_meta(dish_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, generated=generated)


def youtube_metadata():
    data = request_data()
    dish_id = data.get("dishId") or data.get("dish_id") or wiz.request.query("dishId", "")
    try:
        struct.require_admin()
        if not dish_id:
            raise Exception("유튜브 업로드 준비 전에 레시피를 먼저 저장해주세요.")
        metadata = struct.youtube.build_upload_metadata(dish_id)
        if metadata.get("apiKeyRequired"):
            raise Exception("YouTube API Key를 관리자 AI 설정에서 먼저 등록해주세요.")
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, metadata=metadata)

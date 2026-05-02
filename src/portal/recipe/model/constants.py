class Constants:
    USER_ROLES = {
        "GUEST": "guest",
        "USER": "user",
        "ADMIN": "admin",
    }

    USER_STATUSES = {
        "ACTIVE": "active",
        "SUSPENDED": "suspended",
        "DELETED": "deleted",
        "PENDING": "pending",
    }

    SUBSCRIPTION_PLANS = {
        "FREE": "free",
        "PREMIUM": "premium",
    }

    RECIPE_STATUSES = {
        "DRAFT": "draft",
        "CRAWLED": "crawled",
        "AI_PARSED": "ai_parsed",
        "AI_MODIFIED": "ai_modified",
        "PENDING_REVIEW": "pending_review",
        "APPROVED": "approved",
        "REJECTED": "rejected",
        "HIDDEN": "hidden",
    }

    AI_STATUSES = {
        "QUEUED": "queued",
        "PROCESSING": "processing",
        "PENDING_REVIEW": "pending_review",
        "APPROVED": "approved",
        "REJECTED": "rejected",
        "FAILED": "failed",
    }

    AI_PROCESSING_STATUSES = {
        "QUEUED": "queued",
        "PROCESSING": "processing",
        "COMPLETED": "completed",
        "FAILED": "failed",
    }

    AI_PROMPT_TYPES = {
        "RECIPE_SUMMARY": "recipe_summary",
        "LOW_SODIUM": "low_sodium",
        "BABY_FOOD": "baby_food",
        "TASTE_IMPROVEMENT": "taste_improvement",
        "REVIEW_SUMMARY": "review_summary",
    }

    SOURCE_TYPES = {
        "YOUTUBE": "youtube",
        "BLOG": "blog",
        "WEB": "web",
        "DIRECT": "direct",
        "AI_MODIFIED": "ai_modified",
    }

    COMMENT_STATUSES = {
        "VISIBLE": "visible",
        "HIDDEN": "hidden",
        "DELETED": "deleted",
        "REPORTED": "reported",
    }

    EDIT_REQUEST_STATUSES = {
        "OPEN": "open",
        "IN_REVIEW": "in_review",
        "RESOLVED": "resolved",
        "REJECTED": "rejected",
    }

    EDIT_REQUEST_TYPES = {
        "ERROR": "error",
        "MEASUREMENT": "measurement_issue",
        "SOURCE": "source_issue",
        "TASTE_IMPROVEMENT": "taste_improvement",
        "OTHER": "other",
    }

    REPORT_STATUSES = {
        "OPEN": "open",
        "IN_REVIEW": "in_review",
        "ACTIONED": "actioned",
        "REJECTED": "rejected",
    }

    REPORT_TARGET_TYPES = {
        "COMMENT": "comment",
        "RECIPE_VERSION": "recipe_version",
        "RECIPE_DISH": "recipe_dish",
    }

    REPORT_REASONS = {
        "SPAM": "spam",
        "INAPPROPRIATE": "inappropriate",
        "WRONG_INFO": "wrong_info",
        "SAFETY_ISSUE": "safety_issue",
        "COPYRIGHT": "copyright",
        "OTHER": "other",
    }

    EXPERT_STATUSES = {
        "ACTIVE": "active",
        "INACTIVE": "inactive",
    }

    EXPERT_ASSIGNMENT_STATUSES = {
        "ASSIGNED": "assigned",
        "IN_REVIEW": "in_review",
        "REVIEWED": "reviewed",
    }

    EXPERT_ASSIGNMENT_TARGET_TYPES = {
        "EDIT_REQUEST": "edit_request",
        "AI_MODIFICATION": "ai_modification",
    }

    CRAWLING_STATUSES = {
        "PENDING": "pending",
        "ALLOWED": "allowed",
        "BLOCKED": "blocked",
        "COLLECTED": "collected",
        "SUMMARIZED": "summarized",
        "FAILED": "failed",
        "EXPIRED": "expired",
    }

    AI_PURPOSES = {
        "TASTIER": "tastier",
        "LOW_SODIUM": "low_sodium",
        "BABY_FOOD": "baby_food",
        "DIET": "diet",
        "HIGH_PROTEIN": "high_protein",
        "SHORTER_TIME": "shorter_time",
        "SIMPLER_INGREDIENTS": "simpler_ingredients",
        "SOFTER_TEXTURE": "softer_texture",
    }

    DIET_TYPES = {
        "LOW_SODIUM": "low_sodium",
        "BABY_FOOD": "baby_food",
        "DIET": "diet",
        "HIGH_PROTEIN": "high_protein",
        "VEGETARIAN": "vegetarian",
        "LOW_SUGAR": "low_sugar",
        "SOFT_TEXTURE": "soft_texture",
        "QUICK_COOK": "quick_cook",
    }

    RECIPE_SORTS = {
        "VIEW_COUNT": "view_count",
        "LATEST": "latest",
        "POPULAR": "popular",
        "DIFFICULTY": "difficulty",
        "COOKING_TIME": "cooking_time",
        "AI_MODIFIED": "ai_modified",
    }

    DEFAULT_CATEGORIES = [
        "일반",
        "저염",
        "이유식",
        "다이어트",
        "고단백",
        "반찬",
        "국/찌개",
        "죽/미음",
    ]

    DEFAULT_TAGS = [
        "저염",
        "이유식",
        "고단백",
        "다이어트",
        "간단요리",
        "부드러운 식감",
    ]

    BLOCKED_SOURCE_DOMAINS = []

    PUBLIC_RECIPE_STATUS = RECIPE_STATUSES["APPROVED"]
    REVIEW_REQUIRED_STATUSES = [
        RECIPE_STATUSES["CRAWLED"],
        RECIPE_STATUSES["AI_PARSED"],
        RECIPE_STATUSES["AI_MODIFIED"],
        RECIPE_STATUSES["PENDING_REVIEW"],
    ]

    SENSITIVE_PROFILE_FIELDS = [
        "allergies",
        "babyAgeMonth",
        "dislikedIngredients",
        "preferredDietTypes",
        "sodiumPreference",
        "texturePreference",
    ]

    DEFAULT_PAGE = 1
    DEFAULT_DUMP = 20
    MAX_DUMP = 100

    def values(self, name):
        group = getattr(self, name, {})
        if isinstance(group, dict):
            return list(group.values())
        return list(group)

    def has_value(self, name, value):
        return value in self.values(name)

Model = Constants()

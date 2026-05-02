import datetime

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def parse_datetime(value):
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)
    for pattern in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(str(value), pattern)
        except Exception:
            pass
    try:
        return datetime.datetime.fromisoformat(str(value))
    except Exception:
        return None


def is_today(value):
    dt = parse_datetime(value)
    if dt is None:
        return False
    return dt.date() == datetime.datetime.now().date()


def safe_count(db, **filters):
    try:
        return db.count(**filters) or 0
    except Exception:
        return 0


def safe_rows(db, page=1, dump=1000, orderby="created_at", order="DESC", **filters):
    try:
        return db.rows(page=page, dump=dump, orderby=orderby, order=order, **filters) or []
    except Exception:
        return []


def status_count(db, statuses):
    total = 0
    for status in statuses:
        total += safe_count(db, status=status)
    return total


def today_count(rows, field="created_at"):
    total = 0
    for row in rows:
        if is_today(row.get(field)):
            total += 1
    return total


def int_value(value, default=0):
    try:
        return int(value or 0)
    except Exception:
        return default


def float_value(value, default=0):
    try:
        return float(value or 0)
    except Exception:
        return default


def round_rate(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 1)


def numeric_sum(value):
    if value is None:
        return 0
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return float(value)
        except Exception:
            parsed = struct.json_loads(value, {})
            if parsed == value:
                return 0
            return numeric_sum(parsed)
    if isinstance(value, dict):
        total = 0
        for item in value.values():
            total += numeric_sum(item)
        return total
    if isinstance(value, list):
        total = 0
        for item in value:
            total += numeric_sum(item)
        return total
    return 0


def sum_field(rows, field):
    total = 0
    for row in rows:
        total += int_value(row.get(field))
    return total


def sum_cost(rows):
    total = 0
    for row in rows:
        total += float_value(row.get("cost_estimate"))
    return round(total, 4)


def sum_tokens(rows):
    total = 0
    for row in rows:
        total += numeric_sum(row.get("token_usage"))
    return int(total)


def dish_tags(dish):
    return struct.json_loads(dish.get("tags"), [])


def category_view_count(rows, category="", tag=""):
    total = 0
    for row in rows:
        tags = dish_tags(row)
        if category and row.get("category") == category:
            total += int_value(row.get("view_count"))
            continue
        if tag and tag in tags:
            total += int_value(row.get("view_count"))
    return total


def daily_visitors(recent_rows):
    users = set()
    anonymous_views = 0
    for row in recent_rows:
        if is_today(row.get("viewed_at")) == False:
            continue
        user_id = row.get("user_id", "")
        if user_id:
            users.add(user_id)
        else:
            anonymous_views += 1
    return len(users) + anonymous_views


def daily_recent_view_count(recent_rows):
    total = 0
    for row in recent_rows:
        if is_today(row.get("viewed_at")):
            total += int_value(row.get("view_count"), 1)
    return total


def row_dto(row, title_key="title"):
    return {
        "id": row.get("id"),
        "title": row.get(title_key, row.get("id", "")),
        "status": row.get("status", row.get("crawl_status", "")),
        "createdAt": date_text(row.get("created_at")),
        "updatedAt": date_text(row.get("updated_at")),
        "errorMessage": row.get("error_message", ""),
    }


def popular_recipe_dto(row):
    return {
        "id": row.get("id"),
        "name": row.get("name", ""),
        "category": row.get("category", ""),
        "tags": dish_tags(row),
        "viewCount": int_value(row.get("view_count")),
        "status": row.get("status", ""),
        "href": f"/recipes/detail/{row.get('id')}",
    }


def review_counts(dish_db, version_db, ai_modification_db, edit_request_db, report_db):
    pending_statuses = [
        constants.RECIPE_STATUSES["CRAWLED"],
        constants.RECIPE_STATUSES["AI_PARSED"],
        constants.RECIPE_STATUSES["AI_MODIFIED"],
        constants.RECIPE_STATUSES["PENDING_REVIEW"],
    ]
    dish_pending = status_count(dish_db, pending_statuses)
    version_pending = status_count(version_db, pending_statuses)
    ai_pending = safe_count(ai_modification_db, status=constants.AI_STATUSES["PENDING_REVIEW"])
    edit_open = safe_count(edit_request_db, status=constants.EDIT_REQUEST_STATUSES["OPEN"])
    report_open = safe_count(report_db, status=constants.REPORT_STATUSES["OPEN"])
    return {
        "dishPending": dish_pending,
        "versionPending": version_pending,
        "aiPending": ai_pending,
        "editOpen": edit_open,
        "reportOpen": report_open,
        "pendingTotal": dish_pending + version_pending + ai_pending + edit_open + report_open,
    }


def overview():
    try:
        dish_db = struct.db("recipe_dish")
        version_db = struct.db("recipe_version")
        user_db = struct.db("user")
        comment_db = struct.db("comment")
        edit_request_db = struct.db("recipe_edit_request")
        report_db = struct.db("report")
        ai_modification_db = struct.db("ai_recipe_modification")
        ai_log_db = struct.db("ai_processing_log")
        source_db = struct.db("crawled_source")
        recent_view_db = struct.db("recent_view")

        dish_rows = safe_rows(dish_db, dump=1000)
        version_rows = safe_rows(version_db, dump=1000)
        user_rows = safe_rows(user_db, dump=1000)
        comment_rows = safe_rows(comment_db, dump=1000)
        report_rows = safe_rows(report_db, dump=1000)
        ai_modification_rows = safe_rows(ai_modification_db, dump=1000)
        ai_log_rows = safe_rows(ai_log_db, dump=1000)
        source_rows_all = safe_rows(source_db, dump=1000)
        recent_view_rows = safe_rows(recent_view_db, dump=1000, orderby="viewed_at")

        review = review_counts(dish_db, version_db, ai_modification_db, edit_request_db, report_db)
        ai_failed = safe_count(ai_log_db, status=constants.AI_PROCESSING_STATUSES["FAILED"])
        ai_log_total = safe_count(ai_log_db)
        ai_total = safe_count(ai_modification_db)
        source_count = safe_count(source_db)
        source_errors = safe_count(source_db, crawl_status=constants.CRAWLING_STATUSES["FAILED"])
        source_failure_rate = round_rate(source_errors, source_count)

        approved = (
            safe_count(dish_db, status=constants.RECIPE_STATUSES["APPROVED"])
            + safe_count(version_db, status=constants.RECIPE_STATUSES["APPROVED"])
            + safe_count(ai_modification_db, status=constants.AI_STATUSES["APPROVED"])
        )
        rejected = (
            safe_count(dish_db, status=constants.RECIPE_STATUSES["REJECTED"])
            + safe_count(version_db, status=constants.RECIPE_STATUSES["REJECTED"])
            + safe_count(ai_modification_db, status=constants.AI_STATUSES["REJECTED"])
        )
        approval_total = approved + rejected

        daily = {
            "visitors": daily_visitors(recent_view_rows),
            "recipeViews": daily_recent_view_count(recent_view_rows),
            "signups": today_count(user_rows),
            "comments": today_count(comment_rows),
            "reports": today_count(report_rows),
            "aiRequests": today_count(ai_modification_rows),
        }

        total_recipe_views = sum_field(dish_rows, "view_count")
        low_sodium_views = category_view_count(dish_rows, category="저염", tag="저염")
        baby_food_views = category_view_count(dish_rows, category="이유식", tag="이유식")
        popular_rows = safe_rows(dish_db, page=1, dump=5, orderby="view_count", order="DESC", status=constants.RECIPE_STATUSES["APPROVED"])
        recent_sources = safe_rows(source_db, page=1, dump=5, orderby="created_at", order="DESC")
        failed_logs = safe_rows(ai_log_db, status=constants.AI_PROCESSING_STATUSES["FAILED"], page=1, dump=5, orderby="created_at", order="DESC")

        metrics = [
            {"label": "일간 방문자", "value": daily["visitors"], "tone": "sky", "href": "/dashboard"},
            {"label": "레시피 조회", "value": total_recipe_views, "tone": "emerald", "href": "/admin/recipes"},
            {"label": "검수 대기", "value": review["pendingTotal"], "tone": "amber", "href": "/admin/recipes?status=pending_review"},
            {"label": "AI 요청", "value": ai_total, "tone": "indigo", "href": "/admin/ai"},
            {"label": "신고/수정", "value": review["reportOpen"] + review["editOpen"], "tone": "violet", "href": "/admin/feedback"},
            {"label": "가입 사용자", "value": safe_count(user_db), "tone": "zinc", "href": "/admin/users"},
        ]
        review_queue = [
            {"label": "레시피 Dish 검수", "count": review["dishPending"], "href": "/admin/recipes?status=pending_review"},
            {"label": "레시피 Version 검수", "count": review["versionPending"], "href": "/admin/recipes?tab=versions"},
            {"label": "AI 결과 검수", "count": review["aiPending"], "href": "/admin/ai?status=pending_review"},
            {"label": "수정 요청 처리", "count": review["editOpen"], "href": "/admin/feedback?tab=edit-requests"},
            {"label": "신고 처리", "count": review["reportOpen"], "href": "/admin/feedback?tab=reports"},
        ]
        operations = {
            "daily": daily,
            "reviewCounts": review,
            "popularRecipes": [popular_recipe_dto(row) for row in popular_rows],
            "recentSources": [row_dto(row) for row in recent_sources],
            "failedLogs": [row_dto(row, title_key="request_type") for row in failed_logs],
            "sourceCount": source_count,
            "sourceErrors": source_errors,
            "sourceFailureRate": source_failure_rate,
            "totalRecipeViews": total_recipe_views,
            "lowSodiumViews": low_sodium_views,
            "babyFoodViews": baby_food_views,
            "comments": safe_count(comment_db),
            "todayComments": daily["comments"],
            "reports": safe_count(report_db),
            "todayReports": daily["reports"],
            "signups": safe_count(user_db),
            "todaySignups": daily["signups"],
            "aiRequests": ai_total,
            "aiTodayRequests": daily["aiRequests"],
            "aiFailed": ai_failed,
            "aiFailureRate": round_rate(ai_failed, ai_log_total),
            "tokenTotal": sum_tokens(ai_log_rows),
            "costTotal": sum_cost(ai_log_rows),
            "approvalRate": round_rate(approved, approval_total),
            "rejected": rejected,
            "approved": approved,
            "measurementNote": "일간 방문자와 일간 조회수는 로그인 사용자의 recent_view 활동 기준으로 집계합니다.",
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, metrics=metrics, reviewQueue=review_queue, operations=operations)

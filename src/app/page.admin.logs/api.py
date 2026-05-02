import datetime
import json
import re
from urllib.parse import urlparse, urlunparse

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

LOG_TYPE_LABELS = {
    "admin_action": "관리자 작업",
    "login_failure": "로그인 실패",
    "ai_failure": "AI 실패",
    "crawling_failure": "크롤링 실패",
    "api_error": "API 오류",
    "permission_error": "권한 오류",
}

SEVERITY_LABELS = {
    "info": "정보",
    "warning": "주의",
    "error": "오류",
    "security": "보안",
}

SENSITIVE_KEYS = set([
    "password",
    "passwordHash",
    "password_hash",
    "token",
    "session",
    "apiKey",
    "api_key",
    "rawContent",
    "raw_content",
    "allergies",
    "medicalNotes",
    "medical_notes",
])


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


def parse_datetime(value):
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)
    if not value:
        return None
    text = str(value)
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.datetime.strptime(text[:19 if " " in fmt else 10], fmt)
        except Exception:
            pass
    return None


def option_items(values, labels):
    return [{"value": value, "label": labels.get(value, value)} for value in values]


def mask_email(value):
    value = value or ""
    if "@" not in value:
        return value
    name, domain = value.split("@", 1)
    if len(name) <= 2:
        masked = name[:1] + "*"
    else:
        masked = name[:2] + "***"
    return masked + "@" + domain


def mask_ip(value):
    value = value or ""
    parts = value.split(".")
    if len(parts) == 4:
        return ".".join(parts[:3] + ["0"])
    return value


def strip_url(value):
    if not value:
        return ""
    try:
        parsed = urlparse(value)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
    except Exception:
        return value


def trim_text(value, limit=600):
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", lambda match: mask_email(match.group(0)), text)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def mask_value(key, value):
    if key in SENSITIVE_KEYS:
        if isinstance(value, list):
            return "masked:%d_items" % len(value)
        return "masked" if value else value
    if isinstance(value, dict):
        return {child_key: mask_value(child_key, child_value) for child_key, child_value in value.items()}
    if isinstance(value, list):
        return [mask_value(key, item) for item in value[:20]]
    if isinstance(value, str):
        return trim_text(value)
    return value


def safe_json(value):
    if value in [None, ""]:
        return {}
    if isinstance(value, (dict, list)):
        data = value
    else:
        try:
            data = json.loads(value)
        except Exception:
            return trim_text(value)
    if isinstance(data, dict):
        return {key: mask_value(key, item) for key, item in data.items()}
    if isinstance(data, list):
        return [mask_value("items", item) for item in data[:20]]
    return data


def pretty(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    return trim_text(value)


def user_dto(user_id):
    if not user_id:
        return {"id": "", "email": "", "nickname": ""}
    user = struct.user.get(user_id=user_id) or {}
    return {
        "id": user.get("id", user_id),
        "email": mask_email(user.get("email", "")),
        "nickname": user.get("nickname", ""),
        "role": user.get("role", ""),
        "status": user.get("status", ""),
    }


def event_base(event_type, severity, title, occurred_at):
    return {
        "id": "",
        "type": event_type,
        "typeLabel": LOG_TYPE_LABELS.get(event_type, event_type),
        "severity": severity,
        "severityLabel": SEVERITY_LABELS.get(severity, severity),
        "title": title,
        "message": "",
        "actor": {},
        "targetType": "",
        "targetId": "",
        "ipAddress": "",
        "userAgent": "",
        "meta": {},
        "metaText": "",
        "occurredAt": date_text(occurred_at),
        "sortAt": date_text(occurred_at),
    }


def admin_action_event(row):
    event = event_base("admin_action", "info", row.get("action_type", "관리자 작업"), row.get("created_at"))
    before_value = safe_json(row.get("before_value", "{}"))
    after_value = safe_json(row.get("after_value", "{}"))
    event.update({
        "id": row.get("id"),
        "actor": user_dto(row.get("admin_user_id", "")),
        "targetType": row.get("target_type", ""),
        "targetId": row.get("target_id", ""),
        "ipAddress": mask_ip(row.get("ip_address", "")),
        "userAgent": trim_text(row.get("user_agent", ""), 160),
        "message": "%s 대상 %s" % (row.get("target_type", ""), row.get("target_id", "")),
        "meta": {"before": before_value, "after": after_value},
        "metaText": pretty({"before": before_value, "after": after_value}),
    })
    return event


def login_failure_event(user):
    failed_count = int(user.get("login_failed_count") or 0)
    locked_until = date_text(user.get("locked_until"))
    severity = "security" if locked_until else "warning"
    event = event_base("login_failure", severity, "로그인 실패", user.get("updated_at"))
    event.update({
        "id": user.get("id"),
        "actor": user_dto(user.get("id", "")),
        "targetType": "user",
        "targetId": user.get("id", ""),
        "message": "실패 %d회%s" % (failed_count, " · 잠금 " + locked_until if locked_until else ""),
        "meta": {"failedCount": failed_count, "lockedUntil": locked_until},
        "metaText": pretty({"failedCount": failed_count, "lockedUntil": locked_until}),
    })
    return event


def ai_failure_event(row):
    event = event_base("ai_failure", "error", row.get("request_type", "AI 처리 실패"), row.get("created_at"))
    meta = {
        "promptVersion": row.get("prompt_version", ""),
        "inputSummary": trim_text(row.get("input_summary", "")),
        "outputSummary": trim_text(row.get("output_summary", "")),
        "errorMessage": trim_text(row.get("error_message", "")),
        "durationMs": int(row.get("duration_ms") or 0),
    }
    event.update({
        "id": row.get("id"),
        "targetType": "ai_processing_log",
        "targetId": row.get("target_id", ""),
        "message": trim_text(row.get("error_message", "")) or "AI 처리 실패",
        "meta": meta,
        "metaText": pretty(meta),
    })
    return event


def crawling_failure_event(row):
    status = row.get("crawl_status", "")
    severity = "error" if status == constants.CRAWLING_STATUSES["FAILED"] else "warning"
    event = event_base("crawling_failure", severity, row.get("title", "외부 자료 수집 문제"), row.get("updated_at") or row.get("created_at"))
    meta = {
        "sourceType": row.get("source_type", ""),
        "sourceUrl": strip_url(row.get("source_url", "")),
        "crawlStatus": status,
        "retryCount": int(row.get("retry_count") or 0),
        "errorMessage": trim_text(row.get("error_message", "")),
    }
    event.update({
        "id": row.get("id"),
        "targetType": "crawled_source",
        "targetId": row.get("id", ""),
        "message": trim_text(row.get("error_message", "")) or status,
        "meta": meta,
        "metaText": pretty(meta),
    })
    return event


def collect_admin_actions():
    rows = struct.admin_log.log_db.rows(page=1, dump=500, orderby="created_at", order="DESC")
    return [admin_action_event(row) for row in rows]


def collect_login_failures():
    rows = struct.user.user_db.rows(page=1, dump=500, orderby="updated_at", order="DESC")
    events = []
    for row in rows:
        if int(row.get("login_failed_count") or 0) > 0:
            events.append(login_failure_event(row))
    return events


def collect_ai_failures():
    rows = struct.ai.log_db.rows(status=constants.AI_PROCESSING_STATUSES["FAILED"], page=1, dump=500, orderby="created_at", order="DESC")
    return [ai_failure_event(row) for row in rows]


def collect_crawling_failures():
    rows = []
    for status in [constants.CRAWLING_STATUSES["FAILED"], constants.CRAWLING_STATUSES["BLOCKED"], constants.CRAWLING_STATUSES["EXPIRED"]]:
        rows += struct.source.source_db.rows(crawl_status=status, page=1, dump=300, orderby="updated_at", order="DESC")
    return [crawling_failure_event(row) for row in rows]


def collect_events(log_type=""):
    events = []
    if not log_type or log_type == "admin_action":
        events += collect_admin_actions()
    if not log_type or log_type == "login_failure":
        events += collect_login_failures()
    if not log_type or log_type == "ai_failure":
        events += collect_ai_failures()
    if not log_type or log_type == "crawling_failure":
        events += collect_crawling_failures()
    return events


def event_matches(event, filters):
    if filters.get("severity") and event.get("severity") != filters.get("severity"):
        return False
    if filters.get("adminUserId") and event.get("actor", {}).get("id") != filters.get("adminUserId"):
        return False
    if filters.get("targetType") and event.get("targetType") != filters.get("targetType"):
        return False
    occurred = parse_datetime(event.get("occurredAt"))
    from_date = parse_datetime(filters.get("fromDate"))
    to_date = parse_datetime(filters.get("toDate"))
    if from_date and (occurred is None or occurred < from_date):
        return False
    if to_date:
        to_date = to_date + datetime.timedelta(days=1)
        if occurred is None or occurred >= to_date:
            return False
    text = (filters.get("text") or "").lower()
    if text:
        haystack = " ".join([
            event.get("id", ""),
            event.get("typeLabel", ""),
            event.get("severityLabel", ""),
            event.get("title", ""),
            event.get("message", ""),
            event.get("targetType", ""),
            event.get("targetId", ""),
            event.get("actor", {}).get("email", ""),
            event.get("actor", {}).get("nickname", ""),
            event.get("metaText", ""),
        ]).lower()
        if text not in haystack:
            return False
    return True


def paginate(events, page, dump):
    total = len(events)
    start = max(0, (page - 1) * dump)
    return events[start:start + dump], total


def summary_counts():
    return {
        "admin_action": struct.admin_log.log_db.count() or 0,
        "login_failure": len(collect_login_failures()),
        "ai_failure": struct.ai.log_db.count(status=constants.AI_PROCESSING_STATUSES["FAILED"]) or 0,
        "crawling_failure": len(collect_crawling_failures()),
        "api_error": 0,
        "permission_error": 0,
    }


def options():
    try:
        struct.require_admin()
        data = {
            "logTypes": option_items(list(LOG_TYPE_LABELS.keys()), LOG_TYPE_LABELS),
            "severities": option_items(list(SEVERITY_LABELS.keys()), SEVERITY_LABELS),
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **data)


def logs():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", 20))
    filters = {
        "type": wiz.request.query("type", ""),
        "severity": wiz.request.query("severity", ""),
        "adminUserId": wiz.request.query("adminUserId", wiz.request.query("admin_user_id", "")),
        "targetType": wiz.request.query("targetType", wiz.request.query("target_type", "")),
        "fromDate": wiz.request.query("fromDate", wiz.request.query("from_date", "")),
        "toDate": wiz.request.query("toDate", wiz.request.query("to_date", "")),
        "text": wiz.request.query("text", ""),
    }
    try:
        struct.require_admin()
        events = collect_events(filters.get("type"))
        events = [event for event in events if event_matches(event, filters)]
        events.sort(key=lambda item: item.get("sortAt", ""), reverse=True)
        items, total = paginate(events, page, dump)
        summary = summary_counts()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, summary=summary, empty=(total == 0))

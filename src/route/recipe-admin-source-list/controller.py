import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default

def to_bool(value, default=False):
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

def source_dto(source):
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

def source_payload(data):
    source_url = struct.source.normalize_url(data.get("sourceUrl") or data.get("source_url") or "")
    source_type = data.get("sourceType") or data.get("source_type") or struct.source.detect_source_type(source_url)
    blocked = struct.source.is_blocked_domain(source_url)
    payload = {
        "source_url": source_url,
        "source_type": source_type,
        "title": data.get("title", ""),
        "author": data.get("author") or data.get("channel") or "",
        "thumbnail_url": data.get("thumbnailUrl") or data.get("thumbnail_url") or "",
        "collected_text_summary": data.get("summary") or data.get("description") or data.get("collectedTextSummary") or "",
        "raw_content_storage_policy": "summary_only",
        "robots_allowed": False if blocked else to_bool(data.get("robotsAllowed") or data.get("robots_allowed"), False),
        "crawl_status": constants.CRAWLING_STATUSES["BLOCKED"] if blocked else data.get("crawlStatus") or data.get("crawl_status") or constants.CRAWLING_STATUSES["PENDING"],
        "error_message": "Blocked domain" if blocked else data.get("errorMessage") or data.get("error_message") or "",
    }
    return payload

method = wiz.request.method()
if method == "GET":
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = clamp_dump(wiz.request.query("dump", constants.DEFAULT_DUMP))
    status = wiz.request.query("status", "")
    source_type = wiz.request.query("sourceType", wiz.request.query("source_type", ""))
    try:
        rows, total = struct.source.rows(status=status, source_type=source_type, page=page, dump=dump)
        items = [source_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, empty=(total == 0))

if method == "POST":
    try:
        data = request_data()
        payload = source_payload(data)
        if not payload.get("source_url"):
            raise Exception("수집 대상 URL을 입력해주세요.")
        existing = struct.source.get_by_url(payload["source_url"])
        if existing:
            item = source_dto(existing)
            item["duplicate"] = True
        else:
            source_id = struct.source.create(payload)
            source = struct.source.source_db.get(id=source_id)
            item = source_dto(source)
            item["duplicate"] = False
            struct.admin_log.create("source_create", "crawled_source", source_id, {}, source)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201 if item.get("duplicate") == False else 200, source=item)

wiz.response.status(405, message="Method not allowed")

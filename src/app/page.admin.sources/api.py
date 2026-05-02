import datetime
import csv
import json
import urllib.parse
import urllib.request
import urllib.robotparser

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")

SOURCE_TYPE_LABELS = {
    "youtube": "YouTube",
    "blog": "블로그",
    "web": "웹",
    "direct": "직접 등록",
    "ai_modified": "AI 개량",
}

STATUS_LABELS = {
    "pending": "대기",
    "allowed": "허용",
    "blocked": "차단",
    "collected": "수집 완료",
    "summarized": "요약 완료",
    "failed": "실패",
    "expired": "만료",
}


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


def flag(label, active, tone="zinc"):
    return {"label": label, "active": bool(active), "tone": tone}


def source_dto(source, duplicate=False):
    status = source.get("crawl_status", "")
    source_url = source.get("source_url", "")
    summary_ready = bool(source.get("collected_text_summary")) or status == constants.CRAWLING_STATUSES["SUMMARIZED"]
    admin_reviewed = status not in [constants.CRAWLING_STATUSES["PENDING"]] or bool(source.get("last_checked_at"))
    link_expired = status == constants.CRAWLING_STATUSES["EXPIRED"]
    duplicate_of = source.get("duplicate_of", "")
    source_type = source.get("source_type", "")
    return {
        "id": source.get("id"),
        "sourceType": source_type,
        "sourceTypeLabel": SOURCE_TYPE_LABELS.get(source_type, source_type),
        "sourceUrl": source_url,
        "sourceUrlHash": source.get("source_url_hash", ""),
        "hostname": struct.source.hostname(source_url) if source_url else "",
        "title": source.get("title", ""),
        "author": source.get("author", ""),
        "thumbnailUrl": source.get("thumbnail_url", ""),
        "collectedTextSummary": source.get("collected_text_summary", ""),
        "rawContent": source.get("raw_content", ""),
        "rawContentStoragePolicy": source.get("raw_content_storage_policy", "summary_only"),
        "crawlStatus": status,
        "crawlStatusLabel": STATUS_LABELS.get(status, status),
        "robotsAllowed": bool(source.get("robots_allowed")),
        "duplicateOf": duplicate_of,
        "duplicate": bool(duplicate or duplicate_of),
        "summaryReady": summary_ready,
        "adminReviewed": admin_reviewed,
        "linkExpired": link_expired,
        "collectedAt": date_text(source.get("collected_at")),
        "retryCount": int(source.get("retry_count") or 0),
        "lastCheckedAt": date_text(source.get("last_checked_at")),
        "errorMessage": source.get("error_message", ""),
        "createdAt": date_text(source.get("created_at")),
        "updatedAt": date_text(source.get("updated_at")),
        "flags": [
            flag("수집 허용", bool(source.get("robots_allowed")), "emerald"),
            flag("중복 자료", bool(duplicate or duplicate_of), "amber"),
            flag("요약 완료", summary_ready, "sky"),
            flag("관리자 검수", admin_reviewed, "violet"),
            flag("링크 만료", link_expired, "rose"),
        ],
    }


def robots_allowed(url):
    if struct.source.is_blocked_domain(url):
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        request = urllib.request.Request(robots_url, headers={"User-Agent": "RecipeTasteOptimizer/1.0"})
        with urllib.request.urlopen(request, timeout=3) as response:
            content = response.read(500000).decode("utf-8", errors="ignore")
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(content.splitlines())
        return parser.can_fetch("*", url)
    except urllib.error.HTTPError as error:
        return error.code not in [401, 403]
    except Exception:
        return True


def parse_batch_urls(text):
    values = []
    seen = set()
    for line in str(text or "").replace("\r", "\n").split("\n"):
        if not line.strip():
            continue
        for row in csv.reader([line]):
            for cell in row:
                url = struct.source.normalize_url(cell)
                if not url or url in seen:
                    continue
                seen.add(url)
                values.append(url)
    return values


def pick(data, *keys):
    for key in keys:
        if key in data:
            return data.get(key)
    return None


def source_payload(data, for_update=False):
    payload = {}
    source_url_value = pick(data, "sourceUrl", "source_url")
    if source_url_value is not None:
        source_url = struct.source.normalize_url(source_url_value)
        payload["source_url"] = source_url
        payload["source_url_hash"] = struct.source.url_hash(source_url)
    source_type_value = pick(data, "sourceType", "source_type")
    if source_type_value is not None:
        payload["source_type"] = source_type_value
    elif not for_update:
        payload["source_type"] = struct.source.detect_source_type(payload.get("source_url", ""))
    mapping = {
        "title": "title",
        "author": "author",
        "channel": "author",
        "thumbnailUrl": "thumbnail_url",
        "thumbnail_url": "thumbnail_url",
        "summary": "collected_text_summary",
        "description": "collected_text_summary",
        "collectedTextSummary": "collected_text_summary",
        "rawContent": "raw_content",
        "raw_content": "raw_content",
        "errorMessage": "error_message",
        "error_message": "error_message",
        "crawlStatus": "crawl_status",
        "crawl_status": "crawl_status",
    }
    for source_key, target_key in mapping.items():
        if source_key in data:
            payload[target_key] = data.get(source_key) or ""
    robots_value = pick(data, "robotsAllowed", "robots_allowed")
    if robots_value is not None:
        payload["robots_allowed"] = to_bool(robots_value, False)
    if not for_update:
        payload.setdefault("raw_content_storage_policy", "summary_only")
        payload.setdefault("robots_allowed", False)
        payload.setdefault("crawl_status", constants.CRAWLING_STATUSES["PENDING"])
        payload.setdefault("error_message", "")
    if payload.get("source_url") and struct.source.is_blocked_domain(payload.get("source_url")):
        payload["robots_allowed"] = False
        payload["crawl_status"] = constants.CRAWLING_STATUSES["BLOCKED"]
        payload["error_message"] = "Blocked domain"
    if payload.get("raw_content"):
        payload["raw_content_storage_policy"] = "full"
    elif "raw_content" in payload:
        payload["raw_content_storage_policy"] = "summary_only"
    elif payload.get("collected_text_summary"):
        payload["raw_content_storage_policy"] = "summary_only"
    return payload


def filtered_sources(page, dump, status="", source_type="", text=""):
    filters = {}
    if status:
        filters["crawl_status"] = status
    if source_type:
        filters["source_type"] = source_type
    if text:
        all_rows = struct.source.source_db.rows(page=1, dump=500, orderby="created_at", order="DESC", **filters)
        needle = text.lower()
        rows = []
        for row in all_rows:
            haystack = " ".join([
                row.get("source_url", ""),
                row.get("title", ""),
                row.get("author", ""),
                row.get("collected_text_summary", ""),
                row.get("error_message", ""),
            ]).lower()
            if needle in haystack:
                rows.append(row)
        total = len(rows)
        start = (page - 1) * dump
        return rows[start:start + dump], total
    rows = struct.source.source_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
    total = struct.source.source_db.count(**filters) or 0
    return rows, total


def status_summary():
    result = []
    for item in option_items(constants.values("CRAWLING_STATUSES"), STATUS_LABELS):
        result.append({
            "value": item["value"],
            "label": item["label"],
            "count": struct.source.source_db.count(crawl_status=item["value"]) or 0,
        })
    return result


def retry_summary():
    failed = struct.source.source_db.count(crawl_status=constants.CRAWLING_STATUSES["FAILED"]) or 0
    retryable = len(struct.source.retry_failed(limit=500))
    return {"failed": failed, "retryable": retryable}


def options():
    try:
        struct.require_admin()
        source_types = option_items(constants.values("SOURCE_TYPES"), SOURCE_TYPE_LABELS)
        crawl_statuses = option_items(constants.values("CRAWLING_STATUSES"), STATUS_LABELS)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, sourceTypes=source_types, crawlStatuses=crawl_statuses)


def sources():
    page = to_int(wiz.request.query("page", constants.DEFAULT_PAGE), constants.DEFAULT_PAGE)
    dump = to_int(wiz.request.query("dump", 12), 12)
    status = wiz.request.query("status", "")
    source_type = wiz.request.query("sourceType", wiz.request.query("source_type", ""))
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = filtered_sources(page, dump, status=status, source_type=source_type, text=text)
        items = [source_dto(row) for row in rows]
        summary = status_summary()
        retry = retry_summary()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=items, page=page, dump=dump, total=total, statusSummary=summary, retrySummary=retry, empty=(total == 0))


def save_source():
    data = request_data()
    source_id = data.get("id", "")
    try:
        struct.require_admin()
        if source_id:
            before = struct.source.source_db.get(id=source_id)
            if before is None:
                raise Exception("출처를 찾을 수 없습니다.")
            payload = source_payload(data, for_update=True)
            if "source_url_hash" in payload:
                existing = struct.source.source_db.get(source_url_hash=payload["source_url_hash"])
                if existing and existing.get("id") != source_id:
                    raise Exception("이미 등록된 URL입니다.")
            struct.source.update(source_id, payload)
            source = struct.source.source_db.get(id=source_id)
            struct.admin_log.create("source_update", "crawled_source", source_id, before, source)
            duplicate = False
            code = 200
        else:
            payload = source_payload(data, for_update=False)
            if not payload.get("source_url"):
                raise Exception("수집 대상 URL을 입력해주세요.")
            existing = struct.source.get_by_url(payload["source_url"])
            if existing:
                source = existing
                duplicate = True
                code = 200
            else:
                source_id = struct.source.create(payload)
                source = struct.source.source_db.get(id=source_id)
                struct.admin_log.create("source_create", "crawled_source", source_id, {}, source)
                duplicate = False
                code = 201
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(code, source=source_dto(source, duplicate=duplicate))


def batch_import():
    data = request_data()
    try:
        struct.require_admin()
        urls = parse_batch_urls(data.get("urls") or data.get("text") or "")
        if len(urls) > 50:
            raise Exception("배치 등록은 요청당 최대 50개 URL까지만 가능합니다.")
        results = []
        created = 0
        duplicates = 0
        blocked = 0
        errors = 0
        for url in urls:
            try:
                normalized = struct.source.validate_url(url, "배치 URL")
                existing = struct.source.get_by_url(normalized)
                allowed = robots_allowed(normalized)
                if existing:
                    duplicates += 1
                    results.append({"url": normalized, "status": "duplicate", "source": source_dto(existing, duplicate=True)})
                    continue
                payload = source_payload({
                    "sourceUrl": normalized,
                    "sourceType": struct.source.detect_source_type(normalized),
                    "robotsAllowed": allowed,
                    "crawlStatus": constants.CRAWLING_STATUSES["PENDING"] if allowed else constants.CRAWLING_STATUSES["BLOCKED"],
                    "errorMessage": "" if allowed else "robots.txt disallowed",
                }, for_update=False)
                source_id = struct.source.create(payload)
                source = struct.source.source_db.get(id=source_id)
                struct.admin_log.create("source_batch_create", "crawled_source", source_id, {}, source)
                if allowed:
                    created += 1
                    result_status = "created"
                else:
                    blocked += 1
                    result_status = "blocked"
                results.append({"url": normalized, "status": result_status, "source": source_dto(source)})
            except Exception as item_error:
                errors += 1
                results.append({"url": url, "status": "error", "message": str(item_error)})
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, created=created, duplicates=duplicates, blocked=blocked, errors=errors, total=len(urls), results=results)


def status_action():
    data = request_data()
    source_id = data.get("id", "")
    try:
        struct.require_admin()
        before = struct.source.source_db.get(id=source_id)
        if before is None:
            raise Exception("출처를 찾을 수 없습니다.")
        payload = {}
        crawl_status = data.get("crawlStatus") or data.get("crawl_status") or ""
        if crawl_status:
            payload["crawl_status"] = crawl_status
        if "robotsAllowed" in data or "robots_allowed" in data:
            payload["robots_allowed"] = to_bool(pick(data, "robotsAllowed", "robots_allowed"), False)
        if "errorMessage" in data or "error_message" in data:
            payload["error_message"] = pick(data, "errorMessage", "error_message") or ""
        payload["last_checked_at"] = datetime.datetime.now()
        struct.source.update(source_id, payload)
        source = struct.source.source_db.get(id=source_id)
        struct.admin_log.create("source_status_update", "crawled_source", source_id, before, source)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, source=source_dto(source))


def retry_source():
    data = request_data()
    source_id = data.get("id", "")
    try:
        struct.require_admin()
        before = struct.source.source_db.get(id=source_id)
        if before is None:
            raise Exception("출처를 찾을 수 없습니다.")
        retry_count = int(before.get("retry_count") or 0) + 1
        struct.source.update(source_id, {
            "crawl_status": constants.CRAWLING_STATUSES["PENDING"],
            "retry_count": retry_count,
            "last_checked_at": datetime.datetime.now(),
            "error_message": "",
        })
        source = struct.source.source_db.get(id=source_id)
        struct.admin_log.create("source_retry", "crawled_source", source_id, before, source)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, source=source_dto(source))


def retry_failed():
    try:
        struct.require_admin()
        rows = struct.source.retry_failed(limit=50)
        items = []
        for row in rows:
            source_id = row.get("id")
            before = dict(row)
            retry_count = int(row.get("retry_count") or 0) + 1
            struct.source.update(source_id, {
                "crawl_status": constants.CRAWLING_STATUSES["PENDING"],
                "retry_count": retry_count,
                "last_checked_at": datetime.datetime.now(),
                "error_message": "",
            })
            source = struct.source.source_db.get(id=source_id)
            struct.admin_log.create("source_retry_failed", "crawled_source", source_id, before, source)
            items.append(source_dto(source))
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, retried=len(items), items=items, retrySummary=retry_summary())


def expire_source():
    data = request_data()
    source_id = data.get("id", "")
    try:
        struct.require_admin()
        before = struct.source.source_db.get(id=source_id)
        if before is None:
            raise Exception("출처를 찾을 수 없습니다.")
        struct.source.update(source_id, {"crawl_status": constants.CRAWLING_STATUSES["EXPIRED"]})
        source = struct.source.source_db.get(id=source_id)
        struct.admin_log.create("source_expire", "crawled_source", source_id, before, source)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, source=source_dto(source))

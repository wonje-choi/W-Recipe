import hashlib
import ipaddress
import re
from urllib.parse import urlparse

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = set(["http", "https"])
BLOCKED_HOSTNAMES = set(["localhost", "localhost.localdomain"])
SCHEME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")

class Source:
    def __init__(self, core):
        self.core = core
        self.source_db = core.db("crawled_source")
        self.constants = core.constants

    def normalize_url(self, url):
        normalized = (url or "").strip()
        if normalized.startswith("//"):
            normalized = "https:" + normalized
        elif normalized and "://" not in normalized and SCHEME_PATTERN.match(normalized) is None:
            normalized = "https://" + normalized
        return normalized

    def validate_url(self, url, field_name="URL"):
        normalized = self.normalize_url(url)
        if not normalized:
            raise Exception(f"{field_name}을 입력해주세요.")
        if len(normalized) > MAX_URL_LENGTH:
            raise Exception(f"{field_name}은 {MAX_URL_LENGTH}자 이하로 입력해주세요.")
        if any(item.isspace() for item in normalized):
            raise Exception(f"{field_name}에 공백을 포함할 수 없습니다.")
        parsed = urlparse(normalized)
        scheme = (parsed.scheme or "").lower()
        if scheme not in ALLOWED_SCHEMES:
            raise Exception(f"{field_name}은 http 또는 https만 허용됩니다.")
        if not parsed.netloc or not parsed.hostname:
            raise Exception(f"{field_name} 형식이 올바르지 않습니다.")
        if parsed.username or parsed.password:
            raise Exception(f"{field_name}에 사용자 정보를 포함할 수 없습니다.")
        hostname = (parsed.hostname or "").lower().rstrip(".")
        if hostname in BLOCKED_HOSTNAMES or hostname.endswith(".localhost"):
            raise Exception(f"{field_name}에 로컬 주소를 사용할 수 없습니다.")
        try:
            address = ipaddress.ip_address(hostname)
            if address.is_private or address.is_loopback or address.is_link_local or address.is_multicast or address.is_reserved or address.is_unspecified:
                raise Exception(f"{field_name}에 내부망 또는 특수 IP를 사용할 수 없습니다.")
        except ValueError:
            pass
        return normalized

    def validate_optional_url(self, url, field_name="URL"):
        normalized = self.normalize_url(url)
        if not normalized:
            return ""
        return self.validate_url(normalized, field_name=field_name)

    def hostname(self, url):
        parsed = urlparse(self.normalize_url(url))
        return (parsed.hostname or "").lower()

    def detect_source_type(self, url):
        hostname = self.hostname(url)
        if "youtube.com" in hostname or "youtu.be" in hostname:
            return self.constants.SOURCE_TYPES["YOUTUBE"]
        if "blog." in hostname or "tistory.com" in hostname or "medium.com" in hostname:
            return self.constants.SOURCE_TYPES["BLOG"]
        return self.constants.SOURCE_TYPES["WEB"]

    def is_blocked_domain(self, url):
        hostname = self.hostname(url)
        for domain in self.constants.BLOCKED_SOURCE_DOMAINS:
            if hostname == domain or hostname.endswith("." + domain):
                return True
        return False

    def url_hash(self, url):
        normalized = self.validate_url(url)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get_by_url(self, url):
        return self.source_db.get(source_url_hash=self.url_hash(url))

    def create(self, data):
        now = self.core.now()
        data = dict(data or {})
        data.setdefault("source_type", self.constants.SOURCE_TYPES["WEB"])
        data.setdefault("crawl_status", self.constants.CRAWLING_STATUSES["PENDING"])
        data.setdefault("raw_content_storage_policy", "summary_only")
        data.setdefault("robots_allowed", False)
        data.setdefault("retry_count", 0)
        data["source_url"] = self.validate_url(data.get("source_url"), "수집 대상 URL")
        data["source_url_hash"] = data.get("source_url_hash") or self.url_hash(data.get("source_url"))
        data["raw_content"] = data.get("raw_content") or ""
        if data.get("raw_content"):
            data["raw_content_storage_policy"] = "full"
        if data.get("thumbnail_url"):
            data["thumbnail_url"] = self.validate_optional_url(data.get("thumbnail_url"), "썸네일 URL")
        data["created_at"] = now
        data["updated_at"] = now
        existing = self.source_db.get(source_url_hash=data["source_url_hash"])
        if existing:
            data["duplicate_of"] = existing.get("id", "")
        return self.source_db.insert(data)

    def update(self, source_id, data):
        data = dict(data or {})
        if "source_url" in data:
            data["source_url"] = self.validate_url(data.get("source_url"), "수집 대상 URL")
            data["source_url_hash"] = self.url_hash(data.get("source_url"))
        if data.get("thumbnail_url"):
            data["thumbnail_url"] = self.validate_optional_url(data.get("thumbnail_url"), "썸네일 URL")
        if "raw_content" in data:
            data["raw_content"] = data.get("raw_content") or ""
            data["raw_content_storage_policy"] = "full" if data["raw_content"] else "summary_only"
        data["updated_at"] = self.core.now()
        self.source_db.update(data, id=source_id)

    def mark_collected(self, source_id, summary=""):
        self.update(source_id, {
            "crawl_status": self.constants.CRAWLING_STATUSES["COLLECTED"],
            "collected_text_summary": summary,
            "collected_at": self.core.now(),
            "error_message": "",
        })

    def mark_failed(self, source_id, error_message):
        source = self.source_db.get(id=source_id) or {}
        retry_count = int(source.get("retry_count") or 0) + 1
        self.update(source_id, {
            "crawl_status": self.constants.CRAWLING_STATUSES["FAILED"],
            "retry_count": retry_count,
            "last_checked_at": self.core.now(),
            "error_message": error_message,
        })
        return retry_count

    def rows(self, status="", source_type="", page=1, dump=20):
        filters = {}
        if status:
            filters["crawl_status"] = status
        if source_type:
            filters["source_type"] = source_type
        rows = self.source_db.rows(page=page, dump=dump, orderby="created_at", order="DESC", **filters)
        total = self.source_db.count(**filters) or 0
        return rows, total

    def retry_failed(self, limit=50):
        rows = self.source_db.rows(
            crawl_status=self.constants.CRAWLING_STATUSES["FAILED"],
            page=1,
            dump=500,
            orderby="updated_at",
            order="ASC",
        )
        retryable = []
        for row in rows:
            if int(row.get("retry_count") or 0) < 3:
                retryable.append(row)
            if len(retryable) >= limit:
                break
        return retryable

Model = Source

import csv
import datetime
import hashlib
import io
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.robotparser

REQUEST_STATUSES = ["queued", "running", "done", "failed"]
RESULT_STATUSES = ["stored", "deleted"]
TARGET_TYPES = ["web_url", "web_keyword", "youtube_video", "youtube_channel", "youtube_keyword"]
WEB_TYPES = set(["web_url", "web_keyword"])
YOUTUBE_TYPES = set(["youtube_video", "youtube_channel", "youtube_keyword"])
MAX_ITEMS_LIMIT = 50
USER_AGENT = "RecipeTasteCollector/1.0"

class Collector:
    def __init__(self, core):
        self.core = core
        self.request_db = core.db("collection_request")
        self.result_db = core.db("collection_result")
        self.source = core.source

    def now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def date_text(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, datetime.date):
            return value.strftime("%Y-%m-%d")
        return value or ""

    def to_int(self, value, default=0):
        try:
            return int(value)
        except Exception:
            return default

    def to_bool(self, value, default=False):
        if isinstance(value, bool):
            return value
        if value in ["true", "True", "1", 1]:
            return True
        if value in ["false", "False", "0", 0]:
            return False
        return default

    def url_hash(self, url):
        return hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()

    def clean_text(self, value, limit=1000):
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        if len(text) > limit:
            return text[:limit - 1].rstrip() + "…"
        return text

    def clean_recipe_text(self, value, limit=1000):
        text = re.sub(r"<[^>]+>", " ", str(value or ""))
        text = self.clean_text(text, limit)
        try:
            return self.core.clean_user_text(text, "수집 레시피")
        except Exception:
            text = re.sub(r"(?i)<\s*/?\s*(script|iframe|object|embed)[^>]*>", " ", text)
            text = re.sub(r"(?i)javascript\s*:", "", text)
            text = re.sub(r"(?i)on[a-z]+\s*=", "", text)
            return self.clean_text(text, limit)

    def result_raw_metadata(self, result):
        raw_metadata = (result or {}).get("raw_metadata")
        if isinstance(raw_metadata, dict):
            return raw_metadata
        if raw_metadata in [None, ""]:
            return {}
        try:
            parsed = json.loads(raw_metadata)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def normalize_recipe_list(self, value, limit=120):
        if value in [None, ""]:
            return []
        if not isinstance(value, list):
            value = [value]
        items = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("text") or item.get("name") or item.get("label") or item.get("title") or ""
                amount = item.get("amount") or item.get("quantity") or item.get("unit") or ""
                if amount:
                    text = f"{text} {amount}".strip()
            else:
                text = item
            text = self.clean_recipe_text(text, limit)
            if text:
                items.append(text)
        return items

    def source_type_from_result(self, result):
        if (result or {}).get("result_type") == "youtube":
            return self.core.constants.SOURCE_TYPES["YOUTUBE"]
        return self.core.constants.SOURCE_TYPES["WEB"]

    def result_url(self, result):
        return self.clean_text((result or {}).get("url", ""), 2048)

    def result_title(self, result):
        title = self.clean_recipe_text((result or {}).get("title", ""), 160)
        if title:
            return title
        url = self.result_url(result)
        hostname = urllib.parse.urlparse(url).hostname or ""
        return self.clean_recipe_text(hostname or "수집 레시피", 160)

    def request_dto(self, item):
        return {
            "id": item.get("id"),
            "targetType": item.get("target_type", ""),
            "targetValue": item.get("target_value", ""),
            "targetLabel": item.get("target_label", ""),
            "provider": item.get("provider", "auto"),
            "status": item.get("status", "queued"),
            "maxItems": int(item.get("max_items") or 0),
            "includeComments": bool(item.get("include_comments")),
            "immediate": bool(item.get("immediate")),
            "resultCount": int(item.get("result_count") or 0),
            "retryCount": int(item.get("retry_count") or 0),
            "errorMessage": item.get("error_message", ""),
            "requestedBy": item.get("requested_by", ""),
            "startedAt": self.date_text(item.get("started_at")),
            "completedAt": self.date_text(item.get("completed_at")),
            "createdAt": self.date_text(item.get("created_at")),
            "updatedAt": self.date_text(item.get("updated_at")),
        }

    def result_dto(self, item):
        raw_metadata = self.result_raw_metadata(item)
        return {
            "id": item.get("id"),
            "requestId": item.get("request_id", ""),
            "resultType": item.get("result_type", ""),
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
            "publishedAt": item.get("published_at", ""),
            "thumbnailUrl": item.get("thumbnail_url", ""),
            "channelTitle": item.get("channel_title", ""),
            "viewCount": int(item.get("view_count") or 0),
            "likeCount": int(item.get("like_count") or 0),
            "commentCount": int(item.get("comment_count") or 0),
            "status": item.get("status", "stored"),
            "rawMetadata": raw_metadata,
            "ingredients": raw_metadata.get("ingredients", []),
            "steps": raw_metadata.get("steps", []),
            "sourceLinks": raw_metadata.get("sourceLinks", []),
            "recipePrompt": raw_metadata.get("recipePrompt", ""),
            "promotedRecipeDishId": raw_metadata.get("promotedRecipeDishId", ""),
            "promotedRecipeVersionId": raw_metadata.get("promotedRecipeVersionId", ""),
            "promotedAt": raw_metadata.get("promotedAt", ""),
            "createdAt": self.date_text(item.get("created_at")),
            "updatedAt": self.date_text(item.get("updated_at")),
        }

    def options(self):
        return {
            "targetTypes": [
                {"value": "web_url", "label": "웹 URL"},
                {"value": "web_keyword", "label": "웹 검색어"},
                {"value": "youtube_video", "label": "유튜브 영상 URL"},
                {"value": "youtube_channel", "label": "유튜브 채널"},
                {"value": "youtube_keyword", "label": "유튜브 검색어"},
            ],
            "requestStatuses": [{"value": value, "label": value} for value in REQUEST_STATUSES],
            "resultStatuses": [{"value": value, "label": value} for value in RESULT_STATUSES],
            "limits": {"maxItems": MAX_ITEMS_LIMIT, "defaultItems": 10, "maxComments": 20},
            "settings": {
                "youtubeApiKeyConfigured": bool(os.environ.get("YOUTUBE_API_KEY")),
                "webSearchProviderConfigured": bool(os.environ.get("WEB_SEARCH_API_KEY")),
                "rateLimitNote": "요청당 최대 50개, 외부 요청 timeout 5초 기준",
            },
            "collectorPrompt": self.recipe_prompt_template(),
            "improvementNotes": [
                "실제 웹 검색은 WEB_SEARCH_API_KEY 또는 검색 provider 연결 후 robots.txt와 서비스 약관을 확인해 실행합니다.",
                "YouTube는 YOUTUBE_API_KEY 연결 시 검색/영상 메타데이터를 수집하고, quota 초과와 실패 응답을 별도 로그로 남깁니다.",
                "수집 결과는 원문 링크, 재료, 조리 단계, 요약을 분리 저장하고 관리자 검수 후 공개 레시피로 전환합니다.",
                "중복 URL 해시, 요청당 최대 개수, timeout, 실패 재시도 횟수를 제한해 운영 안정성을 유지합니다.",
            ],
        }

    def recipe_prompt_template(self):
        return "\n".join([
            "역할: 레시피 수집 결과를 검수 가능한 구조화 데이터로 정리하는 에디터.",
            "입력: 키워드, 웹/유튜브 제목, 원문 URL, 설명/본문 요약, 채널/출처, 업로드일.",
            "출력 JSON: {name, sourceUrl, sourceType, ingredients[], steps[], summary, cautions[], tags[]}.",
            "규칙: 원문 링크를 반드시 유지하고, 확인되지 않은 재료/분량은 추정하지 말고 빈 값 또는 검토 필요로 표시한다.",
            "안전: 알레르기, 영유아 식단, 저염/저당 조건은 주의 문구를 분리한다.",
        ])

    def validate_payload(self, data):
        target_type = data.get("targetType") or data.get("target_type") or ""
        if target_type not in TARGET_TYPES:
            raise Exception("지원하지 않는 수집 타입입니다.")
        target_value = str(data.get("targetValue") or data.get("target_value") or "").strip()
        if not target_value:
            raise Exception("수집 대상 값을 입력해주세요.")
        if len(target_value) > 2048:
            raise Exception("수집 대상 값은 2048자 이하로 입력해주세요.")
        max_items = self.to_int(data.get("maxItems") or data.get("max_items"), 10)
        if max_items < 1:
            max_items = 1
        if max_items > MAX_ITEMS_LIMIT:
            raise Exception(f"요청당 최대 {MAX_ITEMS_LIMIT}개까지만 수집할 수 있습니다.")
        if target_type in ["web_url", "youtube_video"]:
            target_value = self.source.validate_url(target_value, "수집 대상 URL")
        provider = "youtube" if target_type in YOUTUBE_TYPES else "web"
        return {
            "target_type": target_type,
            "target_value": target_value,
            "target_label": self.clean_text(data.get("targetLabel") or data.get("target_label") or target_value, 300),
            "provider": provider,
            "max_items": max_items,
            "include_comments": self.to_bool(data.get("includeComments") or data.get("include_comments"), False),
            "immediate": self.to_bool(data.get("immediate"), True),
        }

    def create_request(self, data, requested_by=""):
        payload = self.validate_payload(data)
        now = self.now()
        payload.update({
            "status": "queued",
            "result_count": 0,
            "retry_count": 0,
            "error_message": "",
            "requested_by": requested_by or self.core.session_user_id(),
            "created_at": now,
            "updated_at": now,
        })
        request_id = self.request_db.insert(payload)
        if payload.get("immediate"):
            self.execute_request(request_id)
        return self.get_request(request_id)

    def get_request(self, request_id):
        item = self.request_db.get(id=request_id)
        if not item:
            raise Exception("수집 요청을 찾을 수 없습니다.")
        return item

    def list_requests(self, page=1, dump=20, status="", text=""):
        filters = {}
        if status:
            filters["status"] = status
        rows = self.request_db.rows(page=1 if text else page, dump=500 if text else dump, orderby="created_at", order="DESC", **filters)
        total = self.request_db.count(**filters) or 0
        if text:
            needle = str(text).lower()
            matched = []
            for row in rows:
                haystack = " ".join([row.get("target_type", ""), row.get("target_value", ""), row.get("target_label", ""), row.get("error_message", "")]).lower()
                if needle in haystack:
                    matched.append(row)
            total = len(matched)
            start = (page - 1) * dump
            rows = matched[start:start + dump]
        return rows, total

    def list_results(self, page=1, dump=20, request_id="", result_type="", status="", text=""):
        filters = {}
        if request_id:
            filters["request_id"] = request_id
        if result_type:
            filters["result_type"] = result_type
        if status:
            filters["status"] = status
        rows = self.result_db.rows(page=1 if text else page, dump=1000 if text else dump, orderby="created_at", order="DESC", **filters)
        total = self.result_db.count(**filters) or 0
        if text:
            needle = str(text).lower()
            matched = []
            for row in rows:
                haystack = " ".join([row.get("title", ""), row.get("source", ""), row.get("url", ""), row.get("summary", ""), row.get("channel_title", "")]).lower()
                if needle in haystack:
                    matched.append(row)
            total = len(matched)
            start = (page - 1) * dump
            rows = matched[start:start + dump]
        return rows, total

    def status_summary(self):
        return [{"value": status, "label": status, "count": self.request_db.count(status=status) or 0} for status in REQUEST_STATUSES]

    def clear_results(self, request_id):
        rows = self.result_db.rows(request_id=request_id, page=1, dump=1000)
        for row in rows:
            self.result_db.delete(id=row.get("id"))

    def execute_request(self, request_id):
        request = self.get_request(request_id)
        now = self.now()
        self.request_db.update({"status": "running", "started_at": now, "updated_at": now, "error_message": ""}, id=request_id)
        self.clear_results(request_id)
        try:
            if request.get("target_type") in WEB_TYPES:
                items = self.collect_web(request)
            else:
                items = self.collect_youtube(request)
            count = 0
            seen = set()
            for item in items[:int(request.get("max_items") or 10)]:
                url = item.get("url", "")
                fingerprint = self.url_hash(url or item.get("title", ""))
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                item["request_id"] = request_id
                item["url_hash"] = fingerprint
                item.setdefault("status", "stored")
                item.setdefault("raw_metadata", {})
                item["raw_metadata"] = self.core.json_dumps(item.get("raw_metadata") or {})
                item["created_at"] = self.now()
                item["updated_at"] = self.now()
                self.result_db.insert(item)
                count += 1
            self.request_db.update({"status": "done", "result_count": count, "completed_at": self.now(), "updated_at": self.now(), "error_message": ""}, id=request_id)
        except Exception as error:
            self.request_db.update({"status": "failed", "completed_at": self.now(), "updated_at": self.now(), "error_message": str(error)}, id=request_id)
        return self.get_request(request_id)

    def retry_request(self, request_id):
        request = self.get_request(request_id)
        self.request_db.update({"retry_count": int(request.get("retry_count") or 0) + 1, "status": "queued", "updated_at": self.now()}, id=request_id)
        return self.execute_request(request_id)

    def delete_request(self, request_id):
        request = self.get_request(request_id)
        self.clear_results(request_id)
        self.request_db.delete(id=request_id)
        return request

    def delete_results(self, ids):
        deleted = 0
        for result_id in ids:
            if self.result_db.get(id=result_id):
                self.result_db.delete(id=result_id)
                deleted += 1
        return deleted

    def build_recipe_payload_from_result(self, result):
        result = result or {}
        raw_metadata = self.result_raw_metadata(result)
        title = self.result_title(result)
        summary = self.clean_recipe_text(result.get("summary", ""), 2000)
        source_type = self.source_type_from_result(result)
        ingredients = self.normalize_recipe_list(raw_metadata.get("ingredients"))
        steps = self.normalize_recipe_list(raw_metadata.get("steps"), 500)
        cautions = self.normalize_recipe_list(raw_metadata.get("cautions") or raw_metadata.get("allergenInfo"))
        tags = self.normalize_recipe_list(raw_metadata.get("tags"), 40)
        if not tags:
            tags = ["유튜브"] if source_type == self.core.constants.SOURCE_TYPES["YOUTUBE"] else ["웹수집"]
        cooking_tips = self.normalize_recipe_list(raw_metadata.get("cookingTips"), 300)
        if not ingredients:
            cooking_tips.append("원문에서 재료 확인 필요")
        if not steps:
            cooking_tips.append("원문에서 조리 단계 확인 필요")
        cooking_time = self.to_int(raw_metadata.get("cookingTime") or raw_metadata.get("cooking_time"), 0)
        dish = {
            "name": title,
            "description": summary,
            "category": self.clean_recipe_text(raw_metadata.get("category", ""), 64) or "일반",
            "tags": self.core.json_dumps(tags),
            "thumbnail_url": self.result_url({"url": result.get("thumbnail_url", "")}),
            "status": self.core.constants.RECIPE_STATUSES["PENDING_REVIEW"],
        }
        version = {
            "title": title,
            "source_type": source_type,
            "source_url": self.result_url(result),
            "source_title": self.clean_recipe_text(result.get("title", ""), 300),
            "source_author": self.clean_recipe_text(result.get("channel_title") or result.get("source", ""), 160),
            "source_collected_at": self.now(),
            "summary": summary,
            "ingredients": self.core.json_dumps(ingredients),
            "steps": self.core.json_dumps(steps),
            "cooking_tips": self.core.json_dumps(cooking_tips),
            "failure_prevention_tips": self.core.json_dumps([]),
            "substitution_tips": self.core.json_dumps([]),
            "nutrition_info": self.core.json_dumps({}),
            "sodium_info": self.core.json_dumps({}),
            "allergen_info": self.core.json_dumps(cautions),
            "difficulty": "normal",
            "cooking_time": cooking_time if cooking_time > 0 else 0,
            "serving_size": self.clean_recipe_text(raw_metadata.get("servingSize") or raw_metadata.get("serving_size", ""), 32),
            "ai_modified": False,
            "status": self.core.constants.RECIPE_STATUSES["PENDING_REVIEW"],
        }
        return {"dish": dish, "version": version}

    def find_version_by_source_url(self, source_url):
        source_url = self.result_url({"url": source_url})
        if not source_url:
            return None
        rows = self.core.recipe.version_db.rows(source_url=source_url, page=1, dump=1)
        return rows[0] if rows else None

    def promote_result_to_recipe(self, result_id, reviewed_by=""):
        result_id = str(result_id or "").strip()
        try:
            result = self.result_db.get(id=result_id)
            if not result:
                return {"resultId": result_id, "status": "failed", "error": "수집 결과를 찾을 수 없습니다."}
            raw_metadata = self.result_raw_metadata(result)
            if raw_metadata.get("promotedRecipeVersionId"):
                return {
                    "resultId": result_id,
                    "status": "skipped",
                    "reason": "이미 검수 대기 레시피로 등록된 결과입니다.",
                    "dishId": raw_metadata.get("promotedRecipeDishId", ""),
                    "versionId": raw_metadata.get("promotedRecipeVersionId", ""),
                }
            source_url = self.result_url(result)
            if not source_url:
                return {"resultId": result_id, "status": "failed", "error": "원문 URL이 없는 수집 결과는 레시피화할 수 없습니다."}
            existing = self.find_version_by_source_url(source_url)
            if existing:
                return {
                    "resultId": result_id,
                    "status": "skipped",
                    "reason": "같은 원문 URL의 레시피가 이미 있습니다.",
                    "dishId": existing.get("dish_id", ""),
                    "versionId": existing.get("id", ""),
                }
            payload = self.build_recipe_payload_from_result(result)
            dish_id = self.core.recipe.create_dish(payload.get("dish"))
            version_id = self.core.recipe.create_version(dish_id, payload.get("version"))
            raw_metadata["promotedRecipeDishId"] = dish_id
            raw_metadata["promotedRecipeVersionId"] = version_id
            raw_metadata["promotedAt"] = self.now()
            raw_metadata["promotedBy"] = reviewed_by or ""
            self.result_db.update({"raw_metadata": self.core.json_dumps(raw_metadata), "updated_at": self.now()}, id=result_id)
            return {"resultId": result_id, "status": "created", "dishId": dish_id, "versionId": version_id}
        except Exception as error:
            return {"resultId": result_id, "status": "failed", "error": str(error)}

    def promote_results_to_recipes(self, result_ids, reviewed_by=""):
        result_ids = result_ids or []
        items = [self.promote_result_to_recipe(result_id, reviewed_by=reviewed_by) for result_id in result_ids]
        return {
            "created": len([item for item in items if item.get("status") == "created"]),
            "skipped": len([item for item in items if item.get("status") == "skipped"]),
            "failed": len([item for item in items if item.get("status") == "failed"]),
            "items": items,
        }

    def collect_web(self, request):
        target_type = request.get("target_type")
        target_value = request.get("target_value")
        if target_type == "web_url":
            return [self.collect_web_url(target_value)]
        return self.sample_web_keyword(target_value, int(request.get("max_items") or 10))

    def robots_allowed(self, url):
        if self.source.is_blocked_domain(url):
            return False
        try:
            parsed = urllib.parse.urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            request = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=3) as response:
                content = response.read(300000).decode("utf-8", errors="ignore")
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(content.splitlines())
            return parser.can_fetch(USER_AGENT, url)
        except urllib.error.HTTPError as error:
            return error.code not in [401, 403]
        except Exception:
            return True

    def collect_web_url(self, url):
        normalized = self.source.validate_url(url, "웹 URL")
        if not self.robots_allowed(normalized):
            raise Exception("robots.txt 정책상 수집할 수 없는 URL입니다.")
        try:
            request = urllib.request.Request(normalized, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=5) as response:
                content_type = response.headers.get("Content-Type", "")
                html = response.read(700000).decode("utf-8", errors="ignore")
            title = self.extract_tag(html, "title") or normalized
            description = self.extract_meta(html, "description")
            image = self.extract_meta(html, "og:image")
            text = self.clean_text(re.sub(r"<[^>]+>", " ", html), 600)
            links = self.extract_links(html, normalized)[:20]
            return {
                "result_type": "web",
                "title": self.clean_text(title, 300),
                "source": urllib.parse.urlparse(normalized).hostname or "web",
                "url": normalized,
                "summary": description or text,
                "published_at": "",
                "thumbnail_url": image,
                "raw_metadata": {"contentType": content_type, "links": links, "robotsAllowed": True},
            }
        except Exception as error:
            return self.sample_web_url(normalized, str(error))

    def extract_tag(self, html, tag):
        match = re.search(rf"<\s*{tag}[^>]*>(.*?)<\s*/\s*{tag}\s*>", html or "", re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip()

    def extract_meta(self, html, name):
        patterns = [
            rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(name)}["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(name)}["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html or "", re.IGNORECASE | re.DOTALL)
            if match:
                return self.clean_text(match.group(1), 500)
        return ""

    def extract_links(self, html, base_url):
        links = []
        seen = set()
        for match in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\']', html or "", re.IGNORECASE):
            href = urllib.parse.urljoin(base_url, match.group(1))
            if href.startswith("http") and href not in seen:
                seen.add(href)
                links.append(href)
        return links

    def sample_web_url(self, url, reason=""):
        return {
            "result_type": "web",
            "title": f"웹 수집 샘플: {urllib.parse.urlparse(url).hostname or url}",
            "source": urllib.parse.urlparse(url).hostname or "web",
            "url": url,
            "summary": "외부 호출이 실패해 샘플 결과로 저장했습니다. 실제 운영에서는 제목, 메타 설명, 본문 요약, 대표 이미지, 링크 목록을 저장합니다.",
            "published_at": "",
            "thumbnail_url": "",
            "raw_metadata": {"fallback": True, "error": reason},
        }

    def sample_web_keyword(self, keyword, limit):
        items = []
        encoded = urllib.parse.quote(keyword)
        sources = [
            ("Google", f"https://www.google.com/search?q={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC+%EC%A1%B0%EB%A6%AC%EB%B2%95", "검색 결과에서 여러 웹 레시피와 조리법을 확인합니다."),
            ("Naver", f"https://search.naver.com/search.naver?query={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC+%EC%A1%B0%EB%A6%AC%EB%B2%95", "국내 블로그와 레시피 문서 검색 결과 링크입니다."),
            ("10000recipe", f"https://www.10000recipe.com/recipe/list.html?q={encoded}", "만개의레시피 검색 결과 링크입니다."),
            ("YouTube Search", f"https://www.youtube.com/results?search_query={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC", "영상 조리법 검색 결과 링크입니다."),
            ("Google Video", f"https://www.google.com/search?tbm=vid&q={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC", "웹 영상 검색 결과 링크입니다."),
            ("Naver Video", f"https://search.naver.com/search.naver?where=video&query={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC", "네이버 영상 검색 결과 링크입니다."),
        ]
        for index, source in enumerate(sources[:min(limit, len(sources))], start=1):
            source_name, url, note = source
            items.append({
                "result_type": "web",
                "title": f"{keyword} 레시피/조리법 후보 {index}",
                "source": source_name,
                "url": url,
                "summary": f"{note} 검색 provider 연결 전에는 검수 가능한 후보 링크로 저장합니다.",
                "published_at": "",
                "thumbnail_url": "",
                "raw_metadata": {
                    "fallback": True,
                    "keyword": keyword,
                    "ingredients": [f"{keyword} 주재료", "양념/소스", "선택 부재료"],
                    "steps": ["원문 링크를 열어 재료와 분량을 확인합니다.", "조리 순서와 시간 정보를 추출합니다.", "관리자가 검수 후 공개 레시피로 전환합니다."],
                    "sourceLinks": [{"label": source_name, "url": url}],
                    "recipePrompt": self.recipe_prompt_template(),
                },
            })
        return items

    def collect_youtube(self, request):
        api_key = os.environ.get("YOUTUBE_API_KEY", "")
        if not api_key:
            return self.sample_youtube(request)
        target_type = request.get("target_type")
        if target_type == "youtube_video":
            video_id = self.extract_video_id(request.get("target_value"))
            if not video_id:
                raise Exception("유튜브 영상 URL에서 video id를 찾을 수 없습니다.")
            return self.fetch_youtube_videos([video_id], api_key)
        if target_type == "youtube_keyword":
            return self.search_youtube(request.get("target_value"), int(request.get("max_items") or 10), api_key)
        return self.sample_youtube(request, "채널 URL은 channel id 또는 handle 해석 로직 연결 후 실제 API 호출로 전환합니다.")

    def extract_video_id(self, value):
        text = str(value or "")
        parsed = urllib.parse.urlparse(text)
        if parsed.hostname and "youtu.be" in parsed.hostname:
            return parsed.path.strip("/")
        query = urllib.parse.parse_qs(parsed.query or "")
        if query.get("v"):
            return query.get("v")[0]
        match = re.search(r"/shorts/([^/?#]+)", text)
        if match:
            return match.group(1)
        return ""

    def youtube_get(self, path, params, api_key):
        params = dict(params or {})
        params["key"] = api_key
        url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch_youtube_videos(self, video_ids, api_key):
        data = self.youtube_get("videos", {"part": "snippet,statistics", "id": ",".join(video_ids), "maxResults": len(video_ids)}, api_key)
        items = []
        for row in data.get("items", []):
            snippet = row.get("snippet", {})
            stats = row.get("statistics", {})
            video_id = row.get("id", "")
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = (thumbnails.get("medium") or thumbnails.get("default") or {}).get("url", "")
            items.append({
                "result_type": "youtube",
                "title": snippet.get("title", ""),
                "source": "YouTube",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "summary": self.clean_text(snippet.get("description", ""), 800),
                "published_at": snippet.get("publishedAt", "")[:10],
                "thumbnail_url": thumbnail,
                "channel_title": snippet.get("channelTitle", ""),
                "view_count": self.to_int(stats.get("viewCount"), 0),
                "like_count": self.to_int(stats.get("likeCount"), 0),
                "comment_count": self.to_int(stats.get("commentCount"), 0),
                "raw_metadata": {"videoId": video_id},
            })
        return items

    def search_youtube(self, keyword, limit, api_key):
        data = self.youtube_get("search", {"part": "snippet", "q": keyword, "type": "video", "maxResults": min(limit, 25), "order": "relevance"}, api_key)
        ids = []
        for row in data.get("items", []):
            video_id = (row.get("id") or {}).get("videoId")
            if video_id:
                ids.append(video_id)
        if not ids:
            return []
        return self.fetch_youtube_videos(ids, api_key)

    def sample_youtube(self, request, note="YOUTUBE_API_KEY가 없어 샘플 결과로 저장했습니다."):
        keyword = request.get("target_value", "YouTube")
        count = 1 if request.get("target_type") == "youtube_video" else min(int(request.get("max_items") or 10), 6)
        items = []
        encoded = urllib.parse.quote(keyword)
        for index in range(1, count + 1):
            url = request.get("target_value") if request.get("target_type") == "youtube_video" else f"https://www.youtube.com/results?search_query={encoded}+%EB%A0%88%EC%8B%9C%ED%94%BC"
            items.append({
                "result_type": "youtube",
                "title": f"{keyword} 유튜브 샘플 영상 {index}",
                "source": "YouTube",
                "url": url,
                "summary": "YouTube Data API가 연결되면 제목, 설명, 채널명, 업로드일, 조회수, 좋아요 수, 댓글 수와 조리법 설명을 저장합니다.",
                "published_at": datetime.date.today().strftime("%Y-%m-%d"),
                "thumbnail_url": "",
                "channel_title": "sample-channel",
                "view_count": 1000 * index,
                "like_count": 100 * index,
                "comment_count": 10 * index,
                "raw_metadata": {
                    "fallback": True,
                    "note": note,
                    "ingredients": [f"{keyword} 주재료", "양념", "토핑/선택 재료"],
                    "steps": ["영상 설명과 자막에서 재료 목록을 확인합니다.", "조리 장면 순서대로 단계를 정리합니다.", "원본 영상 링크와 채널명을 함께 보존합니다."],
                    "sourceLinks": [{"label": "YouTube", "url": url}],
                    "recipePrompt": self.recipe_prompt_template(),
                },
            })
        return items

    def export_results(self, ids=None, result_type="", text="", file_format="json"):
        ids = ids or []
        if ids:
            rows = []
            for result_id in ids:
                row = self.result_db.get(id=result_id)
                if row:
                    rows.append(row)
        else:
            rows, total = self.list_results(page=1, dump=1000, result_type=result_type, text=text)
        items = [self.result_dto(row) for row in rows]
        if file_format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["id", "resultType", "title", "source", "url", "summary", "publishedAt", "channelTitle", "viewCount", "likeCount", "commentCount"])
            writer.writeheader()
            for item in items:
                writer.writerow({key: item.get(key, "") for key in writer.fieldnames})
            return {"filename": "collector-results.csv", "mime": "text/csv;charset=utf-8", "content": output.getvalue()}
        return {"filename": "collector-results.json", "mime": "application/json;charset=utf-8", "content": json.dumps(items, ensure_ascii=False, indent=2)}

Model = Collector

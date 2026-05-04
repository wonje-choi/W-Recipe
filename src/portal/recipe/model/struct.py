import datetime
import json
import re

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
UNSAFE_TEXT_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"<\s*iframe", re.IGNORECASE),
    re.compile(r"<\s*object", re.IGNORECASE),
    re.compile(r"<\s*embed", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on[a-z]+\s*=", re.IGNORECASE),
]
ALLOWED_UPLOAD_EXTENSIONS = set(["jpg", "jpeg", "png", "webp", "gif", "pdf"])
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

class Struct:
    def __init__(self):
        self.orm = wiz.model("portal/season/orm")
        self.session = wiz.model("portal/season/session").use()
        self.constants = wiz.model("portal/recipe/constants")

        self._User = wiz.model("portal/recipe/struct/user")
        self._Auth = wiz.model("portal/recipe/struct/auth")
        self._Recipe = wiz.model("portal/recipe/struct/recipe")
        self._Source = wiz.model("portal/recipe/struct/source")
        self._AI = wiz.model("portal/recipe/struct/ai")
        self._AIDiet = wiz.model("portal/recipe/struct/ai_diet")
        self._Safety = wiz.model("portal/recipe/struct/safety")
        self._Comment = wiz.model("portal/recipe/struct/comment")
        self._Expert = wiz.model("portal/recipe/struct/expert")
        self._Youtube = wiz.model("portal/recipe/struct/youtube")
        self._AdminLog = wiz.model("portal/recipe/struct/admin_log")
        self._Collector = wiz.model("portal/recipe/struct/collector")

        self._init_tables()

    def _init_tables(self):
        tables = [
            "user",
            "user_preference",
            "recipe_dish",
            "recipe_version",
            "crawled_source",
            "ai_prompt_template",
            "ai_recipe_modification",
            "ai_processing_log",
            "comment",
            "favorite_recipe",
            "recent_view",
            "recipe_edit_request",
            "report",
            "expert",
            "expert_assignment",
            "admin_action_log",
            "collection_request",
            "collection_result",
        ]
        for name in tables:
            try:
                db = self.db(name)
                db.orm.create_table(safe=True)
            except Exception:
                pass
        self._migrate_crawled_source()
        self._migrate_ai_modification()
        self._migrate_user_subscription()

    def _table_columns(self, database, table_name):
        columns = []
        for row in database.execute_sql(f"PRAGMA table_info({table_name})").fetchall():
            if isinstance(row, dict):
                columns.append(row.get("name"))
            elif len(row) > 1:
                columns.append(row[1])
        return columns

    def _migrate_crawled_source(self):
        db = self.db("crawled_source")
        try:
            database = db.orm._meta.database
            columns = self._table_columns(database, "recipe_crawled_source")
            if "raw_content" not in columns:
                database.execute_sql("ALTER TABLE recipe_crawled_source ADD COLUMN raw_content TEXT DEFAULT ''")
        except Exception:
            pass

    def _migrate_ai_modification(self):
        db = self.db("ai_recipe_modification")
        try:
            database = db.orm._meta.database
            columns = self._table_columns(database, "recipe_ai_modification")
            if "confidence_score" not in columns:
                database.execute_sql("ALTER TABLE recipe_ai_modification ADD COLUMN confidence_score REAL DEFAULT 0.0")
        except Exception:
            pass

    def _migrate_user_subscription(self):
        db = self.db("user")
        try:
            database = db.orm._meta.database
            columns = self._table_columns(database, "recipe_user")
            if "subscription_plan" not in columns:
                database.execute_sql("ALTER TABLE recipe_user ADD COLUMN subscription_plan VARCHAR(16) DEFAULT 'free'")
            if "subscription_expires_at" not in columns:
                database.execute_sql("ALTER TABLE recipe_user ADD COLUMN subscription_expires_at DATETIME")
        except Exception:
            pass

    def db(self, name):
        return self.orm.use(name, module="recipe")

    def now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def json_dumps(self, value):
        if value is None:
            value = []
        return json.dumps(value, ensure_ascii=False, default=self.json_default)

    def json_default(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, datetime.date):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def json_loads(self, value, default=None):
        if default is None:
            default = []
        if value in [None, ""]:
            return default
        if isinstance(value, (list, dict)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return default

    def public_status(self):
        return self.constants.PUBLIC_RECIPE_STATUS

    def session_user_id(self):
        return self.session.get("id", "")

    def session_role(self):
        return self.session.get("role", "guest")

    def is_admin(self):
        return self.session_role() == self.constants.USER_ROLES["ADMIN"]

    def require_admin(self):
        if self.is_admin() == False:
            raise Exception("Admin permission required")

    def mask_sensitive(self, data):
        sensitive_fields = set([self.normalize_sensitive_key(item) for item in self.constants.SENSITIVE_PROFILE_FIELDS + [
            "password",
            "passwordHash",
            "password_hash",
            "token",
            "csrfToken",
            "csrf_token",
            "session",
            "apiKey",
            "api_key",
            "authorization",
            "secret",
            "rawContent",
            "raw_content",
        ]])
        return self._mask_sensitive_value(data, sensitive_fields)

    def normalize_sensitive_key(self, key):
        return str(key or "").replace("-", "_").lower()

    def _mask_sensitive_value(self, value, sensitive_fields, key=""):
        if key and self.normalize_sensitive_key(key) in sensitive_fields:
            if isinstance(value, list):
                return f"masked:{len(value)}_items"
            if isinstance(value, dict):
                return "masked:object"
            if value:
                return "masked"
            return value
        if isinstance(value, dict):
            return {item_key: self._mask_sensitive_value(item_value, sensitive_fields, item_key) for item_key, item_value in value.items()}
        if isinstance(value, list):
            return [self._mask_sensitive_value(item, sensitive_fields) for item in value]
        return value

    def clean_user_text(self, value, field_name="내용"):
        text = CONTROL_CHAR_PATTERN.sub("", str(value or "")).strip()
        for pattern in UNSAFE_TEXT_PATTERNS:
            if pattern.search(text):
                raise Exception(f"{field_name}에 허용되지 않는 스크립트 또는 HTML 이벤트가 포함되어 있습니다.")
        return text

    def validate_upload_file(self, filename, size=0):
        name = (filename or "").strip()
        if not name or "/" in name or "\\" in name:
            raise Exception("파일 이름이 올바르지 않습니다.")
        if "." not in name:
            raise Exception("파일 확장자를 확인해주세요.")
        extension = name.rsplit(".", 1)[1].lower()
        if extension not in ALLOWED_UPLOAD_EXTENSIONS:
            raise Exception("허용되지 않는 파일 형식입니다.")
        try:
            filesize = int(size or 0)
        except Exception:
            filesize = 0
        if filesize > MAX_UPLOAD_BYTES:
            raise Exception("파일은 5MB 이하만 업로드할 수 있습니다.")
        return {"filename": name, "extension": extension, "maxBytes": MAX_UPLOAD_BYTES}

    @property
    def user(self):
        return self._User(self)

    @property
    def auth(self):
        return self._Auth(self)

    @property
    def recipe(self):
        return self._Recipe(self)

    @property
    def source(self):
        return self._Source(self)

    @property
    def ai(self):
        return self._AI(self)

    @property
    def ai_diet(self):
        return self._AIDiet(self)

    @property
    def safety(self):
        return self._Safety(self)

    @property
    def comment(self):
        return self._Comment(self)

    @property
    def expert(self):
        return self._Expert(self)

    @property
    def youtube(self):
        return self._Youtube(self)

    @property
    def admin_log(self):
        return self._AdminLog(self)

    @property
    def collector(self):
        return self._Collector(self)

Model = Struct()

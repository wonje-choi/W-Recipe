import datetime
import hashlib
import hmac
import secrets

class Auth:
    MAX_LOGIN_FAILURES = 5
    LOCK_MINUTES = 15
    HASH_ITERATIONS = 120000

    def __init__(self, core):
        self.core = core
        self.user_db = core.db("user")
        self.constants = core.constants
        self.session = core.session

    def normalize_email(self, email):
        return (email or "").strip().lower()

    def hash_password(self, password, salt=""):
        if not salt:
            salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            (password or "").encode("utf-8"),
            salt.encode("utf-8"),
            self.HASH_ITERATIONS,
        ).hex()
        return f"pbkdf2_sha256${self.HASH_ITERATIONS}${salt}${digest}"

    def verify_password(self, password, password_hash):
        parts = (password_hash or "").split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        try:
            iterations = int(parts[1])
            salt = parts[2]
            expected = parts[3]
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                (password or "").encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            return hmac.compare_digest(digest, expected)
        except Exception:
            return False

    def create_user(self, email, password, nickname="", role="user"):
        return self.core.user.create({
            "email": self.normalize_email(email),
            "password_hash": self.hash_password(password),
            "nickname": nickname,
            "role": role,
            "status": self.constants.USER_STATUSES["ACTIVE"],
        })

    def create_admin_password_hash(self, password):
        return self.hash_password(password)

    def _locked_until(self, user):
        locked_until = user.get("locked_until")
        if not locked_until:
            return None
        if isinstance(locked_until, datetime.datetime):
            return locked_until
        try:
            return datetime.datetime.strptime(str(locked_until), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    def _is_locked(self, user):
        locked_until = self._locked_until(user)
        if locked_until is None:
            return False
        return locked_until > datetime.datetime.now()

    def authenticate(self, email, password):
        email = self.normalize_email(email)
        user = self.user_db.get(email=email)
        if not user:
            return None
        if user.get("status") != self.constants.USER_STATUSES["ACTIVE"]:
            raise Exception("계정이 활성 상태가 아닙니다.")
        if self._is_locked(user):
            raise Exception("로그인 시도가 제한되었습니다. 잠시 후 다시 시도해주세요.")
        if self.verify_password(password, user.get("password_hash")) == False:
            failed_count = int(user.get("login_failed_count") or 0) + 1
            data = {
                "login_failed_count": failed_count,
                "updated_at": datetime.datetime.now(),
            }
            if failed_count >= self.MAX_LOGIN_FAILURES:
                data["locked_until"] = datetime.datetime.now() + datetime.timedelta(minutes=self.LOCK_MINUTES)
            self.user_db.update(data, id=user.get("id"))
            return None
        self.user_db.update({
            "login_failed_count": 0,
            "locked_until": None,
            "last_login_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }, id=user.get("id"))
        return self.safe_user(user)

    def safe_user(self, user):
        if not user:
            return None
        return {
            "id": user.get("id"),
            "email": user.get("email"),
            "nickname": user.get("nickname", ""),
            "role": user.get("role", self.constants.USER_ROLES["USER"]),
            "status": user.get("status", self.constants.USER_STATUSES["ACTIVE"]),
            "subscriptionPlan": user.get("subscription_plan", self.constants.SUBSCRIPTION_PLANS["FREE"]),
            "subscriptionExpiresAt": self.date_text(user.get("subscription_expires_at")),
        }

    def date_text(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, datetime.date):
            return value.strftime("%Y-%m-%d")
        return str(value or "").split(" ")[0]

    def login(self, email, password):
        user = self.authenticate(email, password)
        if user is None:
            return None
        self.session.set(
            id=user["id"],
            email=user["email"],
            nickname=user.get("nickname", ""),
            role=user["role"],
            status=user["status"],
        )
        return user

    def logout(self):
        for key in ["id", "email", "nickname", "role", "status"]:
            if self.session.has(key):
                self.session.delete(key)

    def current_user(self):
        user_id = self.session.get("id", "")
        if not user_id:
            return None
        user = self.user_db.get(id=user_id)
        if not user:
            return None
        if user.get("status") != self.constants.USER_STATUSES["ACTIVE"]:
            return None
        return self.safe_user(user)

    def require_login(self):
        user = self.current_user()
        if user is None:
            raise Exception("로그인이 필요합니다.")
        return user

    def require_role(self, roles):
        if isinstance(roles, str):
            roles = [roles]
        user = self.require_login()
        if user.get("role") not in roles:
            raise Exception("권한이 없습니다.")
        return user

    def require_admin(self):
        return self.require_role([self.constants.USER_ROLES["ADMIN"]])

    def subscription_expires_at(self, value):
        if not value:
            return None
        if isinstance(value, datetime.datetime):
            return value
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.datetime.strptime(str(value), fmt)
            except Exception:
                pass
        return None

    def is_premium_user(self, user):
        if not user:
            return False
        if user.get("role") == self.constants.USER_ROLES["ADMIN"]:
            return True
        if user.get("subscription_plan") != self.constants.SUBSCRIPTION_PLANS["PREMIUM"]:
            return False
        expires_at = self.subscription_expires_at(user.get("subscription_expires_at"))
        return expires_at is None or expires_at >= datetime.datetime.now()

    def require_premium(self):
        user = self.require_login()
        row = self.user_db.get(id=user.get("id")) or {}
        if not self.is_premium_user(row):
            raise Exception("프리미엄 구독이 필요합니다.")
        return self.safe_user(row)

    def upgrade_subscription(self, user_id, plan, expires_at=None):
        user = self.user_db.get(id=user_id)
        if not user:
            raise Exception("사용자를 찾을 수 없습니다.")
        if not self.constants.has_value("SUBSCRIPTION_PLANS", plan):
            raise Exception("지원하지 않는 구독 플랜입니다.")
        parsed_expires_at = self.subscription_expires_at(expires_at)
        if expires_at and parsed_expires_at is None:
            raise Exception("구독 만료일 형식이 올바르지 않습니다.")
        if plan == self.constants.SUBSCRIPTION_PLANS["FREE"]:
            parsed_expires_at = None
        self.user_db.update({
            "subscription_plan": plan,
            "subscription_expires_at": parsed_expires_at,
            "updated_at": datetime.datetime.now(),
        }, id=user_id)
        return self.safe_user(self.user_db.get(id=user_id))

    def role_policy(self):
        return {
            "guest": ["public_recipe_read"],
            "user": ["public_recipe_read", "favorite", "comment", "edit_request", "report"],
            "admin": ["public_recipe_read", "recipe_manage", "review_manage", "user_manage", "audit_read"],
        }

Model = Auth

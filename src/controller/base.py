import season
import datetime
import hmac
import json
import os
import secrets
import time

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 120
RATE_LIMIT_SESSION_KEY = "recipe_rate_limit"
CSRF_SESSION_KEY = "recipe_csrf_token"
SESSION_PRIVATE_KEYS = set([RATE_LIMIT_SESSION_KEY, CSRF_SESSION_KEY])

class Controller:
    def __init__(self):
        wiz.session = wiz.model("portal/season/session").use()
        csrf_token = self.ensure_csrf_token()
        self.apply_rate_limit()
        sessiondata = self.public_session_data()
        wiz.response.data.set(session=sessiondata, csrfToken=csrf_token)

        lang = wiz.request.query("lang", None)
        if lang is not None:
            wiz.response.lang(lang)
            wiz.response.redirect(wiz.request.uri())

    def json_default(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

    def apply_rate_limit(self):
        now = time.time()
        timestamps = wiz.session.get(RATE_LIMIT_SESSION_KEY, [])
        if not isinstance(timestamps, list):
            timestamps = []
        active = []
        for item in timestamps:
            try:
                timestamp = float(item)
            except Exception:
                continue
            if now - timestamp < RATE_LIMIT_WINDOW_SECONDS:
                active.append(timestamp)
        if len(active) >= RATE_LIMIT_MAX_REQUESTS:
            wiz.response.status(429, message="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
        active.append(now)
        wiz.session.set(**{RATE_LIMIT_SESSION_KEY: active})

    def ensure_csrf_token(self):
        token = wiz.session.get(CSRF_SESSION_KEY, "")
        if not token:
            token = secrets.token_urlsafe(32)
            wiz.session.set(**{CSRF_SESSION_KEY: token})
        return token

    def public_session_data(self):
        sessiondata = wiz.session.get()
        if not isinstance(sessiondata, dict):
            return {}
        public_data = dict(sessiondata)
        for key in SESSION_PRIVATE_KEYS:
            if key in public_data:
                del public_data[key]
        return public_data

    def is_valid_csrf_token(self, token):
        expected = wiz.session.get(CSRF_SESSION_KEY, "")
        if not expected or not token:
            return False
        return hmac.compare_digest(str(expected), str(token))

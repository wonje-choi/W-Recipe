CSRF_SESSION_KEY = "recipe_csrf_token"


def recipe_struct():
    return wiz.model("portal/recipe/struct")


def csrf_token():
    try:
        return wiz.session.get(CSRF_SESSION_KEY, "")
    except Exception:
        return ""


def login():
    email = wiz.request.query("email", "")
    password = wiz.request.query("password", "")

    if not email or not password:
        return wiz.response.status(400, message="이메일과 비밀번호를 입력해주세요.", csrfToken=csrf_token())

    try:
        struct = recipe_struct()
        user = struct.auth.login(email, password)
    except Exception as error:
        return wiz.response.status(401, message=str(error), csrfToken=csrf_token())

    if user is None:
        return wiz.response.status(401, message="이메일 또는 비밀번호가 올바르지 않습니다.", csrfToken=csrf_token())

    return wiz.response.status(200, user=user, csrfToken=csrf_token())


def logout():
    try:
        recipe_struct().auth.logout()
    except Exception:
        pass
    return wiz.response.status(200, csrfToken=csrf_token())


def me():
    try:
        user = recipe_struct().auth.current_user()
    except Exception:
        user = None
    return wiz.response.status(200, user=user, csrfToken=csrf_token())

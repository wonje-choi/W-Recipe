struct = wiz.model("portal/recipe/struct")
CSRF_SESSION_KEY = "recipe_csrf_token"


def csrf_token():
    return wiz.session.get(CSRF_SESSION_KEY, "")


def login():
    email = wiz.request.query("email", "")
    password = wiz.request.query("password", "")

    if not email or not password:
        wiz.response.status(400, message="이메일과 비밀번호를 입력해주세요.")

    try:
        user = struct.auth.login(email, password)
    except Exception as error:
        wiz.response.status(401, message=str(error))

    if user is None:
        wiz.response.status(401, message="이메일 또는 비밀번호가 올바르지 않습니다.")

    wiz.response.status(200, user=user, csrfToken=csrf_token())


def logout():
    struct.auth.logout()
    wiz.response.status(200, csrfToken=csrf_token())


def me():
    user = struct.auth.current_user()
    wiz.response.status(200, user=user, csrfToken=csrf_token())

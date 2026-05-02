struct = wiz.model("portal/recipe/struct")

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

    wiz.response.status(200, user=user)

def logout():
    struct.auth.logout()
    wiz.response.status(200)

def me():
    user = struct.auth.current_user()
    if user is None:
        wiz.response.status(401, message="로그인이 필요합니다.")
    wiz.response.status(200, user=user)

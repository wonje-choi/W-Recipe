import season

class Controller(wiz.controller("base")):
    def __init__(self):
        super().__init__()
        struct = wiz.model("portal/recipe/struct")
        try:
            user = struct.auth.require_login()
        except Exception as error:
            wiz.response.status(401, message=str(error))
        wiz.response.data.set(user=user)

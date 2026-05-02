import season

class Controller(wiz.controller("user")):
    def __init__(self):
        super().__init__()
        struct = wiz.model("portal/recipe/struct")
        try:
            user = struct.auth.require_premium()
        except Exception as error:
            wiz.response.status(403, message=str(error))
        wiz.response.data.set(user=user)

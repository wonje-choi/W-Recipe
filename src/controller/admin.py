import season

class Controller(wiz.controller("user")):
    def __init__(self):
        super().__init__()
        struct = wiz.model("portal/recipe/struct")
        try:
            admin = struct.auth.require_admin()
        except Exception as error:
            wiz.response.status(401, message=str(error))
        wiz.response.data.set(user=admin)

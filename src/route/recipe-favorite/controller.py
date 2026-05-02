struct = wiz.model("portal/recipe/struct")


method = wiz.request.method()
segment = wiz.request.match("/api/recipes/<version_id>/favorite")
if segment is not None:
    user_id = struct.session_user_id()

    if method == "GET":
        try:
            status = struct.comment.favorite_status(user_id, segment.version_id)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, **status)

    if method == "POST":
        try:
            status = struct.comment.toggle_favorite(user_id, segment.version_id)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, **status)

    if method == "DELETE":
        try:
            removed = struct.comment.remove_favorite(user_id, segment.version_id)
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, favorited=False, removed=removed)

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 즐겨찾기 API 경로입니다.")

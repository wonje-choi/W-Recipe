import datetime

struct = wiz.model("portal/recipe/struct")


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def comment_dto(comment):
    return {
        "id": comment.get("id"),
        "recipeVersionId": comment.get("recipe_version_id", ""),
        "userId": comment.get("user_id", ""),
        "content": comment.get("content", ""),
        "status": comment.get("status", ""),
        "reportCount": int(comment.get("report_count") or 0),
        "createdAt": date_text(comment.get("created_at")),
        "updatedAt": date_text(comment.get("updated_at")),
    }


method = wiz.request.method()
segment = wiz.request.match("/api/comments/<comment_id>")
if segment is not None:
    if method == "DELETE":
        try:
            user = struct.auth.require_login()
            comment = struct.comment.delete(segment.comment_id, user.get("id"))
        except Exception as error:
            wiz.response.status(400, message=str(error))
        wiz.response.status(200, comment=comment_dto(comment))

    wiz.response.status(405, message="Method not allowed")

wiz.response.status(404, message="지원하지 않는 댓글 상세 API 경로입니다.")

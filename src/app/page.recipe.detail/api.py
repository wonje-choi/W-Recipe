import datetime
import json

struct = wiz.model("portal/recipe/struct")
constants = wiz.model("portal/recipe/constants")


def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def date_text(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return value or ""


def parse_data():
    raw = wiz.request.query("data", "")
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            raise Exception("data는 JSON 객체 문자열이어야 합니다.")
    data = wiz.request.query()
    if isinstance(data, dict):
        return data
    return {}


def dish_dto(dish):
    thumbnail_url = dish.get("thumbnail_url", "")
    return {
        "id": dish.get("id"),
        "name": dish.get("name", ""),
        "description": dish.get("description", ""),
        "category": dish.get("category", ""),
        "tags": struct.json_loads(dish.get("tags"), []),
        "thumbnailUrl": thumbnail_url,
        "hasImage": bool(thumbnail_url),
        "viewCount": int(dish.get("view_count") or 0),
        "status": dish.get("status", ""),
        "createdAt": date_text(dish.get("created_at")),
        "updatedAt": date_text(dish.get("updated_at")),
    }


def version_dto(version):
    return {
        "id": version.get("id"),
        "dishId": version.get("dish_id", ""),
        "title": version.get("title", ""),
        "sourceType": version.get("source_type", ""),
        "sourceUrl": version.get("source_url", ""),
        "sourceTitle": version.get("source_title", ""),
        "sourceAuthor": version.get("source_author", ""),
        "sourceCollectedAt": date_text(version.get("source_collected_at")),
        "summary": version.get("summary", ""),
        "ingredients": struct.json_loads(version.get("ingredients"), []),
        "steps": struct.json_loads(version.get("steps"), []),
        "cookingTips": struct.json_loads(version.get("cooking_tips"), []),
        "failurePreventionTips": struct.json_loads(version.get("failure_prevention_tips"), []),
        "substitutionTips": struct.json_loads(version.get("substitution_tips"), []),
        "nutritionInfo": struct.json_loads(version.get("nutrition_info"), {}),
        "sodiumInfo": struct.json_loads(version.get("sodium_info"), {}),
        "allergenInfo": struct.json_loads(version.get("allergen_info"), []),
        "difficulty": version.get("difficulty", ""),
        "cookingTime": int(version.get("cooking_time") or 0),
        "servingSize": version.get("serving_size", ""),
        "viewCount": int(version.get("view_count") or 0),
        "aiModified": bool(version.get("ai_modified")),
        "status": version.get("status", ""),
        "createdAt": date_text(version.get("created_at")),
        "updatedAt": date_text(version.get("updated_at")),
    }


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


def edit_request_dto(item):
    return {
        "id": item.get("id"),
        "userId": item.get("user_id", ""),
        "recipeVersionId": item.get("recipe_version_id", ""),
        "requestType": item.get("request_type", ""),
        "content": item.get("content", ""),
        "attachmentUrl": item.get("attachment_url", ""),
        "status": item.get("status", ""),
        "adminMemo": item.get("admin_memo", ""),
        "handledBy": item.get("handled_by", ""),
        "handledAt": date_text(item.get("handled_at")),
        "createdAt": date_text(item.get("created_at")),
        "updatedAt": date_text(item.get("updated_at")),
    }


def source_dto(version):
    source_url = version.get("source_url", "")
    source = None
    if source_url:
        try:
            source = struct.source.get_by_url(source_url)
        except Exception:
            source = None
    raw_content = (source or {}).get("raw_content", "")
    raw_policy = (source or {}).get("raw_content_storage_policy", "summary_only")
    return {
        "available": bool(source_url),
        "sourceType": version.get("source_type", ""),
        "sourceUrl": source_url,
        "sourceTitle": (source or {}).get("title") or version.get("source_title", ""),
        "sourceAuthor": (source or {}).get("author") or version.get("source_author", ""),
        "sourceCollectedAt": date_text((source or {}).get("collected_at") or version.get("source_collected_at")),
        "rawContent": raw_content if raw_policy == "full" else "",
        "rawContentStoragePolicy": raw_policy,
        "message": "" if source_url else "등록된 원본 출처 링크가 없습니다.",
    }


def compare_versions(base_version, target_version):
    if base_version is None or target_version is None:
        return None
    base = version_dto(base_version)
    target = version_dto(target_version)
    return {
        "baseVersion": base,
        "targetVersion": target,
        "comparison": {
            "ingredientsChanged": base["ingredients"] != target["ingredients"],
            "stepsChanged": base["steps"] != target["steps"],
            "nutritionChanged": base["nutritionInfo"] != target["nutritionInfo"],
            "sodiumChanged": base["sodiumInfo"] != target["sodiumInfo"],
            "targetAiModified": target["aiModified"],
            "sourceTypeChanged": base["sourceType"] != target["sourceType"],
        },
    }


def find_base_version(versions, target_id):
    for version in versions:
        if version.get("id") != target_id and not version.get("ai_modified"):
            return version
    for version in versions:
        if version.get("id") != target_id:
            return version
    return None


def mark_view_once(target_type, target_id):
    today = datetime.datetime.now().strftime("%Y%m%d")
    key = f"recipe_detail_view_{target_type}_{target_id}_{today}"
    if struct.session.has(key):
        return False
    struct.session.set(**{key: True})
    return True


def current_user():
    try:
        return struct.auth.current_user()
    except Exception:
        return None


def load():
    dish_id = wiz.request.query("dishId", True)
    selected_version_id = wiz.request.query("versionId", "")
    try:
        dish = struct.recipe.get_dish(dish_id, public=True)
        if dish is None:
            raise Exception("레시피를 찾을 수 없습니다.")
        rows, total = struct.recipe.versions(dish_id, public=True, page=1, dump=50)
        versions = [version_dto(row) for row in rows]
        selected = None
        selected_raw = None
        for row in rows:
            if row.get("id") == selected_version_id:
                selected_raw = row
                break
        if selected_raw is None and rows:
            selected_raw = rows[0]
        if selected_raw is not None:
            selected = version_dto(selected_raw)
        comparison = compare_versions(find_base_version(rows, selected_raw.get("id")) if selected_raw else None, selected_raw) if selected_raw else None
        source = source_dto(selected_raw) if selected_raw else {"available": False, "message": "승인된 레시피 버전이 없습니다."}
        user = current_user()
        if mark_view_once("dish", dish_id):
            dish["view_count"] = struct.recipe.increment_dish_view(dish_id)
        if selected_raw and mark_view_once("version", selected_raw.get("id")):
            selected["viewCount"] = struct.recipe.increment_version_view(selected_raw.get("id"))
        if user and selected_raw:
            try:
                struct.comment.record_recent_view(user.get("id"), selected_raw.get("id"))
            except Exception:
                pass
    except Exception as error:
        wiz.response.status(404, message=str(error))
    wiz.response.status(
        200,
        dish=dish_dto(dish),
        versions=versions,
        selectedVersion=selected,
        comparison=comparison,
        source=source,
        totalVersions=total,
        user=user,
        editRequestTypes=constants.EDIT_REQUEST_TYPES,
    )


def comments():
    version_id = wiz.request.query("versionId", True)
    page = to_int(wiz.request.query("page", 1), 1)
    dump = to_int(wiz.request.query("dump", 20), 20)
    try:
        rows, total = struct.comment.rows(version_id, page=page, dump=dump, visible_only=True)
        items = [comment_dto(row) for row in rows]
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, comments=items, page=page, dump=dump, total=total, empty=(total == 0))


def create_comment():
    data = parse_data()
    version_id = data.get("versionId") or wiz.request.query("versionId", "")
    try:
        user = struct.auth.require_login()
        comment_id = struct.comment.create(user.get("id"), version_id, data.get("content", ""))
        comment = struct.comment.comment_db.get(id=comment_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, comment=comment_dto(comment))


def create_edit_request():
    data = parse_data()
    version_id = data.get("versionId") or wiz.request.query("versionId", "")
    try:
        user = struct.auth.require_login()
        request_id = struct.comment.request_edit(
            user.get("id"),
            version_id,
            data.get("requestType", ""),
            data.get("content", ""),
            data.get("attachmentUrl", ""),
        )
        item = struct.comment.edit_request_db.get(id=request_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, editRequest=edit_request_dto(item))

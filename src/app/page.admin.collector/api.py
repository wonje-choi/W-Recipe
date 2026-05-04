import json

struct = wiz.model("portal/recipe/struct")
collector = struct.collector


def to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def request_data():
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


def selected_ids(data):
    ids = data.get("ids") or data.get("resultIds") or data.get("result_ids") or []
    if isinstance(ids, str):
        try:
            ids = json.loads(ids)
        except Exception:
            ids = [item.strip() for item in ids.split(",") if item.strip()]
    if not isinstance(ids, list):
        return []
    return [str(item) for item in ids if str(item).strip()]


def options():
    try:
        struct.require_admin()
        data = collector.options()
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **data)


def dashboard():
    try:
        struct.require_admin()
        requests, request_total = collector.list_requests(page=1, dump=8)
        results, result_total = collector.list_results(page=1, dump=12)
        data = {
            "requests": [collector.request_dto(item) for item in requests],
            "requestTotal": request_total,
            "results": [collector.result_dto(item) for item in results],
            "resultTotal": result_total,
            "statusSummary": collector.status_summary(),
            "options": collector.options(),
        }
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **data)


def create_request():
    try:
        struct.require_admin()
        item = collector.create_request(request_data(), requested_by=struct.session_user_id())
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(201, request=collector.request_dto(item))


def requests():
    page = to_int(wiz.request.query("page", 1), 1)
    dump = to_int(wiz.request.query("dump", 10), 10)
    status = wiz.request.query("status", "")
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = collector.list_requests(page=page, dump=dump, status=status, text=text)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=[collector.request_dto(item) for item in rows], page=page, dump=dump, total=total, empty=(total == 0), statusSummary=collector.status_summary())


def request_detail():
    request_id = wiz.request.query("id", "")
    try:
        struct.require_admin()
        item = collector.get_request(request_id)
        rows, total = collector.list_results(page=1, dump=100, request_id=request_id)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, request=collector.request_dto(item), results=[collector.result_dto(row) for row in rows], total=total)


def retry_request():
    data = request_data()
    try:
        struct.require_admin()
        item = collector.retry_request(data.get("id", ""))
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, request=collector.request_dto(item))


def delete_request():
    data = request_data()
    try:
        struct.require_admin()
        item = collector.delete_request(data.get("id", ""))
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, request=collector.request_dto(item))


def results():
    page = to_int(wiz.request.query("page", 1), 1)
    dump = to_int(wiz.request.query("dump", 20), 20)
    request_id = wiz.request.query("requestId", wiz.request.query("request_id", ""))
    result_type = wiz.request.query("resultType", wiz.request.query("result_type", ""))
    status = wiz.request.query("status", "")
    text = wiz.request.query("text", "")
    try:
        struct.require_admin()
        rows, total = collector.list_results(page=page, dump=dump, request_id=request_id, result_type=result_type, status=status, text=text)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, items=[collector.result_dto(item) for item in rows], page=page, dump=dump, total=total, empty=(total == 0))


def delete_results():
    data = request_data()
    try:
        struct.require_admin()
        deleted = collector.delete_results(selected_ids(data))
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, deleted=deleted)


def promote_results():
    data = request_data()
    try:
        struct.require_admin()
        ids = selected_ids(data)
        if not ids:
            raise Exception("레시피화할 수집 결과를 선택해주세요.")
        promoted = collector.promote_results_to_recipes(ids, reviewed_by=struct.session_user_id())
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **promoted)


def export_data():
    data = request_data()
    try:
        struct.require_admin()
        file_format = data.get("format") or data.get("fileFormat") or "json"
        result_type = data.get("resultType") or data.get("result_type") or ""
        text = data.get("text") or ""
        exported = collector.export_results(ids=selected_ids(data), result_type=result_type, text=text, file_format=file_format)
    except Exception as error:
        wiz.response.status(400, message=str(error))
    wiz.response.status(200, **exported)

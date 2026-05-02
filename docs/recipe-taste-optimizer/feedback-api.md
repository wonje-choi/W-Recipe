# 수정 요청과 신고 API

사용자가 공개 레시피에 대해 수정 요청을 남기고, 댓글 또는 레시피를 신고할 수 있는 API이다. 관리자 API는 요청과 신고의 상태를 변경하고 담당자와 관리자 메모를 저장한다.

## 수정 요청 유형

| 값 | 설명 |
| --- | --- |
| `error` | 오류 |
| `measurement_issue` | 계량 문제 |
| `source_issue` | 출처 문제 |
| `taste_improvement` | 맛 개선 요청 |
| `other` | 기타 |

## 수정 요청 생성

```http
POST /api/recipes/{version_id}/edit-requests
```

Form payload:

```json
{
  "data": "{\"requestType\":\"measurement_issue\",\"content\":\"소금 양이 너무 많아 보여요.\",\"attachmentUrl\":\"\"}"
}
```

- `user` controller를 사용하므로 로그인이 필요하다.
- 공개 레시피 버전에만 수정 요청을 생성할 수 있다.
- 같은 사용자가 같은 레시피 버전과 같은 요청 유형으로 `open` 상태 요청을 이미 만들었다면 기존 요청을 반환한다.

## 신고 사유와 대상

신고 대상:

| 값 | 설명 |
| --- | --- |
| `comment` | 댓글 |
| `recipe_version` | 레시피 버전 |
| `recipe_dish` | 레시피 |

신고 사유:

| 값 | 설명 |
| --- | --- |
| `spam` | 스팸 |
| `inappropriate` | 부적절한 내용 |
| `wrong_info` | 잘못된 정보 |
| `safety_issue` | 안전 문제 |
| `copyright` | 저작권 문제 |
| `other` | 기타 |

## 신고 생성

```http
POST /api/reports
```

Form payload:

```json
{
  "data": "{\"targetType\":\"comment\",\"targetId\":\"comment_id\",\"reason\":\"spam\",\"detail\":\"반복 광고 댓글입니다.\"}"
}
```

- `user` controller를 사용하므로 로그인이 필요하다.
- 같은 사용자가 같은 대상에 중복 신고하면 기존 신고를 반환한다.
- 댓글 신고가 새로 생성되면 댓글의 `report_count`를 증가시키고 상태를 `reported`로 변경한다.

## 관리자 수정 요청 목록

```http
GET /api/admin/edit-requests?status=open&page=1&dump=20
```

- `admin` controller를 사용한다.
- `status`, `userId`, `page`, `dump` 필터를 지원한다.

## 관리자 수정 요청 상태 변경

```http
PUT /api/admin/edit-requests/{request_id}/status
```

Form payload:

```json
{
  "data": "{\"status\":\"resolved\",\"adminMemo\":\"계량 표기를 수정했습니다.\"}"
}
```

- 상태 값은 `open`, `in_review`, `resolved`, `rejected` 중 하나다.
- 처리 시 `handled_by`, `handled_at`, `admin_memo`를 저장한다.
- `admin_action_log`에 변경 전후 값을 마스킹하여 기록한다.

## 관리자 신고 목록

```http
GET /api/admin/reports?status=open&targetType=comment&page=1&dump=20
```

- `admin` controller를 사용한다.
- `status`, `targetType`, `page`, `dump` 필터를 지원한다.

## 관리자 신고 상태 변경

```http
PUT /api/admin/reports/{report_id}/status
```

Form payload:

```json
{
  "data": "{\"status\":\"actioned\",\"adminMemo\":\"광고성 댓글로 숨김 처리했습니다.\"}"
}
```

- 상태 값은 `open`, `in_review`, `actioned`, `rejected` 중 하나다.
- 처리 시 `handled_by`, `handled_at`, `admin_memo`를 저장한다.
- `admin_action_log`에 변경 전후 값을 마스킹하여 기록한다.

## 데이터 모델

- `recipe_edit_request`: 사용자 수정 요청, 요청 유형, 첨부 URL, 관리자 메모와 처리 담당자를 저장한다.
- `recipe_report`: 신고 대상, 사유, 상세 내용, 관리자 메모와 처리 담당자를 저장한다.

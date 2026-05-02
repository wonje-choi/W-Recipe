# 관리자 승인/반려 워크플로 API

## 목적
AI 결과와 수집/작성된 레시피가 관리자 검수 전 공개되지 않도록 pending 목록, 승인, 반려 API를 제공한다.

## 권한
모든 endpoint는 `admin` controller를 사용한다.

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/reviews/pending` | 검수 대기 Dish, Version, AI 결과 목록 |
| POST | `/api/admin/reviews/<target_type>/<target_id>/approve` | 검수 대상 승인 |
| POST | `/api/admin/reviews/<target_type>/<target_id>/reject` | 검수 대상 반려 |

## target_type

| 입력값 | 정규화 값 | 대상 |
| --- | --- | --- |
| `dish`, `recipe`, `recipe_dish` | `recipe_dish` | Dish 상태 |
| `version`, `recipe_version` | `recipe_version` | Version 상태 |
| `ai`, `ai_modification`, `ai_recipe_modification` | `ai_modification` | AI 개량 결과 |

## 상태 전환

| 대상 | approve | reject |
| --- | --- | --- |
| Dish | `approved` | `rejected` |
| Version | `approved`, `reviewed_by`, `reviewed_at` 저장 | `rejected`, `reviewed_by`, `reviewed_at` 저장 |
| AI Modification | `approved`, `reviewed_by`, `reviewed_at` 저장 | `rejected`, `reviewed_by`, `reviewed_at`, `rejected_reason` 저장 |

## 요청 Payload
`reject`와 `approve`는 선택적으로 `reason`을 받을 수 있다.

```json
{
  "reason": "출처 확인이 필요합니다."
}
```

## AdminActionLog
- 승인 시 `action_type = review_approve`
- 반려 시 `action_type = review_reject`
- `target_type`은 정규화된 값으로 저장한다.
- 반려 사유는 DB 필드가 없는 대상(Dish/Version)의 경우 감사 로그 after 값에 `reviewReason`으로 남긴다.

## 공개 차단 정책
- 공개 Route는 `approved` 상태만 반환한다.
- `pending_review` 상태는 pending 목록에만 나타난다.
- `rejected` 상태는 공개 Route에서 제외된다.

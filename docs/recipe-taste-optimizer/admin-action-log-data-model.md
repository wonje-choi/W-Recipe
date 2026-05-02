# Recipe Taste Optimizer Admin Action Log Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0009
- **목적**: 관리자 권한 행위를 추적해 운영 감사와 문제 원인 분석이 가능한 DB 기반을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 | 역할 |
|---|---|---|---|
| AdminActionLog | `src/portal/recipe/model/db/admin_action_log.py` | `recipe_admin_action_log` | 관리자 주요 변경 행위 감사 로그 |

## 2. AdminActionLog 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 로그 ID |
| `adminUserId` | `admin_user_id` | Char(32) | 관리자 사용자 ID |
| `actionType` | `action_type` | Char(64) | 수행한 작업 유형 |
| `targetType` | `target_type` | Char(64) | 대상 유형 |
| `targetId` | `target_id` | Char(32) | 대상 ID |
| `beforeValue` | `before_value` | Text(JSON object) | 변경 전 값. 민감 정보 마스킹 필수 |
| `afterValue` | `after_value` | Text(JSON object) | 변경 후 값. 민감 정보 마스킹 필수 |
| `ipAddress` | `ip_address` | Char(64) | 요청 IP |
| `userAgent` | `user_agent` | Char(512) | User-Agent 요약 |
| `createdAt` | `created_at` | DateTime | 로그 생성 시각 |

## 3. 주요 actionType 후보

| actionType | 설명 |
|---|---|
| `recipe_create` | 레시피 생성 |
| `recipe_update` | 레시피 수정 |
| `recipe_hide` | 레시피 숨김 |
| `recipe_delete` | 레시피 삭제 또는 삭제 처리 |
| `recipe_approve` | 레시피 승인 |
| `recipe_reject` | 레시피 반려 |
| `ai_result_approve` | AI 결과 승인 |
| `ai_result_reject` | AI 결과 반려 |
| `ai_result_regenerate` | AI 결과 재생성 요청 |
| `user_role_update` | 사용자 권한 변경 |
| `user_suspend` | 사용자 정지 |
| `comment_hide` | 댓글 숨김 |
| `comment_delete` | 댓글 삭제 |
| `report_action` | 신고 조치 |
| `edit_request_resolve` | 수정 요청 처리 완료 |
| `source_retry` | 외부 자료 수집 재시도 |
| `prompt_update` | AI 프롬프트 수정 |

## 4. targetType 후보

| targetType | 설명 |
|---|---|
| `recipe_dish` | 요리 단위 |
| `recipe_version` | 레시피 버전 |
| `ai_modification` | AI 개량 결과 |
| `user` | 사용자 |
| `comment` | 댓글 |
| `report` | 신고 |
| `edit_request` | 수정 요청 |
| `crawled_source` | 외부 수집 자료 |
| `prompt` | AI 프롬프트 |
| `system` | 시스템 설정/운영 이벤트 |

## 5. 민감 정보 마스킹 정책

`before_value`, `after_value`에는 다음 값을 원문 저장하지 않는다.

- 비밀번호/비밀번호 해시
- 세션/토큰/API key
- 알레르기 원문 목록
- 아이 월령 등 민감한 개인화 정보
- 비선호 재료 원문 목록
- 원본 콘텐츠 전문

필요한 경우 다음처럼 요약 저장한다.

```json
{
  "allergies": "masked:3_items",
  "role": { "from": "user", "to": "admin" },
  "status": { "from": "pending_review", "to": "approved" }
}
```

## 6. 완료 판정

이 문서는 FN-20260501-0009의 완료 기준을 충족한다.

- AdminActionLog 모델을 정의했다.
- 레시피 승인/반려, 삭제, 사용자 권한 변경, 댓글 숨김 등 주요 actionType을 정의했다.
- before/after 값의 민감 정보 마스킹 정책을 문서화했다.

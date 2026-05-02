# 관리자 AI Management UI

`page.admin.ai`는 AI 결과 검수, 프롬프트 버전 관리, AI 처리 로그 확인을 제공하는 관리자 화면이다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/admin/ai` | 관리자 AI 관리 화면 |
| `/admin/ai?tab=logs&status=failed` | 실패 로그 필터 화면 |

## 화면 탭

| 탭 | 설명 |
| --- | --- |
| 검수 | AI 개량 결과 목록, 원본 요약, 변경점, 위험 요소, 승인/반려/재생성 액션 |
| 프롬프트 | 프롬프트 유형별 버전 등록, 수정, 활성화/비활성화 |
| 로그 | AI 생성/실패 로그, 프롬프트 버전, 토큰 사용량, 비용 추정치 |

## 앱 API

| 함수 | 설명 |
| --- | --- |
| `options()` | AI 상태, 로그 상태, 목적, 프롬프트 유형 옵션 반환 |
| `reviews()` | AI 개량 결과 목록 반환 |
| `review_action()` | AI 결과 승인 또는 반려 |
| `regenerate()` | 기존 AI 결과의 레시피 버전과 목적을 사용해 새 검수 대기 결과 생성 |
| `prompts()` | 프롬프트 템플릿 목록 반환 |
| `save_prompt()` | 프롬프트 템플릿 생성 또는 수정 |
| `prompt_action()` | 프롬프트 활성화 또는 비활성화 |
| `logs()` | AI 처리 로그 목록, 표시 토큰 합계, 표시 비용 합계 반환 |

## 검수 정보

AI 결과 상세 영역에는 다음 항목을 표시한다.

- 원본 요약
- 개량 재료와 조리 단계
- 개선 이유와 맛 보완 근거
- 저염 적합성 요약
- 이유식 적합성 요약
- 알레르기 경고
- 주의 문구
- Safety Struct가 탐지한 risk flag와 issue

## 상태 전환

- `approve`: `ai_recipe_modification.status`를 `approved`로 변경하고 검수자를 기록한다.
- `reject`: `ai_recipe_modification.status`를 `rejected`로 변경하고 반려 사유를 기록한다.
- `regenerate`: 같은 `recipe_version_id`, `purpose`, `target_user_type`으로 새 `pending_review` 결과를 생성한다.

변경 작업은 `admin_action_log`에 기록한다.

## 권한

`page.admin.ai`는 `admin` controller를 사용한다. 일반 사용자는 화면과 API를 사용할 수 없다.

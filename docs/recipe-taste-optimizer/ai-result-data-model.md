# Recipe Taste Optimizer AI Result and Processing Log Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0007
- **목적**: AI 개량 결과를 즉시 공개하지 않고 관리자 검수 가능한 상태로 저장하며, AI 처리 실패/비용/프롬프트 버전을 추적할 수 있는 DB 기반을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 | 역할 |
|---|---|---|---|
| AIRecipeModification | `src/portal/recipe/model/db/ai_recipe_modification.py` | `recipe_ai_modification` | AI 개량 결과와 검수 상태 저장 |
| AIProcessingLog | `src/portal/recipe/model/db/ai_processing_log.py` | `recipe_ai_processing_log` | AI 요청/응답 요약, 실패, 비용, 프롬프트 버전 로그 |

## 2. AIRecipeModification 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | AI 개량 결과 ID |
| `recipeVersionId` | `recipe_version_id` | Char(32) | 원본 레시피 버전 ID |
| `requestedBy` | `requested_by` | Char(32) | 요청 사용자 ID. 관리자 생성이면 빈 값 가능 |
| `purpose` | `purpose` | Char(32) | `low_sodium`, `baby_food`, `tastier` 등 |
| `targetUserType` | `target_user_type` | Char(64) | 대상 사용자. 예: 성인, 유아, 다이어트 사용자 |
| `originalSummary` | `original_summary` | Text | 원본 레시피 요약 |
| `modifiedIngredients` | `modified_ingredients` | Text(JSON array) | 변경된 재료와 계량 |
| `modifiedSteps` | `modified_steps` | Text(JSON array) | 개선된 조리 순서 |
| `improvementReason` | `improvement_reason` | Text | 변경 이유 |
| `tasteImprovementPoint` | `taste_improvement_point` | Text | 맛 보완 포인트 |
| `sodiumReductionPoint` | `sodium_reduction_point` | Text | 저염 개선 포인트 |
| `babyFoodSafetyNotes` | `baby_food_safety_notes` | Text | 이유식 안전 메모 |
| `allergenWarnings` | `allergen_warnings` | Text(JSON array) | 알레르기 경고 |
| `cautionNotes` | `caution_notes` | Text(JSON array) | 주의 문구 |
| `riskFlags` | `risk_flags` | Text(JSON array) | 관리자 검수 경고 플래그 |
| `status` | `status` | Char(32) | 기본값 `pending_review` |
| `reviewedBy` | `reviewed_by` | Char(32) | 검수 관리자 ID |
| `reviewedAt` | `reviewed_at` | DateTime nullable | 검수 시각 |
| `rejectedReason` | `rejected_reason` | Text | 반려 사유 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 3. AIProcessingLog 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | AI 처리 로그 ID |
| `requestType` | `request_type` | Char(64) | summary, modification, safety_check 등 |
| `targetId` | `target_id` | Char(32) | 대상 source/version/modification ID |
| `promptVersion` | `prompt_version` | Char(64) | 사용한 프롬프트 버전 |
| `inputSummary` | `input_summary` | Text | 입력 요약. 원문 전문 저장 금지 |
| `outputSummary` | `output_summary` | Text | 출력 요약 |
| `status` | `status` | Char(32) | `queued`, `processing`, `pending_review`, `approved`, `rejected`, `failed` |
| `errorMessage` | `error_message` | Text | 실패 사유 |
| `tokenUsage` | `token_usage` | Text(JSON object) | prompt/completion/total token 등 |
| `costEstimate` | `cost_estimate` | Decimal | 예상 비용 |
| `durationMs` | `duration_ms` | Integer | 처리 시간 |
| `startedAt` | `started_at` | DateTime nullable | 처리 시작 시각 |
| `finishedAt` | `finished_at` | DateTime nullable | 처리 종료 시각 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |

## 4. 공개/검수 정책

- AIRecipeModification은 기본적으로 `pending_review` 상태로 생성한다.
- `approved` 상태로 승인된 결과만 사용자 화면에 노출한다.
- `rejected`, `failed` 상태는 사용자에게 공개하지 않는다.
- 저염식, 이유식, 알레르기 포함 콘텐츠는 반드시 관리자 검수 후 공개한다.
- 위험 요소는 `risk_flags`, `allergen_warnings`, `caution_notes`에 구조화해 관리자 화면에 표시한다.

## 5. 로그 저장 정책

- `input_summary`에는 원문 전문이나 민감 정보를 저장하지 않는다.
- 알레르기, 아이 월령, 비선호 재료 등 개인화 정보는 원문 저장 대신 요약/마스킹한다.
- `prompt_version`을 반드시 저장해 결과 재현성과 프롬프트 회귀 분석이 가능하도록 한다.
- 실패 시 `error_message`를 저장하되 외부 API key, 개인정보, 원문 전문은 포함하지 않는다.

## 6. 완료 판정

이 문서는 FN-20260501-0007의 완료 기준을 충족한다.

- AIRecipeModification 모델을 정의했다.
- AIProcessingLog 모델을 정의했다.
- AI 실패/재생성/검수 이력을 연결할 수 있는 필드를 포함했다.
- AI 결과가 승인 전 공개되지 않는 상태 흐름을 명시했다.

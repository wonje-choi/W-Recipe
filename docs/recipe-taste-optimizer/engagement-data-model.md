# Recipe Taste Optimizer Engagement Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0008
- **목적**: 댓글, 즐겨찾기, 수정 요청, 신고 기능의 저장 기반과 중복 방지 정책을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 | 역할 |
|---|---|---|---|
| Comment | `src/portal/recipe/model/db/comment.py` | `recipe_comment` | 레시피 버전 댓글 |
| FavoriteRecipe | `src/portal/recipe/model/db/favorite_recipe.py` | `recipe_favorite` | 사용자별 저장 레시피 |
| RecipeEditRequest | `src/portal/recipe/model/db/recipe_edit_request.py` | `recipe_edit_request` | 오류/계량/출처/맛 개선 요청 |
| Report | `src/portal/recipe/model/db/report.py` | `recipe_report` | 댓글/레시피 신고 |

## 2. Comment 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 댓글 ID |
| `userId` | `user_id` | Char(32) | 작성자 ID |
| `recipeVersionId` | `recipe_version_id` | Char(32) | 대상 레시피 버전 ID |
| `content` | `content` | Text | 댓글 본문 |
| `status` | `status` | Char(32) | `visible`, `hidden`, `deleted`, `reported` |
| `reportCount` | `report_count` | Integer | 신고 누적 수 |
| `createdAt` | `created_at` | DateTime | 작성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 3. FavoriteRecipe 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 즐겨찾기 ID |
| `userId` | `user_id` | Char(32) | 사용자 ID |
| `recipeVersionId` | `recipe_version_id` | Char(32) | 저장한 레시피 버전 ID |
| `createdAt` | `created_at` | DateTime | 저장 시각 |

중복 저장을 막기 위해 `(user_id, recipe_version_id)` composite unique index를 사용한다.

## 4. RecipeEditRequest 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 수정 요청 ID |
| `userId` | `user_id` | Char(32) | 요청자 ID |
| `recipeVersionId` | `recipe_version_id` | Char(32) | 대상 레시피 버전 ID |
| `requestType` | `request_type` | Char(32) | 오류, 계량 문제, 출처 문제, 맛 개선 요청 등 |
| `content` | `content` | Text | 요청 내용 |
| `attachmentUrl` | `attachment_url` | Char(1024) | 첨부 링크 |
| `status` | `status` | Char(32) | `open`, `in_review`, `resolved`, `rejected` |
| `adminMemo` | `admin_memo` | Text | 관리자 메모 |
| `handledBy` | `handled_by` | Char(32) | 처리 관리자 ID |
| `handledAt` | `handled_at` | DateTime nullable | 처리 시각 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 5. Report 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 신고 ID |
| `reporterUserId` | `reporter_user_id` | Char(32) | 신고자 ID |
| `targetType` | `target_type` | Char(32) | `comment`, `recipe_version`, `recipe_dish` 등 |
| `targetId` | `target_id` | Char(32) | 신고 대상 ID |
| `reason` | `reason` | Text | 신고 사유 |
| `status` | `status` | Char(32) | `open`, `in_review`, `actioned`, `rejected` |
| `handledBy` | `handled_by` | Char(32) | 처리 관리자 ID |
| `handledAt` | `handled_at` | DateTime nullable | 처리 시각 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

동일 사용자의 동일 대상 반복 신고를 막기 위해 `(reporter_user_id, target_type, target_id)` composite unique index를 사용한다.

## 6. 권한/운영 정책

- guest는 댓글 조회만 가능하다.
- user/admin만 댓글 작성, 즐겨찾기, 수정 요청, 신고를 생성할 수 있다.
- 관리자는 댓글 숨김/삭제, 신고 처리, 수정 요청 상태 변경을 수행한다.
- 숨김/삭제/처리 상태 변경은 후속 AdminActionLog와 연결한다.
- 댓글 본문과 신고 사유는 XSS 방지를 위해 출력 시 escape 또는 sanitize한다.

## 7. 완료 판정

이 문서는 FN-20260501-0008의 완료 기준을 충족한다.

- Comment 모델을 정의했다.
- FavoriteRecipe 모델을 정의했다.
- RecipeEditRequest 모델을 정의했다.
- Report 모델을 정의했다.
- 사용자별 중복 즐겨찾기/중복 신고 방지 조건을 설계했다.

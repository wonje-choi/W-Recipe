# Recipe Taste Optimizer Core Recipe Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0005
- **목적**: 요리 단위와 레시피 버전을 분리해 하나의 요리에 여러 출처/AI 개량 버전을 연결할 수 있는 DB 기반을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 | 역할 |
|---|---|---|---|
| RecipeDish | `src/portal/recipe/model/db/recipe_dish.py` | `recipe_dish` | 요리 단위. 예: 된장찌개 |
| RecipeVersion | `src/portal/recipe/model/db/recipe_version.py` | `recipe_version` | 출처별/AI 개량별 레시피 버전 |

DB 필드는 Python/WIZ 관례에 맞춰 snake_case로 저장한다. API 응답 또는 프론트엔드 DTO에서는 필요 시 camelCase로 변환한다.

## 2. RecipeDish 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 요리 ID, primary key |
| `name` | `name` | Char(160) | 요리명 |
| `description` | `description` | Text | 간단 설명 |
| `category` | `category` | Char(64) | 대표 카테고리 |
| `tags` | `tags` | Text(JSON array) | 태그 목록 |
| `thumbnailUrl` | `thumbnail_url` | Char(1024) | 대표 이미지 URL |
| `viewCount` | `view_count` | Integer | 요리 단위 조회수 |
| `status` | `status` | Char(32) | 공개/검수 상태 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 3. RecipeVersion 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 레시피 버전 ID, primary key |
| `dishId` | `dish_id` | Char(32) | 연결된 요리 ID |
| `title` | `title` | Char(200) | 레시피 버전 제목 |
| `sourceType` | `source_type` | Char(32) | `youtube`, `blog`, `web`, `direct`, `ai_modified` |
| `sourceUrl` | `source_url` | Char(1024) | 원본 URL |
| `sourceTitle` | `source_title` | Char(300) | 원본 제목 |
| `sourceAuthor` | `source_author` | Char(160) | 원본 작성자/채널 |
| `sourceCollectedAt` | `source_collected_at` | DateTime nullable | 수집일 |
| `summary` | `summary` | Text | 요약 |
| `ingredients` | `ingredients` | Text(JSON array) | 재료와 계량 정보 |
| `steps` | `steps` | Text(JSON array) | 조리 순서 |
| `cookingTips` | `cooking_tips` | Text(JSON array) | 조리 팁 |
| `failurePreventionTips` | `failure_prevention_tips` | Text(JSON array) | 실패 방지 팁 |
| `substitutionTips` | `substitution_tips` | Text(JSON array) | 재료 대체안 |
| `nutritionInfo` | `nutrition_info` | Text(JSON object) | 영양 정보 |
| `sodiumInfo` | `sodium_info` | Text(JSON object) | 나트륨 관련 정보 |
| `allergenInfo` | `allergen_info` | Text(JSON array) | 알레르기 주의사항 |
| `difficulty` | `difficulty` | Char(16) | 난이도 |
| `cookingTime` | `cooking_time` | Integer | 예상 조리 시간, 분 단위 |
| `servingSize` | `serving_size` | Char(32) | 인분/분량 |
| `viewCount` | `view_count` | Integer | 버전 단위 조회수 |
| `aiModified` | `ai_modified` | Boolean | AI 개량 여부 |
| `status` | `status` | Char(32) | 검수/공개 상태 |
| `reviewedBy` | `reviewed_by` | Char(32) | 검수 관리자 ID |
| `reviewedAt` | `reviewed_at` | DateTime nullable | 검수 시각 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 4. JSON 필드 정책

Peewee/MySQL 호환성을 우선해 MVP에서는 JSON 성격의 데이터를 `TextField`에 JSON 문자열로 저장한다.

| 필드 | 기본값 | 구조 예시 |
|---|---|---|
| `tags` | `[]` | `["저염", "국/찌개"]` |
| `ingredients` | `[]` | `[{"name":"두부", "amount":"150g"}]` |
| `steps` | `[]` | `[{"order":1, "text":"재료를 손질한다."}]` |
| `nutrition_info` | `{}` | `{"calorie": 320, "protein": "20g"}` |
| `sodium_info` | `{}` | `{"estimatedMg": 650, "highSodiumIngredients":["된장"]}` |
| `allergen_info` | `[]` | `[{"name":"대두", "level":"주의"}]` |

Struct 계층에서 JSON encode/decode를 담당하고, API 계층은 이미 파싱된 list/dict를 반환하도록 설계한다.

## 5. 인덱스 전략

| 목적 | 필드 |
|---|---|
| 공개 레시피 조회 | `status` |
| 카테고리 필터 | `category` |
| 이름/제목 검색 보조 | `name`, `title` |
| 조회수 정렬 | `view_count` |
| 조리시간 정렬 | `cooking_time` |
| 난이도 필터/정렬 | `difficulty` |
| AI 개량 필터 | `ai_modified` |
| 요리별 버전 조회 | `dish_id` |
| 출처 유형 필터 | `source_type` |

## 6. 공개 조회 정책

공개 사용자 화면은 기본적으로 다음 조건을 모두 만족하는 데이터만 조회한다.

- `RecipeDish.status == approved`
- `RecipeVersion.status == approved`

관리자 화면은 상태 필터를 통해 Draft, Crawled, AI Parsed, AI Modified, Pending Review, Rejected, Hidden까지 조회할 수 있다.

## 7. 완료 판정

이 문서는 FN-20260501-0005의 완료 기준을 충족한다.

- RecipeDish 모델을 정의했다.
- RecipeVersion 모델을 정의했다.
- JSON 필드와 검색/필터/정렬 인덱스 전략을 정리했다.
- Approved 상태만 공개 조회되도록 기본 정책을 설계했다.

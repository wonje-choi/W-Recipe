# 관리자 레시피 CRUD API

## 목적
관리자가 레시피 Dish와 Version을 직접 생성, 수정, 숨김 처리할 수 있게 한다. 모든 변경은 `AdminActionLog`에 기록한다.

## 권한
모든 endpoint는 `admin` controller를 사용한다. 일반 사용자나 비로그인 사용자가 직접 호출하면 401로 차단된다.

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/recipes` | 전체 상태 레시피 목록 |
| POST | `/api/admin/recipes` | 레시피 Dish 생성 |
| GET | `/api/admin/recipes/<dish_id>` | 레시피 Dish 상세 |
| PUT | `/api/admin/recipes/<dish_id>` | 레시피 Dish 수정 |
| DELETE | `/api/admin/recipes/<dish_id>` | 레시피 Dish 숨김 처리 |
| GET | `/api/admin/recipes/<dish_id>/versions` | 전체 상태 Version 목록 |
| POST | `/api/admin/recipes/<dish_id>/versions` | Version 생성 |
| GET | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 상세 |
| PUT | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 수정 |
| DELETE | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 숨김 처리 |

## Payload 규칙
- `data` query/form 필드에 JSON 객체 문자열을 전달하거나 form-urlencoded 필드를 직접 전달한다.
- `tags`, `ingredients`, `steps`, `cookingTips`, `nutritionInfo`, `sodiumInfo`, `allergenInfo` 등은 JSON 문자열 또는 배열/객체 값으로 받는다.
- `thumbnailUrl`, `sourceUrl`, `sourceTitle`, `sourceAuthor`는 camelCase와 snake_case 모두 허용한다.

## Dish 필드

| API 필드 | DB 필드 |
| --- | --- |
| `name` | `name` |
| `description` | `description` |
| `category` | `category` |
| `tags` | `tags` |
| `thumbnailUrl` | `thumbnail_url` |
| `status` | `status` |

## Version 필드

| API 필드 | DB 필드 |
| --- | --- |
| `title` | `title` |
| `sourceType` | `source_type` |
| `sourceUrl` | `source_url` |
| `sourceTitle` | `source_title` |
| `sourceAuthor` | `source_author` |
| `sourceCollectedAt` | `source_collected_at` |
| `ingredients` | `ingredients` |
| `steps` | `steps` |
| `cookingTips` | `cooking_tips` |
| `failurePreventionTips` | `failure_prevention_tips` |
| `substitutionTips` | `substitution_tips` |
| `nutritionInfo` | `nutrition_info` |
| `sodiumInfo` | `sodium_info` |
| `allergenInfo` | `allergen_info` |
| `aiModified` | `ai_modified` |
| `status` | `status` |

## AdminActionLog

| 행위 | action_type | target_type |
| --- | --- | --- |
| Dish 생성 | `recipe_dish_create` | `recipe_dish` |
| Dish 수정 | `recipe_dish_update` | `recipe_dish` |
| Dish 숨김 | `recipe_dish_hide` | `recipe_dish` |
| Version 생성 | `recipe_version_create` | `recipe_version` |
| Version 수정 | `recipe_version_update` | `recipe_version` |
| Version 숨김 | `recipe_version_hide` | `recipe_version` |

삭제는 물리 삭제 대신 `hidden` 상태 변경으로 처리한다.

# 관리자 Recipe Management UI

`page.admin.recipes`는 운영자가 레시피 콘텐츠를 코드 수정 없이 등록, 수정, 공개, 숨김 처리할 수 있는 관리자 화면이다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/admin/recipes` | 관리자 레시피 목록과 편집 화면 |

## 사용 API

| API | Method | 용도 |
| --- | --- | --- |
| `/api/admin/recipes` | GET | 레시피 목록, 상태/카테고리/태그 검색 |
| `/api/admin/recipes` | POST | 레시피 Dish 생성 |
| `/api/admin/recipes/<dish_id>` | GET | 레시피 Dish 상세 조회 |
| `/api/admin/recipes/<dish_id>` | PUT | Dish 기본 정보와 상태 수정 |
| `/api/admin/recipes/<dish_id>` | DELETE | Dish 물리 삭제 대신 `hidden` 상태로 변경 |
| `/api/admin/recipes/<dish_id>/versions` | GET | Dish 하위 Version 목록 조회 |
| `/api/admin/recipes/<dish_id>/versions` | POST | Version 생성 |
| `/api/admin/recipes/<dish_id>/versions/<version_id>` | PUT | Version 상세 정보와 검수 상태 수정 |
| `/api/admin/recipes/<dish_id>/versions/<version_id>` | DELETE | Version 물리 삭제 대신 `hidden` 상태로 변경 |

화면 옵션은 앱 API `options()`에서 제공한다.

## 화면 구성

- 레시피 이름 검색
- 검수/공개 상태 필터
- 카테고리 필터
- 태그 필터
- 레시피 목록 테이블
- 새 레시피 등록 패널
- Dish 기본 정보 편집
- 대표 이미지 URL 편집
- 태그 선택
- Version별 출처, 조리 콘텐츠, 영양/안전 정보 편집

## 상태 관리

`draft`, `pending_review`, `approved`, `rejected`, `hidden` 등 `RECIPE_STATUSES` 값을 그대로 사용한다. 삭제성 액션은 실제 delete가 아니라 `hidden` 상태 변경으로 처리한다.

## 권한

`page.admin.recipes`는 `admin` controller를 사용한다. REST API도 `admin` controller로 보호되며 변경 작업은 `admin_action_log`에 기록된다.

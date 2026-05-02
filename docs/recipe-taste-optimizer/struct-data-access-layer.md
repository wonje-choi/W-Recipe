# Struct 기반 데이터 접근 계층

## 목적
Recipe Taste Optimizer는 화면과 API가 DB 모델을 직접 다루지 않고 `portal/recipe/struct`를 통해 도메인 단위로 접근한다. 이 계층은 기본 상태값, 공개 범위, 중복 방지, 감사 로그 마스킹 같은 정책을 한곳에 모은다.

## 진입점

```python
struct = wiz.model("portal/recipe/struct")
```

## 구성

| 속성 | 역할 |
| --- | --- |
| `struct.user` | 사용자, 로그인 기록, 취향 프로필 |
| `struct.recipe` | 레시피 Dish/Version 생성, 수정, 공개 검색, 조회수 |
| `struct.source` | 외부 URL 수집 이력, URL 해시 중복 판별, 크롤링 상태 |
| `struct.ai` | AI 개량 결과와 처리 로그, 관리자 승인/반려 |
| `struct.comment` | 댓글, 즐겨찾기, 수정 요청, 신고 |
| `struct.admin_log` | 관리자 감사 로그와 before/after 마스킹 |

## 공개 데이터 정책
- `struct.recipe.search_dishes()`는 status 기본값을 `approved`로 둔다.
- `struct.recipe.get_dish(..., public=True)`와 `get_version(..., public=True)`는 approved가 아니면 `None`을 반환한다.
- `struct.recipe.admin_search_dishes()`와 `struct.recipe.admin_versions()`는 `struct.require_admin()`을 통과한 뒤 전체 상태를 조회한다.
- AI 결과는 `pending_review`로 생성되며 `struct.ai.approve_modification()` 이후에만 공개 데이터로 승격될 수 있다.

## 반복 로직
- `struct.recipe.increment_dish_view()`와 `struct.recipe.increment_version_view()`는 조회수를 갱신한다.
- `struct.comment.toggle_favorite()`는 사용자/레시피 버전 조합을 기준으로 즐겨찾기를 추가하거나 제거한다.
- `struct.comment.hide()`는 댓글 숨김 상태와 조치자, 사유를 함께 저장한다.

## 민감 정보 정책
- `struct.mask_sensitive()`는 password, token, apiKey, rawContent, medicalNotes, allergies 등 민감 필드를 원문 대신 요약 문자열로 치환한다.
- `struct.admin_log.create()`는 before/after 값을 저장하기 전에 항상 마스킹을 수행한다.

## 초기화 정책
- `Struct` 생성 시 recipe 패키지 DB 모델 테이블을 `safe=True`로 생성한다.
- 테이블 생성 실패는 기존 테이블/권한/환경 차이를 고려해 무시하고, 실제 CRUD 실패는 호출 계층에서 처리한다.

# 레시피 목록 페이지 UI

`page.recipe.list`는 공개 레시피 탐색 화면이다. `viewuri`는 `/recipes/:preset?`이며 `layout.recipe`를 사용한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/recipes` | 전체 승인 레시피 |
| `/recipes/low-sodium` | 저염 레시피 preset |
| `/recipes/baby-food` | 이유식 레시피 preset |

## 필터와 정렬

- 검색어: `text`
- 카테고리: `category`
- 태그: `tag`
- 정렬: `view_count`, `latest`, `popular`, `difficulty`, `cooking_time`, `ai_modified`
- 페이지: `page`

목록 데이터는 `page.recipe.list/api.py`의 `search()` 함수가 `struct.recipe.search_dishes()`를 호출해 구성한다. 기본적으로 공개 승인 상태의 레시피만 반환한다.

## UI 상태

- 로딩 스켈레톤
- 검색 결과 없음 상태
- 이미지 없음 배지
- 모바일 필터 접기/열기
- 페이지네이션
- `/recipes/low-sodium` preset의 나트륨 확인 포인트, 맛 보완 재료, 건강 주의 문구
- `/recipes/baby-food` preset의 월령 단계 필터, 알레르기/질식 위험 표시, 보호자 확인 문구

## 연결

- 카드 클릭: `/recipes/detail/{dish_id}`
- 검색/필터 적용: 현재 필터 값을 URL query string으로 반영
- preset 버튼: `/recipes`, `/recipes/low-sodium`, `/recipes/baby-food`로 이동

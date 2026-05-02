# 메인페이지 UI

`page.recipe.home`은 Recipe Taste Optimizer의 공개 메인 화면이다. `viewuri`는 `/`이고, 공통 레이아웃 `layout.recipe`를 사용한다.

## 화면 구성

- Hero 영역: 서비스명, 검색창, 추천 키워드, 저염식/이유식/AI 개량 요청 진입 버튼
- 인기 레시피: 조회수순 승인 레시피 3개
- 최신 업데이트: 최신순 승인 레시피 목록
- 랜덤 레시피: 승인 레시피 풀에서 2개 선택
- 특수식단 개선: 원본/개량 포인트 비교 패널

## 데이터 로딩

`page.recipe.home/api.py`의 `load()` 함수가 데이터를 조합한다.

| 응답 필드 | 설명 |
| --- | --- |
| `popular` | `view_count` 기준 3개 |
| `randomItems` | 승인 레시피 풀에서 2개 |
| `latest` | 최신 승인 레시피 |
| `keywords` | 추천 검색 키워드 |

모든 목록은 `struct.recipe.search_dishes()`를 사용하므로 공개 상태인 `approved` 레시피만 반환한다.

## 탐색

- 검색: `/recipes?text={query}`
- 저염식: `/recipes/low-sodium`
- 이유식: `/recipes/baby-food`
- AI 개량 요청: `/ai/modify`
- 레시피 카드: `/recipes/{dish_id}`

대상 페이지는 이후 UI 작업에서 구현한다.

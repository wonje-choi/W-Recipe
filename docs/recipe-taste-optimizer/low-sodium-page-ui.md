# 저염레시피 페이지 UI

저염레시피 화면은 `page.recipe.list`의 `/recipes/low-sodium` preset 화면으로 구현한다. 별도 Source App을 같은 경로에 추가하면 `/recipes/:preset?` 목록 라우트와 충돌하므로 기존 목록 화면을 저염 전용 상태로 확장한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/recipes/low-sodium` | 저염 카테고리/태그가 적용된 승인 레시피 목록 |

## 데이터 확장

`page.recipe.list/api.py`의 `search()`는 `preset=low-sodium`일 때 각 Dish의 대표 승인 Version을 조회해 `lowSodiumPreview`를 추가한다.

| 필드 | 설명 |
| --- | --- |
| `sodiumPoints` | Version의 `sodium_info`에서 추출한 나트륨 관련 표시 항목 |
| `sodiumIngredients` | 소금, 간장, 장류, 젓갈, 가공육 등 나트륨 주의 재료 후보 |
| `flavorTips` | `cooking_tips`, `substitution_tips` 기반 맛 보완 팁 |
| `aiModified` | 일반 레시피에서 AI로 저염 개량된 버전 여부 |

## UI 구성

- 저염 전용 헤더 문구
- 나트륨 확인 포인트 안내
- 맛 보완 재료 swatch 목록
- 건강 관련 고정 주의 문구
- 카드별 저염 포인트, 나트륨 주의 재료, 맛 보완 팁
- AI 저염 개량 버전과 저염 원본 버전 구분 배지

## 정책

저염 정보는 요리 탐색을 돕는 표시이며 의료 조언처럼 표현하지 않는다. 개인 질환의 진단, 치료, 영양 처방으로 보이지 않도록 고정 주의 문구를 노출한다.

# AI 개량 요청 UI

`page.recipe.ai.modify`는 로그인 사용자가 승인 레시피 버전을 선택해 AI 개량 요청을 저장하는 화면이다. `viewuri`는 `/ai/modify`이며 `layout.recipe`를 사용한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/ai/modify` | AI 레시피 개량 요청 화면 |

## 입력 흐름

1. 승인 레시피의 대표 Version을 대상 레시피로 선택한다.
2. 개량 목적을 선택한다.
3. 대상 사용자, 제외 재료, 알레르기, 원하는 조리 시간, 맛 방향, 추가 요청사항을 입력한다.
4. 요청을 저장하면 `pending_review` 상태의 AI 개량 결과로 저장된다.

## 개량 목적

| 목적 | 저장 값 | 설명 |
| --- | --- | --- |
| 저염식 | `low_sodium` | 나트륨 부담을 낮추고 맛 보완 포인트를 생성 |
| 이유식 | `baby_food` | 월령, 질감, 알레르기, 안전 주의 중심으로 개량 |
| 더 맛있게 | `tastier` | 풍미와 식감 개선 |
| 조리시간 단축 | `shorter_time` | 조리 단계와 시간을 줄이는 방향 |
| 재료 단순화 | `simpler_ingredients` | 핵심 재료 중심으로 간소화 |
| 고단백 | `high_protein` | 단백질 재료 보강 |

## API 함수

| 함수 | 설명 |
| --- | --- |
| `load()` | 로그인 사용자, 대상 레시피 후보, 목적 옵션, 정책 문구 반환 |
| `search_recipes()` | 대상 레시피 후보 검색 |
| `submit()` | 로그인 사용자 AI 개량 요청 저장 |

`submit()`은 `struct.auth.current_user()`가 없으면 401을 반환한다. 저장은 `struct.ai_diet.create()`를 통해 수행하며, 결과는 관리자 검수 전 공개되지 않는 `pending_review` 상태다.

## 로그인 모달 연동

AI 요청 페이지는 비로그인 상태에서 `recipe-open-login` window event를 발생시켜 `layout.recipe`의 공통 로그인 모달을 연다.

## 정책

- AI 개량 결과는 승인 전 공개 레시피로 노출하지 않는다.
- 저염식과 이유식 목적은 안전/주의 문구를 포함하며 관리자 검수 대상이다.
- 추가 요청사항은 `taste_direction`에 병합해 개량 근거 생성에 사용한다.

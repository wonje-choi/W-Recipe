# 레시피 상세 페이지 UI

`page.recipe.detail`은 공개 승인 레시피의 상세 탐색 화면이다. `viewuri`는 `/recipes/detail/:dishId`이며 `layout.recipe`를 사용한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/recipes/detail/:dishId` | 요리 상세 기본 화면 |
| `/recipes/detail/:dishId?version={version_id}` | 특정 승인 버전 선택 화면 |

상세 경로는 `/recipes/low-sodium`, `/recipes/baby-food` 같은 목록 preset 경로와 충돌하지 않도록 `detail` 세그먼트를 사용한다.

## 데이터 구성

- Dish 기본 정보: 이름, 설명, 카테고리, 태그, 대표 이미지, 조회수
- Version 목록: 승인 버전만 조회수순으로 표시
- 선택 Version: 재료/계량, 조리 순서, 맛 팁, 실패 방지 팁, 대체 재료, 영양/나트륨/알레르기 정보
- 비교 데이터: 기준 원본 버전과 선택 버전의 재료, 조리 순서, 영양, 나트륨 변경 여부
- 출처: 원본 제목, 작성자/유형, 수집일, 원본 이동 링크
- 사용자 상호작용: 댓글 조회/작성, 수정 요청 접수

## API 함수

| 함수 | 설명 |
| --- | --- |
| `load()` | Dish, Version 목록, 선택 Version, 출처, 비교, 로그인 사용자 정보를 반환 |
| `comments()` | 선택 Version의 공개 댓글 목록 반환 |
| `create_comment()` | 로그인 사용자 댓글 작성 |
| `create_edit_request()` | 로그인 사용자 수정 요청 작성 |

`load()`는 공개 승인 상태만 조회하고, 동일 세션 기준 일 1회 조회수 증가를 적용한다. 로그인 사용자가 상세를 열면 최근 본 레시피 기록도 갱신한다.

## UI 상태

- 로딩 스켈레톤
- 레시피 없음 오류 상태
- 이미지 없음 배지
- 승인 버전 없음 상태
- 출처 링크 없음 상태
- 댓글 없음 상태
- 로그인 전 댓글/수정요청 제한 상태

## 연결

- 목록/메인 카드 클릭: `/recipes/detail/{dish_id}`
- 버전 선택: `/recipes/detail/{dish_id}?version={version_id}`
- 원본 이동: 새 창으로 source URL 열기

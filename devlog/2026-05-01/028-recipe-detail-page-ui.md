# Recipe Taste Optimizer 레시피 상세 페이지 UI 구현

- **ID**: 028
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
공개 승인 레시피의 상세 페이지 `page.recipe.detail`을 구현했다. 요리 기본 정보, 승인 버전 목록, 선택 버전의 재료/조리 순서/팁/영양 정보, 원본·AI 비교, 출처 링크, 댓글 작성, 수정 요청 접수를 한 화면에서 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.detail/app.json`: `/recipes/detail/:dishId` 상세 페이지와 `layout.recipe` 연결을 정의했다.
- `src/app/page.recipe.detail/api.py`: 상세 데이터 로드, 댓글 목록/작성, 수정 요청 생성 API를 추가했다.
- `src/app/page.recipe.detail/view.ts`: URL 버전 선택, 상세 데이터 로드, 댓글 작성, 수정 요청 제출, 표시 헬퍼를 구현했다.
- `src/app/page.recipe.detail/view.pug`: 상세 헤더, 버전 목록, 재료/순서/팁/영양/출처/비교/댓글/수정요청 UI를 구현했다.
- `src/app/page.recipe.detail/view.scss`: Page host와 입력 요소 안정화 스타일을 추가했다.

### 연결 변경
- `src/app/page.recipe.list/view.ts`: 카드 클릭 경로를 `/recipes/detail/{dish_id}`로 변경했다.
- `src/app/page.recipe.home/view.ts`: 메인 카드 클릭 경로를 `/recipes/detail/{dish_id}`로 변경했다.

### 문서
- `docs/recipe-taste-optimizer/recipe-detail-ui.md`: 상세 페이지 경로, 데이터 구성, API 함수, UI 상태를 문서화했다.
- `docs/recipe-taste-optimizer/recipe-list-ui.md`: 카드 클릭 경로를 상세 페이지 경로로 갱신했다.
- `src/portal/recipe/README.md`: 공개 프론트엔드 페이지 경로 표를 추가했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 상세 페이지 API 문법 검사 통과.
- 신규 Page App과 API 함수 반영을 위해 clean WIZ build 수행, 빌드 성공.
- 빌드 후 generated routing에서 `/recipes/:preset?`와 `/recipes/detail/:dishId`가 별도 경로로 생성되는 것을 확인했다.

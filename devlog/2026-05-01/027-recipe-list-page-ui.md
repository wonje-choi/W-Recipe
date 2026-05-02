# Recipe Taste Optimizer 레시피 목록 페이지 UI 구현

- **ID**: 027
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
공개 레시피 목록 페이지 `page.recipe.list`를 구현했다. `/recipes`, `/recipes/low-sodium`, `/recipes/baby-food` 경로에서 검색어, 카테고리, 태그, 정렬, 페이지네이션을 제공하고 승인 레시피 카드 목록을 표시한다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.list/app.json`: `/recipes/:preset?` 공개 목록 페이지와 `layout.recipe` 연결을 정의했다.
- `src/app/page.recipe.list/api.py`: 필터/정렬/페이지네이션 기반 승인 레시피 검색 API를 추가했다.
- `src/app/page.recipe.list/view.ts`: URL query 동기화, 필터 상태, preset 이동, 페이지네이션, 이미지 fallback 로직을 구현했다.
- `src/app/page.recipe.list/view.pug`: 검색창, 모바일 필터 토글, 카테고리/태그/정렬 컨트롤, 카드 목록, 빈 상태, 이미지 없음 배지를 구현했다.
- `src/app/page.recipe.list/view.scss`: Page host와 line clamp 스타일을 추가했다.

### 문서
- `docs/recipe-taste-optimizer/recipe-list-ui.md`: 목록 페이지 경로, 필터, UI 상태, 연결 규칙을 문서화했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 페이지 API 문법 검사 통과.
- 신규 Page App과 API 함수 반영을 위해 clean WIZ build 수행, 빌드 성공.
- 첫 빌드에서 Pug가 `#{{ filters.tag }}`를 id 문법으로 해석한 오류를 확인하고 `{{ '#' + filters.tag }}`로 수정한 뒤 재빌드 성공.

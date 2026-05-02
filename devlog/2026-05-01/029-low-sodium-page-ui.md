# Recipe Taste Optimizer 저염레시피 페이지 UI 구현

- **ID**: 029
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
`/recipes/low-sodium` preset 화면을 저염레시피 전용 탐색 화면으로 확장했다. 기존 `page.recipe.list` 경로를 유지하면서 나트륨 확인 포인트, 맛 보완 재료, AI 저염 개량 구분, 건강 관련 주의 문구를 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.list/api.py`: `preset=low-sodium`일 때 대표 승인 Version의 나트륨 정보, 나트륨 주의 재료, 맛 보완 팁, AI 개량 여부를 `lowSodiumPreview`로 반환하도록 확장했다.
- `src/app/page.recipe.list/view.ts`: 저염 preset 판별과 카드별 저염 preview 접근 헬퍼를 추가했다.
- `src/app/page.recipe.list/view.pug`: 저염 전용 헤더 문구, 나트륨 확인 안내, 맛 보완 재료 swatch, 건강 주의 문구, 카드별 저염 포인트와 AI 개량 배지를 추가했다.

### 문서
- `docs/recipe-taste-optimizer/low-sodium-page-ui.md`: 저염 페이지 구현 방식, 데이터 확장, UI 구성, 정책을 문서화했다.
- `docs/recipe-taste-optimizer/recipe-list-ui.md`: 저염 preset 전용 UI 상태를 추가했다.
- `src/portal/recipe/README.md`: 목록 Page App 설명에 저염 preset 전용 표시를 반영했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 목록 API 문법 검사 통과.
- 기존 API 함수 내용 수정이므로 일반 WIZ build 수행, 빌드 성공.

## 설계 메모
별도 Source App을 `/recipes/low-sodium`에 추가하면 기존 `/recipes/:preset?` 라우트와 충돌할 수 있어, 동일 URL preset을 유지한 채 `page.recipe.list` 안에서 저염 전용 화면 상태로 확장했다.

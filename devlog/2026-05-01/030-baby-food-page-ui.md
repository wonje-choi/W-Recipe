# Recipe Taste Optimizer 이유식레시피 페이지 UI 구현

- **ID**: 030
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
`/recipes/baby-food` preset 화면을 이유식 전용 탐색 화면으로 확장했다. 초기/중기/후기/완료기 단계 필터, 권장 월령, 입자 크기, 보관/냉동 안내, 알레르기 후보, 안전 경고, 보호자 확인 문구를 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.list/api.py`: 이유식 단계 기준, 안전 경고 키워드, 알레르기 후보 추출, `babyPreview` 응답을 추가했다.
- `src/app/page.recipe.list/view.ts`: 이유식 preset 판별, 단계 옵션, 선택 단계 label, 카드별 이유식 preview 접근 헬퍼를 추가했다.
- `src/app/page.recipe.list/view.pug`: 이유식 전용 헤더, 월령 단계 필터, 안전 키워드, 보호자 안내, 카드별 월령/입자/보관/냉동/알레르기/경고 표시를 추가했다.

### 문서
- `docs/recipe-taste-optimizer/baby-food-page-ui.md`: 이유식 페이지 경로, 단계 기준, 데이터 확장, UI 구성, 정책을 문서화했다.
- `docs/recipe-taste-optimizer/recipe-list-ui.md`: 이유식 preset 전용 UI 상태를 추가했다.
- `src/portal/recipe/README.md`: 목록 Page App 설명에 이유식 preset 전용 표시를 반영했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 목록 API 문법 검사 통과.
- 기존 API 함수 내용 수정이므로 일반 WIZ build 수행, 빌드 성공.

## 설계 메모
별도 Source App 대신 `/recipes/:preset?` 목록 라우트를 유지했다. 이유식 전용 화면은 `preset=baby-food`와 `babyStage` query를 기준으로 같은 Page App에서 분기한다.

# Recipe Taste Optimizer 메인페이지 UI 구현

- **ID**: 026
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
Recipe Taste Optimizer 공개 메인페이지 `page.recipe.home`을 `/` 경로에 구현했다. Hero 검색, 추천 키워드, 저염식/이유식/AI 개량 요청 진입, 인기 레시피, 최신 업데이트, 랜덤 레시피, 특수식단 비교 패널을 구성했다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.home/app.json`: `/` 공개 메인페이지와 `layout.recipe` 연결을 정의했다.
- `src/app/page.recipe.home/api.py`: 승인 레시피 기준 인기/최신/랜덤 데이터와 추천 키워드를 조합하는 `load()` API를 추가했다.
- `src/app/page.recipe.home/view.ts`: 메인페이지 데이터 로딩, 검색 이동, 레시피 상세 이동, 이미지 fallback 로직을 구현했다.
- `src/app/page.recipe.home/view.pug`: Hero, 검색, 추천 키워드, 인기/최신/랜덤 레시피, 특수식단 비교 UI를 구현했다.
- `src/app/page.recipe.home/view.scss`: Page host와 line clamp 스타일을 추가했다.

### 문서
- `docs/recipe-taste-optimizer/main-page-ui.md`: 메인페이지 화면 구성과 데이터 로딩 정책을 문서화했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 페이지 API 문법 검사 통과.
- 신규 Page App과 API 함수 반영을 위해 clean WIZ build 수행, 빌드 성공.

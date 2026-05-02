# 로그인 사용자 맞춤 레시피 추천 섹션 구현

- **ID**: 050
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
즐겨찾기, 최근 조회, 사용자 선호 식단을 기반으로 승인 레시피를 점수화하는 추천 로직을 추가했다.
홈 API는 로그인 사용자에게만 `recommended` 배열을 반환하고, 홈 화면은 추천 항목이 있을 때만 "맞춤 추천" 섹션을 인기 레시피 위에 표시한다.

## 변경 파일 목록
- `src/portal/recipe/model/struct/recipe.py`: `get_recommended(user_id, limit=6)` 추가
- `src/app/page.recipe.home/api.py`: 로그인 사용자 추천 데이터 반환 추가
- `src/app/page.recipe.home/view.ts`: `recommended` 상태 바인딩 추가
- `src/app/page.recipe.home/view.pug`: "맞춤 추천" 섹션 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 홈 템플릿 문법 확인
- 비로그인 사용자는 `recommended`가 빈 배열이라 기존 인기/최신/랜덤 섹션만 표시되는 흐름 확인

# Recipe Taste Optimizer 공개 레시피 조회 API 구현

- **ID**: 013
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
비로그인 사용자가 승인된 레시피 목록, 상세, 버전 목록을 조회할 수 있도록 공개 Route를 추가했다. 목록은 검색/카테고리/태그/정렬/페이지네이션을 지원하며, 상세와 버전 목록은 `approved` 상태의 Dish/Version만 반환한다.

## 변경 파일 목록

### Route
- `src/route/recipe-public-list/app.json` — `/api/recipes` 공개 목록 Route 설정
- `src/route/recipe-public-list/controller.py` — 공개 레시피 목록 조회, 필터, 정렬, 페이지네이션 응답 구현
- `src/route/recipe-public-detail/app.json` — `/api/recipes/<path:path>` 공개 상세 Route 설정
- `src/route/recipe-public-detail/controller.py` — 요리 상세와 승인 버전 목록 조회 응답 구현

### 문서
- `docs/recipe-taste-optimizer/public-recipe-api.md` — 공개 API URL, query, 응답 형식, 오류 정책 정리
- `src/portal/recipe/README.md` — Public Routes 섹션 추가

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

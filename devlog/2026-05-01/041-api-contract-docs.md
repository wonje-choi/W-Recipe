# Recipe Taste Optimizer API 문서와 화면 계약 정리

- **ID**: 041
- **날짜**: 2026-05-01
- **유형**: 문서 업데이트

## 작업 요약
Recipe Taste Optimizer의 화면 App API와 REST Route 계약을 한 문서로 정리했다. Auth, User/Mypage, Public Recipe, Admin Recipe, Review, AI, Comment/Favorite/Edit Request/Report, Crawled Source, Admin Logs/Dashboard API를 role, method/path, 요청 필드, 응답 키 기준으로 구분했다.

공통 응답 envelope, form-urlencoded 요청 규칙, CSRF 헤더, 페이지네이션, DTO 구조, 오류 응답 형식, 상태값 목록과 주요 요청/응답 예시를 포함했다. README에는 API 계약 문서 링크를 추가했다.

## 변경 파일 목록
- `src/portal/recipe/API.md`: 상세 API 계약 문서 신규 작성
- `src/portal/recipe/README.md`: API.md 참조 링크 추가

## 검증
- VS Code diagnostics: `API.md`, `README.md` 오류 없음

# Recipe Taste Optimizer 관리자 승인/반려 워크플로 API 구현

- **ID**: 016
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
검수 전 콘텐츠가 공개되지 않도록 관리자 pending 목록, 승인, 반려 API를 추가했다. Dish, Version, AI Modification을 공통 target_type 패턴으로 처리하고 승인/반려 시 AdminActionLog를 남기도록 구현했다.

## 변경 파일 목록

### Route
- `src/route/recipe-admin-review/app.json` — `/api/admin/reviews/<path:path>` 관리자 검수 Route 설정
- `src/route/recipe-admin-review/controller.py` — pending 목록, approve, reject 처리와 감사 로그 연결 구현

### 문서
- `docs/recipe-taste-optimizer/admin-review-workflow-api.md` — 검수 API URL, target_type, 상태 전환, 감사 로그 정책 정리
- `src/portal/recipe/README.md` — Review Routes 섹션 추가

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

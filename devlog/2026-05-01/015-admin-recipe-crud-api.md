# Recipe Taste Optimizer 관리자 레시피 CRUD API 구현

- **ID**: 015
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 레시피 Dish와 Version을 직접 생성, 수정, 숨김 처리할 수 있도록 관리자 Route를 추가했다. 모든 변경은 AdminActionLog에 남기고, 감사 로그의 before/after 값에 datetime이 포함되어도 JSON 저장이 가능하도록 공통 직렬화를 보강했다.

## 변경 파일 목록

### Route
- `src/route/recipe-admin-list/app.json` — `/api/admin/recipes` 관리자 목록/생성 Route 설정
- `src/route/recipe-admin-list/controller.py` — 관리자 전체 상태 목록 조회와 Dish 생성 구현
- `src/route/recipe-admin-detail/app.json` — `/api/admin/recipes/<path:path>` 관리자 상세 Route 설정
- `src/route/recipe-admin-detail/controller.py` — Dish 상세/수정/숨김, Version 목록/생성/상세/수정/숨김 구현

### Portal Package
- `src/portal/recipe/model/struct.py` — AdminActionLog before/after datetime 직렬화 지원
- `src/portal/recipe/README.md` — Admin Routes 섹션 추가

### 문서
- `docs/recipe-taste-optimizer/admin-recipe-crud-api.md` — 관리자 CRUD URL, payload 매핑, 감사 로그 actionType 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

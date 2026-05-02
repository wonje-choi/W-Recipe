# Recipe Taste Optimizer AI 레시피 요약 파이프라인 구현

- **ID**: 019
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
YouTube, blog, web URL 또는 직접 입력 텍스트를 레시피 구조 후보로 변환하는 관리자용 AI 요약 파이프라인을 추가했다. 외부 AI SDK가 없는 MVP 환경에서는 내장 규칙 기반 파이프라인으로 재료, 조리 단계, 팁, 불확실성 후보를 추출하고, 결과를 검수 대기 Dish/Version과 AIProcessingLog로 저장한다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/struct/ai.py` — `parse_recipe_summary()`와 내장 `recipe_summary:heuristic-v1` 프롬프트 fallback, 출처 연결, 후보 추출, 로그 완료/실패 처리 구현
- `src/portal/recipe/README.md` — 관리자 AI 요약 Route, 요약 파이프라인 정책, 불확실성 저장 규칙 추가

### Route
- `src/route/recipe-admin-ai-summary/app.json` — `/api/admin/ai/recipe-summary` 관리자 Route 설정
- `src/route/recipe-admin-ai-summary/controller.py` — URL/직접 입력 payload를 받아 요약 파이프라인 실행, Dish/Version/Source/Log DTO 반환 구현

### 문서
- `docs/recipe-taste-optimizer/admin-ai-recipe-summary-api.md` — AI 레시피 요약 API, payload, 처리 규칙, 응답, 감사 로그 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

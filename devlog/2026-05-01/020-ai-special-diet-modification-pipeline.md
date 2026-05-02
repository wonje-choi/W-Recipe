# Recipe Taste Optimizer AI 특수식단 개량 파이프라인 구현

- **ID**: 020
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
기존 레시피 버전을 저염식, 이유식, 다이어트식, 고단백식 등 특수식단 목적에 맞게 개량 요청하는 파이프라인을 추가했다. 로그인 사용자 또는 관리자가 요청하면 목적, 대상 사용자, 제외 재료, 알레르기, 원하는 조리 시간, 맛 방향을 반영해 `ai_recipe_modification`에 `pending_review` 결과와 AIProcessingLog를 저장한다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/struct/ai_diet.py` — 특수식단 개량 요청 처리, 목적별 프롬프트 fallback, 재료/단계/주의사항 구조화 구현
- `src/portal/recipe/model/struct.py` — `struct.ai_diet` 진입점 추가
- `src/portal/recipe/README.md` — 특수식단 개량 Route, Struct, 정책 문서 갱신

### Route
- `src/route/recipe-ai-modification/app.json` — `/api/ai/recipe-modifications` 로그인 사용자 Route 설정
- `src/route/recipe-ai-modification/controller.py` — 특수식단 개량 요청 payload 처리, Modification/Log DTO 응답 구현

### 문서
- `docs/recipe-taste-optimizer/ai-special-diet-modification-api.md` — API payload, purpose 값, 처리 규칙, prompt fallback 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

# Recipe Taste Optimizer AI 안전성 체크 로직 구현

- **ID**: 021
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
AI 생성 결과를 관리자 검수 전에 안전성 관점으로 확인할 수 있도록 Safety Struct와 검수 DTO 확장을 구현했다. 알레르기, 고나트륨 재료, 이유식 부적합 재료, 생식/질식 위험, 의료적 치료/예방 보장 표현을 탐지하고 `riskFlags`와 `safety` 요약으로 반환한다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/struct/safety.py` — 위험 후보 탐지 로직과 Version/AI Modification 검사 함수 추가
- `src/portal/recipe/model/struct.py` — `struct.safety` 진입점 추가
- `src/portal/recipe/model/struct/ai_diet.py` — 특수식단 개량 결과 생성 시 Safety risk flags 병합
- `src/portal/recipe/README.md` — Safety Struct와 관리자 검수 safety/riskFlags 정책 문서 갱신

### Route
- `src/route/recipe-admin-review/controller.py` — pending review Version/AI Modification DTO에 `safety`, `riskFlags` 포함

### 문서
- `docs/recipe-taste-optimizer/ai-safety-checks.md` — 탐지 risk flag, Struct API, 검수 API 응답 형식 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 기존 Route 수정이므로 WIZ 일반 빌드 수행 및 성공.

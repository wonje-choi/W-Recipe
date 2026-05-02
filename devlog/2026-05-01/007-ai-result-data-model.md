# Recipe Taste Optimizer AI 개량 결과와 처리 로그 모델 구현

- **ID**: 007
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
AI 개량 결과를 검수 가능한 상태로 저장하는 모델과 AI 처리 로그 모델을 추가했다. AI 개량 결과는 기본 `pending_review` 상태로 저장하고, 승인 전 사용자에게 공개하지 않는 정책을 명시했다. 처리 로그에는 프롬프트 버전, 입력/출력 요약, 실패 사유, 토큰 사용량, 비용 추정치를 저장할 수 있게 했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/ai_recipe_modification.py` — AI 개량 결과와 관리자 검수 상태 DB 모델 추가
- `src/portal/recipe/model/db/ai_processing_log.py` — AI 처리 로그, 실패, 비용, 프롬프트 버전 DB 모델 추가
- `src/portal/recipe/README.md` — AI 검수 정책과 관련 DB 모델 추가

### 문서
- `docs/recipe-taste-optimizer/ai-result-data-model.md` — AIRecipeModification/AIProcessingLog 필드 매핑, 공개/검수 정책, 로그 저장 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

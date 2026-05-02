# Recipe Taste Optimizer AI 프롬프트 버전 관리 API 구현

- **ID**: 018
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 AI 요약, 저염식, 이유식, 맛 개선, 검수 요약 프롬프트를 버전 단위로 관리할 수 있도록 프롬프트 템플릿 모델과 관리자 API를 추가했다. `promptKey:version` 형식의 `promptVersion`을 생성하고, 활성 버전 전환 시 같은 promptKey의 기존 활성 버전을 자동 비활성화한다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/ai_prompt_template.py` — 프롬프트 템플릿, 버전, 활성 여부, 변경 사유 저장 모델 추가
- `src/portal/recipe/model/struct.py` — `ai_prompt_template` 테이블 초기화 추가
- `src/portal/recipe/model/struct/ai.py` — 프롬프트 생성/수정/활성화/비활성화와 AIProcessingLog `prompt_version` 연결 로직 추가
- `src/portal/recipe/model/constants.py` — `AI_PROMPT_TYPES` 추가
- `src/portal/recipe/libs/constants.ts` — 프론트엔드용 `AI_PROMPT_TYPES` 타입/상수 추가
- `src/portal/recipe/README.md` — 관리자 AI 프롬프트 Route와 DB/정책 문서 갱신

### Route
- `src/route/recipe-admin-ai-prompt-list/app.json` — `/api/admin/ai/prompts` Route 설정
- `src/route/recipe-admin-ai-prompt-list/controller.py` — 프롬프트 목록 조회와 생성 API 구현
- `src/route/recipe-admin-ai-prompt-detail/app.json` — `/api/admin/ai/prompts/<path:path>` Route 설정
- `src/route/recipe-admin-ai-prompt-detail/controller.py` — 프롬프트 상세/수정/활성화/비활성화 API 구현

### 문서
- `docs/recipe-taste-optimizer/admin-ai-prompt-api.md` — 프롬프트 타입, 엔드포인트, payload, 로그 연결 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

# AI 결과 신뢰도 기반 자동 승인 설정 구현

- **ID**: 051
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
AI 개량 결과에 `confidence_score`를 저장하고, 설정 임계값 이상이면 생성 직후 자동 승인되도록 했다.
관리자 AI 검수 화면에서 자동 승인 임계값을 슬라이더로 조정하고 `config/ai_settings.json`에 저장할 수 있도록 API와 UI를 추가했다.

## 변경 파일 목록
- `src/portal/recipe/model/db/ai_recipe_modification.py`: `confidence_score` 컬럼 추가
- `src/portal/recipe/model/struct.py`: 기존 SQLite 테이블용 `confidence_score` 컬럼 보강 마이그레이션 추가
- `src/portal/recipe/model/struct/ai.py`: 설정 로드/저장, 신뢰도 산출, 자동 승인 로직 추가
- `src/app/page.admin.ai/api.py`: `get_settings()`, `save_settings()` 및 검수 DTO 신뢰도 필드 추가
- `src/app/page.admin.ai/view.ts`: 설정 상태 로드/저장 로직 추가
- `src/app/page.admin.ai/view.pug`: 자동 승인 임계값 슬라이더와 신뢰도 표시 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 관리자 AI 템플릿 문법 확인
- 관리자 대시보드 reviewQueue는 기존처럼 `pending_review`만 집계하므로 자동 승인 결과가 제외되는 흐름 확인

# Recipe Taste Optimizer 초기 데이터와 샘플 레시피 시드 작성

- **ID**: 011
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
개발/QA에서 빈 화면 없이 공개 목록, 상세, 관리자 검수 흐름을 확인할 수 있도록 초기 카테고리/태그 상수와 샘플 레시피 시드 모델을 추가했다. 시드는 고정 ID와 upsert 방식으로 작성해 여러 번 실행해도 중복 생성되지 않도록 했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/constants.py` — 기본 카테고리/태그와 AI 처리 로그 상태 상수 보강
- `src/portal/recipe/libs/constants.ts` — 프론트엔드 기본 카테고리/태그와 AI 처리 로그 상태 상수 보강
- `src/portal/recipe/model/seed.py` — 샘플 공개 레시피, 검수 대기 AI 버전, 데모 사용자 취향, 선택적 관리자 계정 시드 추가
- `src/portal/recipe/model/struct/ai.py` — 실제 DB 필드와 상수명에 맞게 AI Struct 보정
- `src/portal/recipe/model/struct/comment.py` — 수정 요청 기본 상태를 실제 상수와 맞게 보정
- `src/portal/recipe/README.md` — Seed API와 관리자 계정 생성 절차 요약 추가

### 문서
- `docs/recipe-taste-optimizer/initial-seed-data.md` — 기본 카테고리/태그, 샘플 데이터 ID, 관리자 계정 생성 절차, QA 체크 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

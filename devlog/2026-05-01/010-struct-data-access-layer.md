# Recipe Taste Optimizer Struct 기반 데이터 접근 계층 구현

- **ID**: 010
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
Recipe Taste Optimizer의 API와 UI가 DB 모델을 직접 다루지 않도록 `portal/recipe/struct` 계층을 추가했다. User, Recipe, Source, AI, Comment, AdminLog 도메인 Struct를 구성하고 공개 레시피는 기본적으로 approved 상태만 조회되도록 정책을 중앙화했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/struct.py` — Struct 진입점, DB wrapper 접근, 공통 JSON/권한/마스킹 유틸리티 추가
- `src/portal/recipe/model/struct/user.py` — 사용자, 로그인 기록, 취향 프로필 로직 추가
- `src/portal/recipe/model/struct/recipe.py` — 레시피 생성/수정/공개조회/관리자조회/조회수 로직 추가
- `src/portal/recipe/model/struct/source.py` — 외부 URL 정규화, 해시 중복 판정, 수집 상태 로직 추가
- `src/portal/recipe/model/struct/ai.py` — AI 개량 결과, 승인/반려, 처리 로그 로직 추가
- `src/portal/recipe/model/struct/comment.py` — 댓글, 즐겨찾기 토글, 수정 요청, 신고 로직 추가
- `src/portal/recipe/model/struct/admin_log.py` — 관리자 감사 로그와 before/after 마스킹 저장 로직 추가
- `src/portal/recipe/model/constants.py` — AI 처리 로그 상태 상수 보강
- `src/portal/recipe/libs/constants.ts` — 프론트엔드 AI 처리 로그 상태 상수 보강
- `src/portal/recipe/README.md` — Struct API와 반복 로직 정책 추가

### 문서
- `docs/recipe-taste-optimizer/struct-data-access-layer.md` — Struct 구성, 공개/관리자 조회 정책, 반복 로직 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

# Recipe Taste Optimizer 인증과 role 기반 권한 컨트롤러 구현

- **ID**: 012
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
Recipe Taste Optimizer의 백엔드 권한 강제를 위해 `portal/recipe/struct/auth`를 추가하고, `user`/`admin` 컨트롤러가 recipe 인증 Struct를 사용하도록 연결했다. `/access` API는 recipe 사용자 인증, 로그아웃, 현재 사용자 조회를 제공하도록 갱신했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/struct/auth.py` — PBKDF2 비밀번호 해시/검증, 로그인 실패 제한, 세션 로그인/로그아웃, role 검증 추가
- `src/portal/recipe/model/struct.py` — `struct.auth` 진입점 연결
- `src/portal/recipe/README.md` — Auth API와 권한 정책 요약 추가

### Controller/API
- `src/controller/user.py` — active 로그인 사용자만 통과하도록 recipe auth 검증 적용
- `src/controller/admin.py` — admin role 사용자만 통과하도록 recipe auth 검증 적용
- `src/app/page.access/api.py` — recipe auth 기반 `login`, `logout`, `me` API 구현

### 문서
- `docs/recipe-taste-optimizer/auth-role-policy.md` — 세션 키, 권한 매트릭스, 로그인 실패 제한, 관리자 계정 해시 절차 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 API 함수 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

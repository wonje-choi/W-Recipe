# Recipe Taste Optimizer 사용자와 인증 데이터 모델 구현

- **ID**: 004
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
사용자 계정과 개인 선호도 저장을 위한 DB 모델을 recipe 패키지에 추가했다. 비밀번호는 해시만 저장하도록 설계했고, 로그인 실패 제한을 위한 실패 횟수/잠금 만료 필드를 포함했다. 알레르기, 아이 월령, 선호 식단 등 민감 정보는 로그 원문 저장 금지 원칙으로 문서화했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/user.py` — 사용자 계정, 권한, 상태, 로그인 실패 기록 DB 모델 추가
- `src/portal/recipe/model/db/user_preference.py` — 사용자 식단 선호도, 알레르기, 비선호 재료, 조리 조건 DB 모델 추가
- `src/portal/recipe/README.md` — 사용자 관련 DB 모델과 개인정보 보호 원칙 추가

### 문서
- `docs/recipe-taste-optimizer/user-auth-data-model.md` — User/UserPreference 필드 매핑, 비밀번호 저장 정책, 민감 정보 보호 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

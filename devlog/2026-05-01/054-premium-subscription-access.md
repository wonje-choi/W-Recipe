# 유료 구독 모델과 프리미엄 접근 제어 구현

- **ID**: 054
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
사용자 모델에 `free`/`premium` 구독 플랜과 만료일을 추가하고, 기존 user/admin 권한 흐름과 분리된 프리미엄 접근 제어를 구현했다.
관리자는 참여 관리 화면의 구독 탭에서 회원 플랜을 수동으로 변경할 수 있으며, 마이페이지에는 현재 구독 상태와 수동 활성화 안내가 표시된다.

## 변경 파일 목록
- `src/portal/recipe/model/db/user.py`: 구독 플랜과 만료일 컬럼 추가
- `src/portal/recipe/model/constants.py`: `SUBSCRIPTION_PLANS` 상수 추가
- `src/portal/recipe/model/struct.py`: 기존 SQLite 사용자 테이블 구독 컬럼 마이그레이션 추가
- `src/portal/recipe/model/struct/auth.py`: 프리미엄 판별, 프리미엄 권한 요구, 관리자 구독 변경 메서드 추가
- `src/controller/premium.py`: 로그인 사용자 중 Premium 또는 Admin만 통과하는 컨트롤러 추가
- `src/app/page.mypage/view.ts`, `src/app/page.mypage/view.pug`: 구독 현황과 업그레이드 안내 표시
- `src/app/page.admin.feedback/api.py`, `view.ts`, `view.pug`: 구독 회원 목록, 필터, 수동 플랜 변경 기능 추가
- `src/app/layout.recipe/view.ts`: `premium: true` nav 항목 조건부 표시 지원

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 변경 Pug 템플릿 문법 확인
- 기존 `controller/user.py`와 `controller/admin.py` 권한 구조를 변경하지 않고 프리미엄 권한을 별도 컨트롤러로 추가했는지 확인

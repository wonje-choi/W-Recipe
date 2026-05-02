# Recipe Taste Optimizer 공통 레이아웃과 로그인 모달 UI 구현

- **ID**: 025
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
Recipe Taste Optimizer 공개 화면에서 사용할 `layout.recipe` 공통 레이아웃을 구현했다. 상단/모바일 내비게이션, 일반/관리자 로그인 탭 모달, 로그인 상태 표시, admin role 버튼 노출을 포함했다.

## 변경 파일 목록

### Source App
- `src/app/layout.recipe/app.json`: Recipe 공통 레이아웃 앱 메타데이터를 정의했다.
- `src/app/layout.recipe/api.py`: 레이아웃에서 사용하는 `me`, `login`, `logout` API를 추가했다.
- `src/app/layout.recipe/view.ts`: 세션 사용자 조회, 로그인/로그아웃, 모바일 메뉴, role 기반 내비게이션 상태를 구현했다.
- `src/app/layout.recipe/view.pug`: 데스크톱/모바일 내비게이션과 로그인 모달 UI를 구현했다.
- `src/app/layout.recipe/view.scss`: 레이아웃 host 스타일을 설정했다.

### 문서
- `docs/recipe-taste-optimizer/common-layout-login-modal.md`: 레이아웃 사용 방식과 인증 API, 개인정보 노출 범위를 문서화했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 레이아웃 API 문법 검사 통과.
- 신규 Layout App과 API 함수 반영을 위해 clean WIZ build 수행, 빌드 성공.

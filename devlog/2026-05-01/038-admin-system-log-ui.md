# Recipe Taste Optimizer 관리자 System Log UI 구현

- **ID**: 038
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
운영자가 관리자 작업, 로그인 실패, AI 실패, 크롤링 실패 이벤트를 한 화면에서 추적할 수 있는 `/admin/logs` 화면을 구현했다. 유형, 심각도, 관리자, 대상, 기간, 키워드 필터를 제공하고 상세 영역에는 마스킹된 메타 정보를 표시한다.

## 변경 파일 목록

### Source App
- `src/app/page.admin.logs/app.json`: `/admin/logs` 관리자 페이지 설정
- `src/app/page.admin.logs/api.py`: `admin_action_log`, 사용자 로그인 실패, AI 실패, 크롤링 실패 이벤트 통합 조회 API 구현
- `src/app/page.admin.logs/view.ts`: 필터, 페이지네이션, 로그 선택, 요약 카드 상태 관리
- `src/app/page.admin.logs/view.pug`: 시스템 로그 목록, 필터, 마스킹 상세 UI 구현
- `src/app/page.admin.logs/view.scss`: Page host와 로그 상세 텍스트 스타일 정의

### Layout
- `src/app/layout.recipe/view.ts`: 관리자 네비게이션에 시스템 로그 메뉴 추가

### 문서
- `docs/recipe-taste-optimizer/admin-system-log-ui.md`: 시스템 로그 화면 계약과 마스킹 정책 문서 추가
- `src/portal/recipe/README.md`: `/admin/logs` Page App 참조 추가

## 검증
- VS Code diagnostics: `page.admin.logs`와 `layout.recipe` 관련 파일 오류 없음
- `python3 -m py_compile src/app/page.admin.logs/api.py` 통과
- WIZ clean build 성공 후 `/admin/logs` 라우팅 산출물 확인

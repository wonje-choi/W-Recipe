# Recipe Taste Optimizer 관리자 Dashboard UI 구현

- **ID**: 033
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
기존 `/dashboard`를 Recipe 운영자용 관리자 대시보드로 교체했다. 전체 레시피, 검수 대기, 사용자, 댓글, 수정 요청, AI 요청 수와 외부 자료/AI 실패/승인 비율을 표시하고 검수/로그 세부 화면으로 이동하는 액션을 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.dashboard/app.json`: `/dashboard`를 `layout.recipe`와 `admin` controller 기반 페이지로 변경했다.
- `src/app/page.dashboard/api.py`: 운영 지표, 검수 대기 큐, 최근 외부 자료, AI 실패 로그, 승인/반려 비율을 반환하는 `overview()`를 구현했다.
- `src/app/page.dashboard/view.ts`: 대시보드 데이터 로드, tone class, 이동 액션을 구현했다.
- `src/app/page.dashboard/view.pug`: 지표 카드, 검수 대기 큐, 처리 품질, 최근 외부 자료, AI 실패 로그 UI를 구현했다.
- `src/app/page.dashboard/view.scss`: Page host와 line clamp 스타일을 추가했다.

### 공통 레이아웃
- `src/app/layout.recipe/view.ts`: admin 사용자에게만 보이는 관리자 내비게이션 항목을 추가했다.

### 문서
- `docs/recipe-taste-optimizer/admin-dashboard-ui.md`: 관리자 대시보드 경로, API, 지표, 권한을 문서화했다.
- `src/portal/recipe/README.md`: 공개/관리자 프론트엔드 페이지 목록에 `/dashboard`를 추가했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 대시보드 API 문법 검사 통과.
- 기존 API 함수 내용 및 app.json 변경이므로 일반 WIZ build 수행, 빌드 성공.

# Recipe Taste Optimizer 관리자 참여/신고/수정 요청 관리 UI 구현

- **ID**: 037
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 댓글, 신고, 수정 요청을 한 화면에서 확인하고 처리할 수 있는 `/admin/feedback` 화면을 구현했다. 댓글 숨김/삭제/복구, 신고 처리 상태 변경, 수정 요청 처리 상태 변경, 사용자 정지 액션을 제공하고 주요 변경 사항을 관리자 감사 로그에 남기도록 했다.

## 변경 파일 목록

### Source App
- `src/app/page.admin.feedback/app.json`: `/admin/feedback` 관리자 페이지 설정
- `src/app/page.admin.feedback/api.py`: 댓글/신고/수정 요청 목록과 처리 액션 API 구현
- `src/app/page.admin.feedback/view.ts`: 탭, 필터, 페이지네이션, 선택 상세, 상태 처리 액션 구현
- `src/app/page.admin.feedback/view.pug`: 댓글/신고/수정 요청 관리 UI 구현
- `src/app/page.admin.feedback/view.scss`: Page host와 목록 텍스트 클램프 스타일 정의

### Layout
- `src/app/layout.recipe/view.ts`: 관리자 네비게이션에 참여 관리 메뉴 추가

### 문서
- `docs/recipe-taste-optimizer/admin-feedback-management-ui.md`: 관리자 참여 관리 화면 계약 문서 추가
- `src/portal/recipe/README.md`: `/admin/feedback` Page App 참조 추가

## 검증
- VS Code diagnostics: `page.admin.feedback`와 `layout.recipe` 관련 파일 오류 없음
- `python3 -m py_compile src/app/page.admin.feedback/api.py` 통과
- WIZ clean build 성공 후 `/admin/feedback` 라우팅 산출물 확인

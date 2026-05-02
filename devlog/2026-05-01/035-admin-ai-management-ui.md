# Recipe Taste Optimizer 관리자 AI Management UI 구현

- **ID**: 035
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 AI 개량 결과를 검수하고 승인, 반려, 재생성할 수 있는 `/admin/ai` 화면을 구현했다.
프롬프트 버전 관리와 AI 처리 로그, 실패 로그, 토큰 사용량 및 비용 확인 UI를 함께 구성하여 AI 결과가 운영자 검수 후에만 공개될 수 있도록 했다.

## 변경 파일 목록

### Source App
- `src/app/page.admin.ai/app.json`: `/admin/ai` 관리자 페이지 라우팅, `admin` controller, `layout.recipe` 설정
- `src/app/page.admin.ai/api.py`: 검수 목록, 승인/반려/재생성, 프롬프트 저장/활성화, 로그 조회 API 구현
- `src/app/page.admin.ai/view.ts`: 검수/프롬프트/로그 탭 상태와 액션 처리 구현
- `src/app/page.admin.ai/view.pug`: AI 검수 상세, 프롬프트 편집기, 처리 로그 테이블 UI 구현
- `src/app/page.admin.ai/view.scss`: 페이지 host, 입력 UI, line clamp 스타일 정의

### Layout
- `src/app/layout.recipe/view.ts`: 관리자 내비게이션에 AI 관리 메뉴 추가

### Documentation
- `docs/recipe-taste-optimizer/admin-ai-management-ui.md`: 관리자 AI 관리 화면 계약과 운영 흐름 문서화
- `src/portal/recipe/README.md`: 프론트엔드 화면 목록에 `page.admin.ai` 추가

## 검증
- `get_errors`로 신규 AI 관리 앱, layout, 문서 오류 없음 확인
- `python3 -m py_compile src/app/page.admin.ai/api.py` 통과
- WIZ 일반 빌드 성공

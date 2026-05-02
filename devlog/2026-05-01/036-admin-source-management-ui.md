# Recipe Taste Optimizer 관리자 Crawled Source Management UI 구현

- **ID**: 036
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 외부 URL 수집 이력과 출처 상태를 추적할 수 있는 `/admin/sources` 화면을 구현했다. URL, 출처 유형, 제목, 작성자, 수집 일자, 크롤링 상태와 운영 플래그를 목록에서 확인하고, 실패 사유와 재시도/만료/상태 변경 액션을 처리할 수 있게 했다.

## 변경 파일 목록

### Source App
- `src/app/page.admin.sources/app.json`: `/admin/sources` 관리자 페이지 설정
- `src/app/page.admin.sources/api.py`: 목록, 옵션, 저장, 상태 변경, 재시도, 만료 처리 API 구현
- `src/app/page.admin.sources/view.ts`: 필터, 페이지네이션, 편집 패널, 원본 열기, 재시도 액션 상태 관리
- `src/app/page.admin.sources/view.pug`: 출처 목록, 상태 플래그, 실패 사유, 편집 패널 UI 구현
- `src/app/page.admin.sources/view.scss`: Page host와 목록 텍스트 클램프 스타일 정의

### Layout
- `src/app/layout.recipe/view.ts`: 관리자 네비게이션에 출처 관리 메뉴 추가

### 문서
- `docs/recipe-taste-optimizer/admin-source-management-ui.md`: 관리자 출처 관리 화면 계약 문서 추가
- `src/portal/recipe/README.md`: `/admin/sources` Page App 참조 추가

## 검증
- VS Code diagnostics: `page.admin.sources`와 `layout.recipe` 관련 파일 오류 없음
- `python3 -m py_compile src/app/page.admin.sources/api.py` 통과
- WIZ clean build 성공 후 `/admin/sources` 라우팅 산출물 확인
- 스타일 보정 후 WIZ normal build 성공

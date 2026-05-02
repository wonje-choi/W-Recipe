# Recipe Taste Optimizer 관리자 Recipe Management UI 구현

- **ID**: 034
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 레시피 콘텐츠를 코드 수정 없이 운영할 수 있도록 `/admin/recipes` 화면을 추가했다. 기존 관리자 REST API를 연결하여 레시피 목록 검색, 상태 필터, Dish 등록/수정, Version 편집, 공개/검수/숨김 상태 변경을 지원한다.

## 변경 파일 목록

### Source App
- `src/app/page.admin.recipes/app.json`: `layout.recipe`와 `admin` controller 기반 `/admin/recipes` 페이지를 추가했다.
- `src/app/page.admin.recipes/api.py`: 상태, 출처 유형, 난이도, 카테고리, 태그 옵션을 제공하는 `options()`를 구현했다.
- `src/app/page.admin.recipes/view.ts`: 관리자 REST API 연동, 검색/페이지네이션, 등록/수정 폼, 버전 선택, 상태 변경, 숨김 처리 로직을 구현했다.
- `src/app/page.admin.recipes/view.pug`: 목록 테이블, 상태 필터, Dish 기본 정보, 출처, 조리 콘텐츠, 안전/영양 정보 편집 UI를 구현했다.
- `src/app/page.admin.recipes/view.scss`: host와 line clamp 스타일을 추가했다.

### 공통 레이아웃
- `src/app/layout.recipe/view.ts`: admin 사용자에게만 보이는 `레시피 관리` 내비게이션 항목을 추가했다.

### 문서
- `docs/recipe-taste-optimizer/admin-recipe-management-ui.md`: 관리자 레시피 관리 화면과 사용하는 REST API를 문서화했다.
- `src/portal/recipe/README.md`: 프론트엔드 페이지 목록에 `/admin/recipes`를 추가했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 앱 API 문법 검사 통과.
- 새 Page App과 새 API 함수가 추가되어 클린 WIZ build 수행, 빌드 성공.
- 빌드 산출물에서 `/admin/recipes` 라우팅 반영을 확인했다.

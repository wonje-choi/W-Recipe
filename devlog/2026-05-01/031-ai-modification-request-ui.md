# Recipe Taste Optimizer AI 개량 요청 UI 구현

- **ID**: 031
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
로그인 사용자가 승인 레시피 Version을 선택해 AI 개량 요청을 저장하는 `page.recipe.ai.modify` 화면을 구현했다. 개량 목적, 대상 사용자, 제외 재료, 알레르기, 조리 시간, 맛 방향, 추가 요청사항 입력과 pending review 안내를 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.recipe.ai.modify/app.json`: `/ai/modify` 공개 페이지와 `layout.recipe` 연결을 정의했다.
- `src/app/page.recipe.ai.modify/api.py`: 초기 데이터 로드, 대상 레시피 검색, AI 개량 요청 저장 API를 추가했다.
- `src/app/page.recipe.ai.modify/view.ts`: 대상 레시피 선택, 목적 선택, 로그인 모달 이벤트, 제출 상태, 성공 안내 상태를 구현했다.
- `src/app/page.recipe.ai.modify/view.pug`: 대상 레시피 검색/선택, 개량 목적 카드, 요청 조건 입력, pending review 안내, 저장 완료 UI를 구현했다.
- `src/app/page.recipe.ai.modify/view.scss`: Page host, 입력 요소, line clamp 스타일을 추가했다.

### 공통 레이아웃
- `src/app/layout.recipe/view.ts`: `recipe-open-login` window event를 받아 공통 로그인 모달을 열도록 연결했다.

### 문서
- `docs/recipe-taste-optimizer/ai-modification-request-ui.md`: AI 요청 화면 경로, 입력 흐름, 목적 옵션, API 함수, 로그인 모달 연동, 정책을 문서화했다.
- `src/portal/recipe/README.md`: 공개 프론트엔드 페이지 목록에 `/ai/modify`를 추가했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 AI 요청 페이지 API 문법 검사 통과.
- 신규 Page App과 API 함수 반영을 위해 clean WIZ build 수행, 빌드 성공.

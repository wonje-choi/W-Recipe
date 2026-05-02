# Recipe Taste Optimizer 마이페이지 UI 구현

- **ID**: 032
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
기존 `/mypage` Page App을 Recipe 앱의 마이페이지로 교체했다. `layout.recipe`와 `user` controller를 사용하며 프로필, 저장한 레시피, 최근 본 레시피, 댓글, 수정 요청, AI 개량 요청, 개인화 설정을 제공한다.

## 변경 파일 목록

### Source App
- `src/app/page.mypage/app.json`: `/mypage`를 `layout.recipe` 기반 로그인 사용자 페이지로 변경했다.
- `src/app/page.mypage/api.py`: 프로필/선호도/활동 내역 로드, 프로필 저장, 개인화 설정 저장 API를 구현했다.
- `src/app/page.mypage/view.ts`: 탭 상태, 활동 카운트, 선호도 토글, 프로필/선호도 저장, 레시피 상세 이동 로직을 구현했다.
- `src/app/page.mypage/view.pug`: 활동, 개인화 설정, 프로필 탭 UI와 각 활동 목록을 구현했다.
- `src/app/page.mypage/view.scss`: Page host와 line clamp 스타일을 추가했다.

### 문서
- `docs/recipe-taste-optimizer/mypage-ui.md`: 마이페이지 경로, API 함수, UI 구성, 데이터 정책을 문서화했다.
- `src/portal/recipe/README.md`: 공개 프론트엔드 페이지 목록에 `/mypage`를 추가했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 마이페이지 API 문법 검사 통과.
- API 함수 목록 및 레이아웃 변경 반영을 위해 clean WIZ build 수행, 빌드 성공.
- generated routing에서 `/mypage`가 `layout.recipe` 하위에 배치된 것을 확인했다.

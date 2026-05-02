# Recipe Taste Optimizer 보안 요구사항 구현

- **ID**: 040
- **날짜**: 2026-05-01
- **유형**: 기능 추가 / 보안 개선 / 문서 업데이트

## 작업 요약
비밀번호 해시 저장, 로그인 실패 제한, 관리자 role controller, 사용자별 데이터 접근 제한 등 기존 보안 구현을 확인했다. 누락된 영역은 외부 URL 검증, 사용자 입력 안전 검사, 중첩 민감정보 마스킹, 세션 CSRF 토큰 전달 흐름으로 보강했다.

외부 출처 URL, 레시피 원본/이미지 URL, 썸네일 URL, 수정 요청 첨부 URL은 http/https만 허용하고 localhost, 내부망, loopback, link-local, reserved IP와 사용자 정보 포함 URL을 차단한다. 댓글/수정 요청/신고 입력은 제어문자와 고위험 스크립트 패턴을 차단한다.

## 변경 파일 목록
- `src/controller/base.py`: 세션 내부 키 공개 제거, CSRF 토큰 생성/전달, 토큰 검증 helper 추가
- `src/angular/wiz.ts`: `wiz.call()` 요청에 `X-CSRF-Token` 헤더 자동 첨부
- `src/app/layout.recipe/api.py`: `me`/`login`/`logout` 응답에 CSRF 토큰 포함
- `src/app/layout.recipe/view.ts`: CSRF 토큰을 `window.recipeCsrfToken`에 저장
- `src/app/page.admin.recipes/view.ts`: 관리자 REST fetch 호출에 CSRF 토큰 헤더 첨부
- `src/portal/recipe/model/struct.py`: 사용자 입력 검사, 업로드 파일 정책 helper, 재귀 민감정보 마스킹 추가
- `src/portal/recipe/model/struct/source.py`: 외부 URL 스킴/호스트/IP 검증과 썸네일 URL 검증 추가
- `src/portal/recipe/model/struct/recipe.py`: 레시피 대표 이미지와 원본 URL 검증 연결
- `src/portal/recipe/model/struct/comment.py`: 댓글/수정 요청/신고 입력 안전 검사와 첨부 URL 검증 연결
- `src/portal/recipe/README.md`: Security Policy 문서화

## 검증
- `python3 -m py_compile src/controller/base.py src/app/layout.recipe/api.py src/portal/recipe/model/struct.py src/portal/recipe/model/struct/source.py src/portal/recipe/model/struct/recipe.py src/portal/recipe/model/struct/comment.py` 통과
- VS Code diagnostics: 변경한 Python/TypeScript/README 파일 오류 없음
- WIZ normal build 성공 (`success: true`, `errors: null`)

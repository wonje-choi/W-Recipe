# 메인페이지 manifest 오류 수정과 관리자 계정 설정

- **ID**: 047
- **날짜**: 2026-05-01
- **유형**: 버그 수정 | 설정 변경

## 작업 요약
메인페이지가 존재하지 않는 루트 `/manifest.json`을 참조해 HTML fallback을 manifest JSON으로 파싱하던 문제를 수정했다.
실제 정적 자산 경로인 `/assets/manifest.json`을 제공하고, 누락된 `/sw.js` 등록을 제거했으며, 요청된 운영 관리자 계정을 활성 admin 계정으로 설정했다.

## 변경 파일 목록

### Frontend Shell
- `src/angular/index.pug`: manifest 링크를 `/assets/manifest.json`으로 변경하고 미사용 service worker 등록을 제거했다.

### Static Assets
- `src/assets/manifest.json`: Web App Manifest JSON을 추가했다.

### Data
- `data/recipe.db`: `41180dnjswp@gmail.com` 계정을 admin/active 상태로 생성하고 비밀번호를 PBKDF2 해시로 저장했다.

## 검증
- `python3 -m json.tool`로 Angular 설정과 manifest JSON 검증 완료.
- `wiz project build --project main` normal build 성공.
- `bundle/src/assets/manifest.json` JSON 파싱 성공.
- `GET /assets/manifest.json` HTTP 200 및 JSON 응답 확인.
- `POST /wiz/api/layout.recipe/login` 관리자 계정 로그인 성공, role `admin` 확인.

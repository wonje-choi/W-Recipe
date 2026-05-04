# 개발 일지

📅 Development Log

### 1. 작업 개요

```text
Date
2026-05-02

Developer
Codex

Project
Recipe Taste Optimizer

Task
전체 페이지 구조 점검, 페이지 컴파일 오류 수정, 개발 빌드 검증, 발표 자료 및 PPT 제작
```

---

### 2. 작업 내용

```text
작업 목적
Recipe Taste Optimizer 프로젝트의 전체 페이지 구성을 확인하고,
페이지 실행에 영향을 주는 오류를 수정한 뒤 개발 빌드 기준으로 정상 컴파일되는지 검증했다.
또한 프로젝트팀 발표를 위해 비전공자도 이해할 수 있는 발표 문서와 PPT 자료를 제작했다.

개발 내용
1. 전체 페이지 구성 확인
   - 공통 레이아웃:
     - layout.recipe
     - layout.sidebar
     - layout.empty
   - 공통 컴포넌트:
     - component.nav.sidebar
   - 사용자/공개 페이지:
     - page.recipe.home
     - page.recipe.list
     - page.recipe.detail
     - page.recipe.ai.modify
     - page.dashboard
     - page.posts
     - page.posts.item
     - page.access
     - page.members
     - page.mypage
   - 관리자 페이지:
     - page.admin.recipes
     - page.admin.sources
     - page.admin.ai
     - page.admin.feedback
     - page.admin.logs
   - Portal 공통 앱:
     - portal.post.list
     - portal.post.detail
     - portal.season.form.dropdown
     - portal.season.loading.default
     - portal.season.loading.season
     - portal.season.modal
     - portal.season.pagination
     - portal.season.tree

2. 페이지 컴파일 오류 수정
   - 누락된 view.scss 파일 추가
   - 비어 있는 스타일 파일이 잘못 처리되어 발생하던 Angular 리소스 오류 수정
   - Angular strict 타입 검사와 WIZ 생성 코드 간 충돌 완화
   - 전역 라우트 정보 WizRoute 타입 선언 보강
   - wiz.call() 및 Request.post() 응답 타입 보강
   - 동적 상태 객체 Status 타입 보강
   - pagination, tree, modal, file, crypto 유틸 타입 오류 수정
   - 관리자 페이지 view.ts 내부 중복 wiz 선언 제거

3. 전체 페이지 개발 빌드 검증
   - 개발 빌드 명령 실행:
     npm run build -- --configuration development
   - 결과:
     성공

4. 발표 자료 제작
   - 프로젝트팀 대상 발표 문서 작성
   - 발표용 PPTX 제작
   - 발표에 불필요한 세부 구현 내용은 제외하고,
     서비스 목적, 사용자 흐름, 관리자 검수 구조, 검증 결과, 남은 TODO 중심으로 구성
```

---

### 3. 사용 기술

```text
Language
TypeScript
JavaScript
Python
SCSS
Pug
Markdown

Framework
Angular 18
WIZ Framework

Library
@angular/core
@angular/router
@ngx-translate/core
@ng-bootstrap/ng-bootstrap
@ng-util/monaco-editor
socket.io-client
jquery
moment
python-pptx
```

---

### 4. 주요 코드 / 구조

```text
핵심 코드 설명
1. Angular/WIZ 라우팅 구조
   - src/angular/app/app-routing.module.ts
   - WIZ 페이지 라우트를 Angular Router와 연결
   - 전역 WizRoute 객체를 통해 현재 URL segment 정보를 페이지에서 사용

2. 공통 서비스 구조
   - src/portal/season/libs/service.ts
   - auth, modal, status, event, request, formatter 등 공통 기능 초기화
   - 페이지와 공통 컴포넌트에서 Service를 주입받아 사용

3. API 호출 구조
   - src/angular/wiz.ts
   - wiz.call()을 통해 각 page api.py 또는 route와 통신
   - CSRF Token이 있으면 X-CSRF-Token 헤더에 포함

4. 상태 관리 구조
   - src/portal/season/libs/src/status.ts
   - loading, navbar 등 화면 상태를 동적으로 관리

5. 공통 UI 컴포넌트
   - portal.season.modal
   - portal.season.pagination
   - portal.season.tree
   - portal.season.loading.default
   - portal.season.loading.season

데이터 구조
Recipe Taste Optimizer는 레시피를 단일 게시글이 아니라 다음 구조로 관리한다.

1. Recipe Dish
   - 요리 기본 정보
   - 이름, 설명, 태그, 공개 상태

2. Recipe Version
   - 같은 요리에 대한 여러 버전
   - 원본 요약, AI 저염식, AI 이유식, AI 간편식 등

3. Crawled Source
   - 원본 출처 링크
   - 수집 상태
   - 원문 보관 정책

4. AI Modification Request
   - 사용자의 AI 개량 요청
   - 목적, 조건, 결과, 검수 상태

5. Admin Action Log
   - 관리자가 어떤 데이터를 언제 승인/반려/변경했는지 기록

알고리즘
별도 복잡한 알고리즘 구현보다는 다음 흐름이 핵심이다.

1. 사용자 레시피 탐색
   메인 → 목록 검색/필터 → 상세 확인

2. AI 개량 요청
   목적 선택 → 조건 입력 → 요청 저장 → Pending Review 상태

3. 관리자 검수
   검수 대기 목록 확인 → 승인 또는 반려 → 공개 상태 및 로그 기록
```

---

### 5. 발생한 문제

```text
문제 상황
전체 페이지를 개발 빌드로 검증하는 과정에서 Angular 컴파일 오류가 발생했다.
일부 오류는 실제 페이지 로직 문제가 아니라 WIZ 생성 코드와 Angular 18 strict 타입 검사 간의 충돌이었다.

오류 메시지
1. 누락된 스타일 리소스
   Error: Module not found: Can't resolve '.../view.scss?ngResource'

2. SCSS 처리 오류
   The loader ".../view.scss" didn't return a string.

3. Angular Router 타입 오류
   Object literal may only specify known properties, and '"app_id"' does not exist in type 'Route'.

4. 전역 라우트 객체 타입 오류
   Property 'WizRoute' does not exist on type 'Window & typeof globalThis'.

5. API 응답 타입 오류
   Property 'code' does not exist on type '{}'.
   Property 'data' does not exist on type '{}'.

6. 공통 서비스 초기화 오류
   Expected 1 arguments, but got 0.

7. 동적 상태 객체 오류
   Property 'loading' does not exist on type 'Status'.
   Property 'navbar' does not exist on type 'Status'.

8. 프로덕션 빌드 제한 오류
   Error: bundle initial exceeded maximum budget.

재현 조건
build 디렉터리에서 다음 명령을 실행하면 오류를 확인할 수 있었다.

npm run build

개발 빌드 검증은 다음 명령으로 수행했다.

npm run build -- --configuration development
```

---

### 6. 해결 방법

```text
문제 해결 과정
1. 현재 WIZ 프로젝트 확인
   - wiz_workspace_status로 현재 프로젝트가 main인지 확인
   - 수정 범위를 /opt/app/project/main 내부로 한정

2. 전체 페이지 및 공통 컴포넌트 확인
   - src/app
   - src/portal/post/app
   - src/portal/season/app
   - docs/recipe-taste-optimizer

3. 누락된 SCSS 파일 추가
   - component.nav.sidebar
   - layout.sidebar
   - page.members
   - page.posts
   - page.posts.item
   - portal.season.loading.season
   - portal.season.modal
   - portal.season.pagination

4. 타입 선언 보강
   - WizRoute 전역 타입 추가
   - wiz.call() 반환 타입을 Promise<any>로 지정
   - Request.post() 반환 타입을 Promise<any>로 지정
   - Status에 index signature와 loading/navbar 기본 상태 추가
   - Auth에 request 속성 선언

5. 공통 서비스 안정화
   - Service.init()의 app 인자를 optional로 변경
   - app이 없는 경우에도 auth/status/modal 등 공통 객체가 초기화되도록 수정
   - render()에서 optional chaining을 사용해 app.ref 접근 오류를 방지

6. 유틸 코드 타입 오류 수정
   - modal cancel 속성 선언
   - file util result 객체를 any로 지정
   - crypto util의 중복 var 선언 제거
   - tree drop 결과를 any[]로 캐스팅
   - pagination에서 Math 속성 선언

7. 관리자 페이지 중복 선언 제거
   - 일부 관리자 view.ts에 중복 선언된 declare const wiz 제거

적용한 방법
코드 수정 후 개발 빌드 명령으로 전체 페이지 컴파일을 재검증했다.
페이지 관련 컴파일 오류는 해결되었고 개발 빌드는 성공했다.
프로덕션 빌드는 번들 용량 budget 초과가 남아 있어 TODO로 분리했다.
```

---

### 7. 테스트 결과

```text
테스트 환경
OS/Workspace
/opt/app

Project
/opt/app/project/main

Build Target
/opt/app/project/main/build

Framework
Angular 18
WIZ Framework

테스트 데이터
실제 데이터 입력 테스트는 수행하지 않았고,
전체 페이지 및 공통 컴포넌트가 Angular 개발 빌드에서 컴파일되는지 확인했다.

결과
1. 개발 빌드
   Command:
   npm run build -- --configuration development

   Result:
   Success

2. 프로덕션 빌드
   Command:
   npm run build

   Result:
   Failed

   Cause:
   페이지 코드 오류가 아니라 초기 bundle size가 production budget을 초과함.

3. 남은 경고
   - jquery CommonJS 경고
   - moment CommonJS 경고
   - debug CommonJS 경고

4. npm install 후 확인된 보안 경고
   - npm audit 기준 취약점 존재
   - 운영 배포 전 영향도 분석 필요
```

---

### 8. 다음 작업 계획

```text
다음 개발 예정 기능
1. 주요 사용자 시나리오 브라우저 QA
   - 메인 페이지
   - 레시피 목록
   - 레시피 상세
   - AI 개량 요청
   - 마이페이지
   - 관리자 레시피 관리
   - 관리자 출처 관리
   - 관리자 AI 관리
   - 관리자 피드백 관리
   - 관리자 로그 화면

2. 관리자 검수 플로우 확인
   - AI 요청 생성
   - Pending Review 저장
   - 승인/반려
   - 공개 상태 반영
   - 관리자 작업 로그 기록

3. production build 통과
   - bundle budget 기준 조정 여부 검토
   - lazy loading 가능성 검토
   - 불필요한 의존성 제거
   - Monaco/editor 등 대형 라이브러리 분리 검토

개선 사항
1. CommonJS 의존성 경고 개선
   - jquery, moment 사용 범위 점검
   - 대체 라이브러리 또는 Angular 설정 검토

2. npm audit 취약점 점검
   - 실제 영향도 확인
   - 안전한 버전 업데이트 가능 여부 확인

3. 운영 문서 보강
   - 배포 절차
   - 롤백 절차
   - 관리자 검수 정책
   - QA 체크리스트
```

---

### 9. 참고 자료

```text
GitHub 링크
현재 로컬 작업 기준이며 원격 GitHub 링크는 확인하지 않음.

문서 링크
docs/recipe-taste-optimizer/mvp-scope-and-ia.md
docs/recipe-taste-optimizer/wiz-project-structure.md
docs/recipe-taste-optimizer/main-page-ui.md
docs/recipe-taste-optimizer/recipe-list-ui.md
docs/recipe-taste-optimizer/recipe-detail-ui.md
docs/recipe-taste-optimizer/ai-modification-request-ui.md
docs/recipe-taste-optimizer/admin-recipe-management-ui.md
docs/recipe-taste-optimizer/admin-source-management-ui.md
docs/recipe-taste-optimizer/admin-ai-management-ui.md
docs/recipe-taste-optimizer/admin-feedback-management-ui.md
docs/recipe-taste-optimizer/admin-system-log-ui.md
docs/recipe-taste-optimizer/project-team-presentation.md
docs/recipe-taste-optimizer/recipe-taste-optimizer-project-presentation.pptx

참고 자료
Angular build result
npm run build -- --configuration development

Production build TODO
npm run build
bundle initial exceeded maximum budget
```


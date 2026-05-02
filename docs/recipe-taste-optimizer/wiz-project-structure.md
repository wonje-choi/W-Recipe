# Recipe Taste Optimizer WIZ Project Structure

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0002
- **목적**: Recipe Taste Optimizer를 WIZ 프로젝트에 구현하기 위한 Source App, Portal Package, Controller, Route 배치와 네이밍 기준을 확정한다.

## 1. 현재 프로젝트 상태

| 항목 | 값 |
|---|---|
| 활성 WIZ 프로젝트 | `main` |
| 프로젝트 경로 | `project/main` |
| Source 경로 | `project/main/src` |
| 기존 Source App | `page.access`, `page.dashboard`, `page.posts`, `page.posts.item`, `page.members`, `page.mypage`, `layout.empty`, `layout.sidebar`, `component.nav.sidebar` |
| 기존 Portal Package | `season`, `post` |
| 기존 Controller | `base`, `user`, `admin` |

현재 Source App은 2026-02-21 작업에서 생성된 일반 서비스 샘플 패턴이다. Recipe Taste Optimizer 구현 단계에서는 샘플 앱을 그대로 제품 화면으로 사용하지 않고, 레시피 서비스용 앱으로 교체 또는 신규 생성한다.

## 2. 패키지 전략

### 2.1 유지할 패키지

| 패키지 | 역할 | 사용 방식 |
|---|---|---|
| `season` | 공통 인증, 세션, ORM, Service, UI 공통 기능 | 모든 Page/Layout/Component의 `view.ts`에서 `Service`를 주입해 사용 |

`season` 패키지는 이미 README와 Service API가 준비되어 있으므로 공통 기반으로 유지한다.

### 2.2 신규 도메인 패키지

| 패키지 후보 | 결정 | 사유 |
|---|---|---|
| `recipe` | 채택 | 도메인 의미가 명확하고 DB/Struct/API/상수의 책임을 직관적으로 표현한다. |
| `taste` | 보류 | 서비스명과는 어울리지만 레시피/출처/AI 개량 도메인 전체를 설명하기에는 추상적이다. |

신규 Portal Package는 `src/portal/recipe`로 설계한다.

예상 역할:

- `src/portal/recipe/model/db/` — User, UserPreference, RecipeDish, RecipeVersion, CrawledSource, AIRecipeModification, Comment, FavoriteRecipe, RecipeEditRequest, AIProcessingLog, AdminActionLog, Report 스키마
- `src/portal/recipe/model/struct/` — user, recipe, source, ai, comment, favorite, request, admin_log 도메인 로직
- `src/portal/recipe/model/struct.py` — recipe 패키지 Aggregate/Composite Struct 진입점
- `src/portal/recipe/libs/` — 프론트엔드 상수, 타입, 포매터가 필요할 때 사용
- `src/portal/recipe/README.md` — 패키지 내부 API와 사용 예시 문서

### 2.3 기존 `post` 패키지 처리

`post` 패키지는 샘플 또는 기존 게시물 도메인으로 보이며 Recipe Taste Optimizer의 핵심 도메인과 직접 맞지 않는다. MVP 구현에서는 재사용하지 않고, 충돌이 생기지 않는 한 삭제하지 않는다.

## 3. Source App 설계

WIZ App 네이밍은 `{appType}.{viewuri 세그먼트}` 기준을 따른다. URL에 하이픈이 있어도 namespace는 점 구분을 사용한다.

| 화면 | Source App | viewuri | layout | controller | 설명 |
|---|---|---|---|---|---|
| 메인페이지 | `page.home` | `/` | `layout.recipe` | `base` | 비로그인 진입 화면. 검색, 인기/랜덤/최신 레시피 표시 |
| 레시피 목록 | `page.recipes` | `/recipes` | `layout.recipe` | `base` | 공개 레시피 목록, 검색, 필터, 정렬 |
| 레시피 상세 | `page.recipes.item` | `/recipes/:id/:versionId?` | `layout.recipe` | `base` | 요리 상세와 버전 전환. `versionId`는 optional |
| 저염레시피 | `page.low.sodium` | `/low-sodium` | `layout.recipe` | `base` | 저염식 목록과 나트륨 개선 포인트 |
| 이유식레시피 | `page.baby.food` | `/baby-food` | `layout.recipe` | `base` | 월령/단계별 이유식 목록과 안전 필터 |
| 마이페이지 | `page.my` | `/my` | `layout.recipe` | `user` | 프로필, 선호도, 활동 내역 |
| 관리자 | `page.admin` | `/admin/:section?/:id?` | `layout.recipe` | `admin` | 관리자 대시보드와 하위 관리 화면을 내부 탭/섹션으로 처리 |

### 3.1 기존 샘플 앱과의 관계

| 기존 앱 | 처리 방향 |
|---|---|
| `page.dashboard` | `page.home` 또는 `page.admin` 구현 시 참고 후 교체 가능 |
| `page.posts` | `page.recipes` 구현 시 검색/필터 패턴 참고 |
| `page.posts.item` | `page.recipes.item` 구현 시 optional segment와 탭 전환 패턴 참고 |
| `page.members` | 관리자 User Management 카드/모달 패턴 참고 |
| `page.mypage` | `page.my` 구현 시 프로필 폼 패턴 참고 |
| `page.access` | MVP는 로그인 모달을 사용하므로 별도 로그인 페이지로 사용하지 않음. 필요 시 fallback 접근 페이지로 보류 |

실제 앱 생성/삭제는 후속 작업에서 수행한다. 이 문서 단계에서는 기존 샘플 앱을 삭제하지 않는다.

## 4. Layout과 Component 설계

### 4.1 Layout

| Layout | 결정 | 설명 |
|---|---|---|
| `layout.recipe` | 신규 생성 | 공개 서비스와 관리자 진입을 모두 감싸는 공통 레이아웃 |
| `layout.empty` | 유지 | 오류/인증 fallback 등 최소 화면이 필요할 때 사용 가능 |
| `layout.sidebar` | 참고 또는 교체 | 현재 샘플 레이아웃. 제품용 레이아웃은 `layout.recipe`로 분리 권장 |

`layout.recipe`는 다음을 포함한다.

- 상단 또는 좌측 내비게이션
- 메뉴: 메인페이지, 레시피, 저염레시피, 이유식레시피, 마이페이지
- 로그인 버튼과 로그인 모달 진입
- admin role일 때만 Admin Dashboard 버튼 표시
- `wiz-portal-season-modal` 배치
- `router-outlet` 영역

### 4.2 Component

| Component | 역할 |
|---|---|
| `component.auth.login-modal` | 일반 로그인/관리자 로그인 탭을 가진 모달. 실제 인증은 role 기반 단일 API 사용 |
| `component.recipe.card` | 메인/목록/저염/이유식 화면에서 재사용하는 레시피 카드 |
| `component.recipe.filters` | 검색, 카테고리, 태그, 정렬 필터 |
| `component.recipe.source-links` | 원본 출처 링크 목록 |
| `component.recipe.safety-notice` | 저염/이유식/알레르기 주의 문구 표시 |

MVP 초기에는 컴포넌트를 과도하게 쪼개지 않는다. 동일 UI가 2개 이상 화면에서 반복될 때 컴포넌트로 분리한다.

## 5. Controller 적용 기준

| Controller | 적용 대상 | 기준 |
|---|---|---|
| `base` | 공개 페이지, 공개 조회 API | 세션 초기화, 언어 처리, 공개 조회 허용 |
| `user` | 마이페이지, 댓글/즐겨찾기/수정 요청/AI 요청 | 로그인 필수 |
| `admin` | 관리자 Page/API | 로그인 + `role == 'admin'` 필수 |

관리자 권한은 프론트엔드 버튼 노출만으로 판단하지 않는다. 모든 관리자 API와 `page.admin`에는 `admin` controller를 적용한다.

## 6. API와 Route 배치 기준

MVP는 WIZ의 App `api.py`와 Source Route를 역할별로 분리한다.

| API 유형 | 배치 | 기준 |
|---|---|---|
| 화면 전용 API | 각 Page의 `api.py` | 해당 화면에서만 사용하는 조회/저장. `wiz.call()`로 호출 |
| 도메인 공통 API | `src/route/recipe-api` 등 Source Route | 외부 연동 또는 화면 독립 REST 호출이 필요한 API |
| 관리자 운영 API | `src/route/admin-api` 또는 `page.admin/api.py` | 우선 `page.admin/api.py`로 시작하고, 외부 연동 필요 시 Source Route로 분리 |
| AI 처리 API | `src/route/ai-api` 또는 `page.admin/api.py` | 관리자 검수 플로우와 강하게 연결되므로 MVP 초기에는 관리자 API에서 시작 |

초기 구현 우선순위는 App `api.py` 중심이다. REST 형태 문서화는 유지하되, WIZ 화면 연동은 `wiz.call()`을 사용한다. 화면과 무관한 외부 호출이 필요해질 때 Source Route로 승격한다.

## 7. 관리자 화면 구조 결정

관리자 하위 화면은 MVP에서 별도 Source Page로 나누지 않고 `page.admin` 단일 Page 내부 섹션으로 구현한다.

| 섹션 | URL 예시 | 설명 |
|---|---|---|
| Dashboard | `/admin/dashboard` 또는 `/admin` | 지표와 검수 대기 요약 |
| Recipe Management | `/admin/recipes` | 레시피 목록, 등록, 수정, 상태 변경 |
| User Management | `/admin/users` | 사용자 목록, 권한/상태 관리 |
| Comment & Report | `/admin/comments` | 댓글, 신고 처리 |
| AI Management | `/admin/ai` | AI 검수, 프롬프트, 로그 |
| Crawled Source | `/admin/sources` | URL 수집 상태와 출처 관리 |
| Edit Request | `/admin/edit-requests` | 수정 요청 처리 |
| System Log | `/admin/logs` | 작업/오류/권한 로그 |

단일 Page를 선택한 이유:

- MVP에서 앱 개수를 줄여 빌드와 유지보수를 단순화한다.
- 관리자 하위 화면은 공통 필터/테이블/모달을 많이 공유한다.
- `Router.events`로 `section` 변경만 감지하면 탭 전환처럼 처리할 수 있다.
- 화면 규모가 커지면 Phase 5 이후 `page.admin.recipes`, `page.admin.ai` 등으로 분리할 수 있다.

## 8. 생성 순서 제안

후속 구현 작업은 다음 순서가 안전하다.

1. `src/portal/recipe` 패키지 생성
2. `recipe` 패키지 README와 공통 상수 문서 작성
3. DB Model과 Struct 구현
4. `layout.recipe` 생성
5. 로그인 모달과 공통 카드/필터 컴포넌트 생성
6. 공개 Page 생성: `page.home`, `page.recipes`, `page.recipes.item`, `page.low.sodium`, `page.baby.food`
7. 로그인 사용자 Page 생성: `page.my`
8. 관리자 Page 생성: `page.admin`
9. 각 Page `api.py`와 Struct 연결
10. 빌드 및 화면 QA

## 9. 네이밍 규칙

| 대상 | 규칙 | 예시 |
|---|---|---|
| Page 폴더 | `page.{namespace}` | `page.recipes.item` |
| Layout 폴더 | `layout.{namespace}` | `layout.recipe` |
| Component 폴더 | `component.{domain}.{name}` | `component.recipe.card` |
| viewuri | 사용자 URL은 kebab-case 허용 | `/low-sodium`, `/baby-food` |
| namespace | WIZ 폴더명은 점 구분 | `low.sodium`, `baby.food` |
| 관리자 섹션 | URL segment는 kebab-case | `/admin/edit-requests` |
| Portal package | 단수 도메인명 | `recipe` |
| Struct 파일 | snake_case 또는 단일 도메인명 | `recipe.py`, `admin_log.py` |

## 10. 완료 판정

이 문서는 FN-20260501-0002의 완료 기준을 충족한다.

- 활성 프로젝트가 `main`임을 확인했다.
- 신규 Portal Package를 `recipe`로 결정했다.
- Source Page, Layout, Component 후보와 controller 적용 기준을 정리했다.
- 관리자 하위 화면은 MVP에서 `page.admin` 단일 Page 내부 섹션으로 구현하기로 결정했다.
- 앱 생성 작업으로 바로 이어질 수 있는 폴더명, `viewuri`, app id, layout, controller 기준을 문서화했다.

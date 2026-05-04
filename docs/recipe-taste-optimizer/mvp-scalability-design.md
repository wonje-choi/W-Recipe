# Recipe List MVP Scalability Design

- **작성일**: 2026-05-04
- **대상 WIZ 프로젝트**: `main`
- **대상 페이지**: `project/main/src/app/page.recipe.list`
- **목적**: 공개 레시피 목록 페이지의 MVP 구조를 기능, 데이터, 권한, API 확장에 대응 가능한 단위로 재정리한다.

## 1. 대상 페이지 식별

### 1.1 페이지 후보

| 페이지 | 경로 | 역할 | 판단 |
|---|---|---|---|
| `page.recipe.home` | `/` | 추천, 인기, 최신 레시피 진입 | 목록으로 유입시키는 허브 |
| `page.recipe.list` | `/recipes/:preset?` | 검색, 필터, 정렬, 저염/이유식 preset 목록 | 확장성 설계 대상 |
| `page.recipe.detail` | `/recipes/detail/:dishId` | 요리 상세, 버전, 댓글, 수정 요청 | 목록 후속 상세 화면 |
| `page.admin.recipes` | `/admin/recipes` | 관리자 레시피 CRUD와 검수 | 운영 관리 화면 |

`page.recipe.list`를 설계 대상으로 확정한다. 이유는 공개 사용자의 핵심 탐색 흐름이 이 페이지에 집중되어 있고, 저염레시피와 이유식레시피가 같은 페이지의 `preset` 확장으로 이미 구현되어 있어 향후 기능 증가 시 구조 복잡도가 가장 먼저 커질 가능성이 높기 때문이다.

### 1.2 대상 페이지 파일

| 파일 | 존재 | 역할 |
|---|---:|---|
| `project/main/src/app/page.recipe.list/app.json` | O | WIZ page metadata, `/recipes/:preset?` 라우팅 |
| `project/main/src/app/page.recipe.list/view.ts` | O | 필터 상태, URL 동기화, `wiz.call('search')`, 페이지 이동 |
| `project/main/src/app/page.recipe.list/view.pug` | O | 검색 영역, preset 안내, 필터 aside, 카드 목록, 상태 UI |
| `project/main/src/app/page.recipe.list/view.scss` | X | 현재 Tailwind class 중심으로 스타일 구성 |
| `project/main/src/app/page.recipe.list/api.py` | O | 공개 레시피 검색 API, 저염/이유식 preview DTO 생성 |

### 1.3 현재 사용자 흐름

1. 사용자가 `/recipes`, `/recipes/low-sodium`, `/recipes/baby-food` 중 하나로 진입한다.
2. `view.ts`가 URL path와 query string에서 `preset`, 검색어, 카테고리, 태그, 정렬, 이유식 단계를 읽는다.
3. `wiz.call('search')`가 `api.py`의 `search()`를 호출한다.
4. `search()`는 `struct.recipe.search_dishes()`로 승인된 요리 목록을 조회한다.
5. `preset`이 `low-sodium`이면 저염 preview, `baby-food`이면 이유식 preview를 각 카드 DTO에 추가한다.
6. 사용자는 필터를 조정하거나 카드 클릭으로 `/recipes/detail/{dishId}` 상세 페이지로 이동한다.

### 1.4 현재 기능

- 공개 승인 레시피 목록 조회
- 검색어, 카테고리, 태그 필터
- 조회수순, 최신순, 인기순, 난이도순, 조리시간순, AI 개량순 정렬
- 전체/저염/이유식 preset 전환
- 이유식 월령 단계 선택
- 저염 preview: 나트륨 확인 포인트, 고나트륨 재료, 맛 보완 팁
- 이유식 preview: 월령, 입자, 보관, 냉동, 알레르기, 주의 문구
- 로딩 스켈레톤, 결과 없음, 이미지 없음 fallback, 페이지네이션

### 1.5 데이터 흐름

| 구간 | 현재 구조 |
|---|---|
| UI 상태 | `view.ts`의 `filters`, `loading`, `items`, `page`, `totalPages` |
| 서버 호출 | `wiz.call('search', query)` |
| API DTO | `api.py`의 `dish_dto()`, `low_sodium_preview()`, `baby_food_preview()` |
| 비즈니스 로직 | `portal/recipe/model/struct/recipe.py`, `constants.py` |
| DB 모델 | `recipe_dish`, `recipe_version`, 사용자 참여/선호 관련 테이블 |
| 상세 연결 | 카드 클릭 시 `/recipes/detail/{dishId}` |

### 1.6 구조 메모

- `page.recipe.list`는 단순 목록을 넘어 특수 식단 preset별 preview 생성 책임까지 포함하고 있다.
- 검색/필터/정렬 상태와 URL 동기화는 `view.ts`에 모여 있어 이해하기 쉽지만, preset이 늘어나면 조건문이 빠르게 증가한다.
- 저염/이유식 preview 로직은 `api.py`에 위치해 mock 없이 실제 struct를 직접 호출한다.
- 카드 UI는 하나의 `view.pug` 내부에 일반 카드, 저염 카드 확장, 이유식 카드 확장이 함께 들어 있어 컴포넌트 분리 후보가 명확하다.
- 현재 MVP 기준으로는 동작 범위가 적절하지만, 식단 유형, 개인화, 권한별 액션, API 라우트 분리, 관리자 노출 상태가 추가되면 페이지 전용 helper와 공통 component 분리가 필요하다.

## 2. MVP 기능 범위 및 우선순위

### 2.1 페이지 목적

`page.recipe.list`는 사용자가 승인된 레시피를 검색, 필터, 정렬하고 저염/이유식 같은 특수 목적 레시피를 안전 표시와 함께 빠르게 찾도록 돕는 공개 탐색 페이지다.

### 2.2 사용자 유형

| 사용자 유형 | 현재 페이지에서 필요한 행동 | MVP 기준 |
|---|---|---|
| Guest | 승인 레시피 조회, 검색/필터/정렬, 상세 이동 | 핵심 사용자 |
| User | Guest 기능 + 개인화/즐겨찾기/최근 본 레시피로 확장 가능 | 목록에서는 읽기 중심 |
| Admin | 공개 화면 품질 확인, 공개 상태 데이터 검증 | 관리자 기능은 별도 화면 우선 |

### 2.3 핵심 행동

1. 원하는 레시피를 키워드, 카테고리, 태그로 찾는다.
2. 저염 또는 이유식 preset에서 안전/주의 정보를 훑어본다.
3. 카드에서 충분한 요약 정보를 확인한다.
4. 관심 있는 레시피 상세로 이동한다.

### 2.4 기능 우선순위 표

| 기능 | 단계 | 이유 |
|---|---|---|
| 승인 레시피 목록 조회 | MVP | 공개 탐색 페이지의 기본 가치 |
| 검색어 필터 | MVP | 사용자가 원하는 레시피를 직접 찾는 핵심 수단 |
| 카테고리/태그 필터 | MVP | 한국어 레시피 탐색에서 빠른 범위 축소가 필요 |
| 정렬 | MVP | 최신/인기/조회수 등 탐색 우선순위 선택 |
| 페이지네이션 | MVP | 데이터 증가 시 목록 성능과 화면 안정성 유지 |
| 상세 페이지 이동 | MVP | 목록은 탐색 진입점이고 상세가 소비 화면 |
| 로딩/빈/이미지 없음 상태 | MVP | 데이터 상태 변화에도 화면이 깨지지 않도록 필요 |
| 저염 preset | MVP | 서비스 차별화 축인 저염식 탐색 |
| 저염 preview | MVP | 나트륨 확인 포인트와 맛 보완 정보를 목록에서 미리 판단 |
| 이유식 preset | MVP | 서비스 차별화 축인 이유식 탐색 |
| 이유식 월령 단계 | MVP | 월령별 안전 기준이 목록 필터에 직접 연결됨 |
| 이유식 안전 preview | MVP | 알레르기, 질식, 보관 등 보호자 확인 항목 필요 |
| URL query 상태 유지 | MVP | 공유, 새로고침, 뒤로가기 동작 안정성 |
| 즐겨찾기 액션 | V1 | 로그인 사용자 전환과 재방문 가치는 높지만 목록 MVP의 필수는 아님 |
| 최근 본 레시피 반영 | V1 | 상세 방문 후 개인화 탐색 품질 개선 |
| 사용자 선호 기반 추천 정렬 | V1 | 선호 데이터 축적 이후 효율적 |
| 알레르기/비선호 재료 경고 개인화 | V1 | 사용자 설정과 권한 흐름이 안정화된 뒤 추가 |
| 관리자 공개 상태 미리보기 | V1 | 운영 효율 기능이며 공개 사용자 MVP와 분리 가능 |
| 식단 preset 추가 | V1 | 고단백, 당 조절, 간편식 등으로 확장 가능 |
| 무한 스크롤 | Later | SEO, URL 상태, 접근성 측면에서 MVP 페이지네이션이 더 단순 |
| AI 대화형 레시피 추천 | Later | 목록 탐색과 별도 경험이며 비용/품질 리스크가 큼 |
| 외부 장보기/주문 연결 | Later | 결제, 재고, 배송 연동이 필요해 현재 범위 밖 |
| 의료 목적 맞춤 식단 | 제외 | 진단/치료 지침으로 오해될 수 있어 서비스 범위 밖 |

### 2.5 MVP에 반드시 포함할 기능

- 승인 상태 레시피만 목록에 노출
- 검색, 카테고리, 태그, 정렬, 페이지네이션
- 전체/저염/이유식 preset 탐색
- 저염/이유식 preview와 안전 문구
- 로딩, 빈 상태, 이미지 fallback
- URL 기반 상태 보존
- 상세 페이지 이동

### 2.6 지금 제외할 기능

| 제외 기능 | 제외 사유 |
|---|---|
| 목록 내 즐겨찾기/저장 버튼 | 로그인 상태, 중복 처리, 실패 복구 UI가 필요해 V1로 분리 |
| 개인화 추천 정렬 | 선호도와 행동 데이터가 충분히 쌓인 뒤 품질을 검증해야 함 |
| 관리자 액션 직접 노출 | 공개 페이지 책임이 흐려지고 권한 UI가 복잡해짐 |
| 식단 preset 다수 추가 | 저염/이유식 구조를 먼저 안정화한 뒤 config 기반으로 확장 |
| AI 대화형 추천 | 비용, 응답 지연, 안전 문구 검증 부담이 커서 목록 MVP에서 제외 |
| 의료 상담형 표현 | 서비스 정책상 진단/치료/질병 개선 보장 표현 금지 |

## 3. 확장 가능한 페이지 및 컴포넌트 구조

### 3.1 추천 페이지 섹션

| 섹션 | 현재 위치 | 역할 | 확장 기준 |
|---|---|---|---|
| Page Header | `view.pug` 상단 `section` | 제목, 설명, 검색 입력 | preset별 문구는 config에서 가져오도록 확장 |
| Preset Guide | 저염/이유식 조건부 `section` | 특수식단 안내, 안전 문구, 빠른 선택 | diet preset별 guide renderer로 분리 |
| Filter Sidebar | `aside` | 빠른 분류, 카테고리, 태그, 정렬 | 필터 종류가 늘면 config 기반 필터 블록으로 분리 |
| Result Summary | 목록 상단 | 총 개수와 적용 필터 chip | 필터 chip 제거/수정 액션 추가 가능 |
| Loading State | 목록 영역 | 스켈레톤 | 공통 상태 컴포넌트 후보 |
| Empty State | 목록 영역 | 결과 없음 안내 | 검색 없음, 권한 없음, 승인 없음 상태로 확장 |
| Recipe Grid | 목록 영역 | 카드 그리드 | 카드 variant와 action slot을 받을 수 있게 분리 |
| Pagination | 목록 하단 | 페이지 이동 | 기존 `portal/season/app/pagination` 사용 검토 |

### 3.2 추천 컴포넌트 구조

WIZ 구조에서는 페이지 내부가 커질 때 `src/app/component.{name}/` 또는 `src/portal/{package}/app/{component}/`로 분리한다. 이 페이지는 먼저 page 전용 컴포넌트로 분리하고, 다른 페이지에서 재사용되는 시점에 `portal/recipe/app/`로 승격하는 방식이 적절하다.

| 컴포넌트 후보 | 우선 위치 | 책임 | 입력 데이터 |
|---|---|---|---|
| `component.recipe.search-header` | `src/app/component.recipe.search-header` | 제목, 설명, 검색 폼 | `title`, `description`, `searchText`, `preset` |
| `component.recipe.preset-guide` | `src/app/component.recipe.preset-guide` | 저염/이유식 등 preset 안내 | `preset`, `lowSodium`, `babyFood`, `selectedStage` |
| `component.recipe.filter-panel` | `src/app/component.recipe.filter-panel` | 필터/정렬 입력 | `filters`, `categories`, `tags`, `sortOptions`, `presetOptions` |
| `component.recipe.result-summary` | `src/app/component.recipe.result-summary` | 총 개수와 chip | `total`, `filters`, `selectedLabels` |
| `component.recipe.card` | `src/app/component.recipe.card` | 레시피 카드 기본 표시 | `item`, `variant`, `imageUrl` |
| `component.recipe.card-diet-preview` | `src/app/component.recipe.card-diet-preview` | 저염/이유식 preview 표시 | `preset`, `lowSodiumPreview`, `babyPreview` |
| `component.recipe.state` | `src/app/component.recipe.state` | loading/empty/error 표시 | `state`, `message`, `action` |
| `portal/season/app/pagination` | 기존 portal | 페이지네이션 | `page`, `totalPages`, `onChange` |

### 3.3 책임 분리 기준

| 책임 | 유지 위치 | 분리 조건 |
|---|---|---|
| URL 동기화 | `page.recipe.list/view.ts` | 다른 목록 페이지에서도 같은 query 정책을 쓰면 hook/helper로 이동 |
| 필터 상태 | `page.recipe.list/view.ts` | 필터 종류가 5개 이상으로 늘면 `RecipeListFilterState` 타입과 helper로 이동 |
| 검색 API 호출 | `page.recipe.list/api.py` | public route API와 화면 API가 중복되면 route 또는 struct method로 합침 |
| DTO 변환 | `api.py` 단기 유지 | detail/home/admin에서 중복되면 `struct/recipe.py` 또는 DTO helper로 이동 |
| preset별 guide | 컴포넌트 분리 | preset이 3개 이상이면 config-driven renderer로 변경 |
| 카드 diet preview | 컴포넌트 분리 | 카드 variant가 일반/저염/이유식/개인화로 늘어날 때 필수 |

### 3.4 단일 페이지에서 모듈로 확장하는 기준

| 확장 상황 | 권장 구조 |
|---|---|
| preset이 저염/이유식 외 1개 추가 | `presetConfig`로 제목, 설명, guide, API flag를 정의 |
| preset별 필터가 완전히 달라짐 | `/recipes/:preset?` 유지, 필터 패널만 preset별 block으로 교체 |
| preset별 독립 랜딩이 필요 | `page.recipe.low-sodium`, `page.recipe.baby-food`를 만들고 목록 grid component 재사용 |
| 개인화 목록이 필요 | `/recipes/recommended` 또는 마이페이지 섹션으로 분리, 같은 card/grid 재사용 |
| 관리자 미리보기 필요 | 공개 페이지에 admin action을 넣지 않고 `page.admin.recipes`에서 card preview component만 재사용 |

### 3.5 WIZ 구조 적용안

```txt
project/main/src/app/
  page.recipe.list/
    app.json
    view.ts
    view.pug
    api.py
  component.recipe.search-header/
  component.recipe.preset-guide/
  component.recipe.filter-panel/
  component.recipe.result-summary/
  component.recipe.card/
  component.recipe.state/

project/main/src/portal/recipe/
  model/struct/recipe.py
  model/struct/safety.py
  model/constants.py
  libs/constants.ts
```

MVP 다음 단계에서는 위 컴포넌트 후보를 모두 한 번에 만들기보다 `recipe.card`, `recipe.filter-panel`, `recipe.state`부터 분리하는 편이 효과적이다. 이 세 영역이 현재 `view.pug`의 반복/조건부 복잡도를 가장 많이 줄인다.

## 4. 데이터 모델, 상태 관리, API 전환 구조

### 4.1 주요 엔티티

| 엔티티 | 역할 | 현재 근거 |
|---|---|---|
| `RecipeDish` | 목록 카드의 요리 단위 | `recipe_dish`, `dish_dto()` |
| `RecipeVersion` | 승인된 상세 버전과 preview 산출 근거 | `recipe_version`, `versions()` |
| `RecipeListFilter` | 검색/필터/정렬/query 상태 | `view.ts filters`, `api.py search()` query |
| `DietPreset` | 전체/저염/이유식 등 목록 변형 | URL `preset`, `preset_filters()` |
| `DietPreview` | preset별 카드 확장 정보 | `lowSodiumPreview`, `babyPreview` |
| `PaginationState` | 목록 페이지 상태 | `page`, `dump`, `total`, `totalPages` |
| `UiRequestState` | 로딩/빈/에러/권한 없음 상태 | 현재 `loading`, `items.length === 0` |

### 4.2 데이터 모델 예시

```ts
type RecipeDishListItem = {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  thumbnailUrl: string;
  hasImage: boolean;
  viewCount: number;
  status: 'approved';
  createdAt: string;
  updatedAt: string;
  dietPreview?: LowSodiumPreview | BabyFoodPreview;
  permissions?: RecipeListItemPermission;
  metadata?: Record<string, any>;
};

type RecipeListFilter = {
  text: string;
  preset: '' | 'low-sodium' | 'baby-food' | string;
  category: string;
  tag: string;
  sort: 'view_count' | 'latest' | 'popular' | 'difficulty' | 'cooking_time' | 'ai_modified' | string;
  babyStage?: '' | 'early' | 'middle' | 'late' | 'complete';
  page: number;
  dump: number;
};

type RecipeListResponse = {
  items: RecipeDishListItem[];
  filters: RecipeListFilter;
  page: number;
  dump: number;
  total: number;
  empty: boolean;
  categories: string[];
  tags: string[];
  presets: DietPreset[];
};
```

Python/WIZ API에서는 DB 필드를 snake_case로 유지하고 `api.py` 또는 DTO helper에서 camelCase로 변환한다. `metadata`는 MVP에서 적극 사용하지 않더라도 실험적 badge, ranking reason, personal reason 같은 후속 정보가 생길 때 기존 카드 계약을 깨지 않도록 남겨둘 수 있다.

### 4.3 확장 필드 기준

| 필드 | 적용 대상 | 용도 |
|---|---|---|
| `status` | Dish, Version, Comment, Request | 공개/검수/숨김 등 상태 전환 |
| `role` | User, Permission | guest/user/admin/premium/expert 확장 |
| `metadata` | DTO | 실험적 UI 정보, 추천 이유, 외부 연동 정보 |
| `createdAt`, `updatedAt` | 모든 주요 엔티티 | 정렬, 감사, 캐시 무효화 |
| `reviewedBy`, `reviewedAt` | Version, AI result | 관리자 검수 추적 |
| `sourceType`, `sourceUrl` | Version | 출처 정책과 원문 링크 |
| `aiModified` | Version/Preview | AI 개량 여부 표시 |

### 4.4 상태 관리 기준

| 상태 | 위치 | 설명 | 확장 방향 |
|---|---|---|---|
| `filters` | local UI state | URL query와 동기화되는 검색 조건 | `RecipeListFilter` helper로 분리 |
| `loading` | local UI state | `wiz.call('search')` 진행 중 | `requestState: 'idle'|'loading'|'success'|'error'`로 확장 |
| `items`, `total` | server data state | API 응답 데이터 | 캐시/재시도 필요 시 service layer로 분리 |
| `filtersOpen` | local UI state | 모바일 필터 열림 | 컴포넌트 내부 상태로 이동 가능 |
| `lowSodium`, `babyFood` | server config state | preset guide와 preview 표시 기준 | `presets` 배열 기반 config로 통합 |
| `errorMessage` | 추가 필요 | 현재 search 실패 UI가 명시적이지 않음 | 에러 상태 컴포넌트와 retry 액션 추가 |
| `permission` | 추가 가능 | 권한별 action 노출 | API 응답의 `permissions` 또는 policy helper |

### 4.5 화면 상태 정의

| 상태 | 조건 | UI 기준 |
|---|---|---|
| Loading | `requestState === 'loading'` | grid 크기를 유지하는 skeleton |
| Empty | 요청 성공, `items.length === 0` | 조건 완화와 전체 보기 액션 |
| Error | API 실패 | 오류 메시지, 재시도, 전체 목록 이동 |
| Unauthorized | 로그인 필요 action 클릭 | 목록은 유지하고 로그인 모달 또는 안내 |
| Forbidden | 권한 없는 role action | action 비노출이 기본, 직접 접근 시 안내 |
| Partial Preview | recipe는 있으나 version preview 없음 | 카드에 "정보 준비 중" 수준으로 표시 |

### 4.6 API 레이어 전환 구조

현재 화면 API는 `page.recipe.list/api.py`의 `search()`가 직접 DTO를 구성한다. MVP 다음 단계에서는 중복을 줄이기 위해 아래 순서로 분리한다.

```txt
view.ts
  -> recipeListService.search(filters)
    -> wiz.call('search', filters)
      -> page.recipe.list/api.py
        -> struct.recipe.search_public_list(filters)
          -> struct.safety.low_sodium_preview(dish_id)
          -> struct.safety.baby_food_preview(dish_id, stage)
```

| 단계 | MVP | V1 전환 |
|---|---|---|
| UI 호출 | `wiz.call('search')` 직접 호출 | `recipeListService.search()` wrapper |
| DTO 생성 | `api.py` 내부 함수 | `struct` 또는 `portal/recipe` DTO helper |
| preset filter | `preset_filters()` 조건문 | `DietPresetConfig` |
| safety preview | `api.py` 함수 | `struct/safety.py` 또는 dedicated preview struct |
| route API | 별도 public route 존재 | page API와 route API의 응답 계약 정렬 |

### 4.7 Mock에서 실제 API로 전환하기 쉬운 방식

- mock을 만들 경우 `RecipeListResponse` 형태를 실제 `search()` 응답과 동일하게 둔다.
- UI 컴포넌트는 `wiz.call` 결과의 원본이 아니라 정규화된 `RecipeListResponse`만 받는다.
- `categories`, `tags`, `presets`, `sortOptions`는 API config 응답 또는 constants 기반으로 공급한다.
- preview가 준비되지 않은 경우에도 `dietPreview.available=false` 형태로 내려 카드 렌더링 분기를 단순화한다.
- 실패 응답은 `{ code, message, errors? }` 형태로 고정해 error state component가 재사용 가능하게 한다.

## 5. 권한, 사용자 유형, UX 상태 확장 설계

### 5.1 사용자 유형과 권한 기준

| 사용자 유형 | 목록 조회 | 필터/정렬 | 상세 이동 | 참여 액션 | 관리자 액션 |
|---|---:|---:|---:|---:|---:|
| Guest | 가능 | 가능 | 가능 | 로그인 유도 | 불가 |
| User | 가능 | 가능 | 가능 | 가능 | 불가 |
| Premium User | 가능 | 가능 | 가능 | 가능 | 프리미엄 badge/필터 가능 |
| Expert | 가능 | 가능 | 가능 | 전문 검수 표시 가능 | 배정된 검수만 가능 |
| Admin | 가능 | 가능 | 가능 | 가능 | 관리자 화면에서 처리 |

공개 목록 페이지의 기본 정책은 action 비노출이다. 권한에 따라 추가되는 기능은 카드 내부에 직접 조건문을 흩뿌리지 않고 `permissions` DTO 또는 `canRecipeListAction(user, item, action)` 형태의 policy helper로 판단한다.

### 5.2 권한 제어 대상

| 대상 | MVP | V1 이후 |
|---|---|---|
| 레시피 조회 | guest 가능, approved만 노출 | premium/expert 전용 filter 가능 |
| 즐겨찾기 | 제외 | user 이상, 실패 시 inline feedback |
| 최근 본 레시피 | 상세에서 기록 | 목록 ranking 또는 badge에 활용 |
| AI 개량 요청 | 상세/별도 페이지 | user 이상, 목록 quick action은 후순위 |
| 관리자 검수/숨김 | 목록에는 비노출 | admin 화면에서만 처리 |
| 전문가 검수 표시 | 제외 | expert assignment와 연결 |

### 5.3 권한 로직 분리안

```txt
api.py
  -> current_user()
  -> build_item_permissions(user, dish)
  -> item.permissions

view.ts
  -> canShowAction(item, 'favorite')
  -> component.recipe.card receives permissions

policy helper
  -> canRecipeListAction(userRole, itemStatus, action)
```

MVP에서는 목록 조회가 public이므로 권한 로직을 최소화한다. V1에서 action이 생기면 API 응답에 `permissions`를 포함해 UI가 role/status 조합을 직접 계산하지 않게 한다.

### 5.4 UX 흐름

| 단계 | 사용자 목표 | 화면 기준 |
|---|---|---|
| 진입 | 전체/저염/이유식 중 원하는 범위로 시작 | path preset을 제목과 guide에 즉시 반영 |
| 탐색 | 검색/필터/정렬로 후보 축소 | 필터는 좌측, 결과는 우측, 모바일은 접기 |
| 비교 | 카드에서 핵심 정보와 안전 preview 확인 | 카드 높이와 정보 밀도를 안정적으로 유지 |
| 상세 이동 | 관심 레시피를 자세히 확인 | 카드 전체 클릭, 명확한 hover/focus |
| 결과 없음 | 조건 수정 또는 전체 목록 복귀 | 빈 상태에서 직접 액션 제공 |
| 오류 | 재시도 또는 안전한 복귀 | error state에 retry/전체 보기 제공 |

### 5.5 반응형 기준

| 뷰포트 | 레이아웃 |
|---|---|
| Mobile | 검색은 상단 full-width, 필터는 접힘, 카드 1열, 상태 UI는 목록 위치 유지 |
| Tablet | 카드 2열, 필터는 필요 시 접힘, preset guide는 1~2열 |
| Desktop | 좌측 260px 필터, 우측 목록, 카드 3열, header 검색은 우측 정렬 |

필터가 늘어날 경우 모바일에서 한 화면을 과도하게 차지하지 않도록 filter drawer 또는 accordion 방식으로 확장한다. Desktop에서는 필터 영역을 고정 폭으로 유지해 목록 grid가 흔들리지 않게 한다.

### 5.6 기능 증가 시 화면 우선순위

| 우선순위 | 정보/액션 | 이유 |
|---|---|---|
| 1 | 검색어, preset, 결과 수 | 탐색 맥락 유지 |
| 2 | 레시피명, 설명, 카테고리, 태그 | 카드 선택 판단 |
| 3 | 저염/이유식 안전 preview | 서비스 차별화와 안전 안내 |
| 4 | 정렬, 카테고리, 태그 | 탐색 세분화 |
| 5 | 즐겨찾기, 개인화 badge | V1 이후 추가 액션 |
| 6 | 관리자/전문가 표시 | 공개 목록에서는 보조 정보 |

### 5.7 사용자 피드백 기준

| 상황 | 피드백 |
|---|---|
| 검색 실행 | URL query 갱신 후 loading skeleton |
| 필터 적용 | 적용된 filter chip 표시 |
| 필터 초기화 | `/recipes`로 복귀 |
| 즐겨찾기 성공 | 카드 action 영역에 짧은 상태 표시 |
| 로그인 필요 | 현재 목록 유지, 로그인 modal 또는 안내 |
| API 실패 | 목록 영역 error state, retry |
| 권한 없음 | action 비노출, 직접 접근 시 forbidden 안내 |

피드백은 목록 탐색을 방해하지 않는 위치에 둔다. 전역 alert보다 카드 action 영역 또는 목록 state 영역을 우선한다.

## 6. 최종 설계 요약 및 후속 구현 TODO 후보

### 6.1 페이지 목적 요약

`page.recipe.list`는 공개 승인 레시피를 빠르게 탐색하고, 저염/이유식처럼 안전 표시가 필요한 특수식단 정보를 목록 단계에서 미리 판단하게 하는 핵심 탐색 화면이다.

### 6.2 MVP 핵심 기능

- 승인 레시피 목록 조회
- 검색, 카테고리, 태그, 정렬
- 전체/저염/이유식 preset
- 저염 preview와 이유식 안전 preview
- 로딩, 빈 상태, 이미지 fallback, 페이지네이션
- URL 기반 상태 보존
- 상세 페이지 이동

### 6.3 확장 가능한 페이지 구조

| 영역 | 확장 방향 |
|---|---|
| Header | preset config 기반 제목/설명/검색 폼 |
| Preset Guide | diet preset별 guide component |
| Filter Sidebar | filter block config 기반 확장 |
| Result Summary | 적용 필터 chip과 제거 액션 |
| Recipe Grid | card component와 variant slot |
| State UI | loading/empty/error/forbidden 공통 상태 |
| Pagination | portal pagination 재사용 검토 |

### 6.4 추천 컴포넌트 구조

1. `component.recipe.card`
2. `component.recipe.filter-panel`
3. `component.recipe.state`
4. `component.recipe.preset-guide`
5. `component.recipe.result-summary`
6. `component.recipe.search-header`

우선순위는 현재 `view.pug`의 조건부 복잡도와 반복도를 기준으로 정한다. 카드, 필터, 상태 UI부터 분리하면 페이지 본문이 가장 빠르게 단순해진다.

### 6.5 데이터 모델 예시

핵심 계약은 `RecipeListResponse` 하나로 묶는다.

```ts
type RecipeListResponse = {
  items: RecipeDishListItem[];
  filters: RecipeListFilter;
  page: number;
  dump: number;
  total: number;
  empty: boolean;
  categories: string[];
  tags: string[];
  presets: DietPreset[];
};
```

API 응답이 이 구조를 유지하면 mock, page API, public route API, 컴포넌트 테스트를 같은 데이터 형태로 다룰 수 있다.

### 6.6 향후 확장 시나리오

| 시나리오 | 대응 구조 |
|---|---|
| 식단 preset 추가 | `DietPresetConfig`와 guide/card preview renderer 추가 |
| 개인화 추천 | `metadata.personalReason`, `permissions`, 사용자 선호 API 연결 |
| 즐겨찾기 액션 | card action slot, `permissions.canFavorite`, optimistic update |
| 전문가 검수 표시 | item badge와 review metadata 추가 |
| 관리자 미리보기 | admin page에서 card component 재사용, action은 admin page에만 배치 |
| API route 통합 | `struct.recipe.search_public_list()` 중심으로 page API와 route API 정렬 |
| 테스트 확장 | `RecipeListResponse` fixture로 loading/empty/error/success 상태 테스트 |

### 6.7 구현 시 주의할 점

- 공개 목록 페이지에는 `approved` 상태만 노출한다.
- 저염/이유식 문구는 의료 상담이나 치료 보장처럼 보이지 않게 유지한다.
- preset이 늘어날 때 `if preset == ...` 조건문을 계속 추가하지 말고 config와 renderer로 전환한다.
- UI 컴포넌트는 `wiz.call`을 직접 호출하지 않고 정규화된 props만 받도록 분리한다.
- 권한 action은 숨김이 기본이며, 직접 접근 방어는 API에서 처리한다.
- 컴포넌트 분리는 한 번에 크게 하지 말고 카드, 필터, 상태 UI 순서로 진행한다.

### 6.8 후속 구현 TODO 후보

```md
# FN-20260504-0007: 레시피 목록 카드 컴포넌트 분리
- 목표: `page.recipe.list/view.pug`의 카드 렌더링을 `component.recipe.card`로 분리한다.
- 작업:
  - 카드 기본 정보 영역과 이미지 fallback 로직을 컴포넌트 props로 분리한다.
  - 저염/이유식 preview 영역은 별도 입력으로 받아 조건부 렌더링한다.
  - 기존 카드 클릭 상세 이동 동작을 유지한다.
- 완료 기준:
  - 목록 카드 UI가 기존과 동일하게 동작한다.
  - `page.recipe.list/view.pug`의 카드 관련 중첩이 줄어든다.

# FN-20260504-0008: 레시피 목록 필터 패널 컴포넌트 분리
- 목표: 빠른 분류, 카테고리, 태그, 정렬 영역을 `component.recipe.filter-panel`로 분리한다.
- 작업:
  - `filters`, `categories`, `tags`, `sortOptions`, `presetOptions`를 props로 전달한다.
  - 필터 변경과 적용 이벤트를 페이지로 전달한다.
  - 모바일 접힘 상태와 desktop 표시를 유지한다.
- 완료 기준:
  - 필터 동작과 URL query 결과가 기존과 동일하다.
  - 필터 UI 책임이 페이지 본문에서 분리된다.

# FN-20260504-0009: 레시피 목록 상태 UI와 에러 상태 추가
- 목표: loading/empty/error 상태를 `component.recipe.state`로 통합한다.
- 작업:
  - 기존 loading skeleton과 empty state를 공통 상태 컴포넌트로 분리한다.
  - `view.ts`에 `errorMessage` 또는 `requestState`를 추가한다.
  - API 실패 시 재시도 또는 전체 목록 이동 액션을 제공한다.
- 완료 기준:
  - 성공/빈/로딩/실패 상태가 모두 명확히 표시된다.
  - 기존 검색과 필터 동작에 영향이 없다.

# FN-20260504-0010: DietPresetConfig 기반 preset 구조 정리
- 목표: 저염/이유식 preset 조건문을 config 기반 구조로 전환한다.
- 작업:
  - preset별 title, description, category, tag, preview flag를 정의한다.
  - `preset_filters()`와 `view.ts` preset 문구를 config 기준으로 정리한다.
  - 새 preset 추가 시 수정 범위를 줄인다.
- 완료 기준:
  - 기존 `/recipes`, `/recipes/low-sodium`, `/recipes/baby-food` 동작이 유지된다.
  - preset 추가 지점이 config 중심으로 정리된다.
```

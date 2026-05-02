# Recipe Taste Optimizer Portal Package

`recipe` 패키지는 Recipe Taste Optimizer의 도메인 모델, Struct, 프론트엔드 상수, 향후 공용 컴포넌트를 담는 재사용 패키지다.

## Package Metadata

- Package: `recipe`
- Version: `0.1.0`
- Model: enabled
- Libs: enabled

## Backend Constants

```python
constants = wiz.model("portal/recipe/constants")
```

주요 정책 값은 `model/constants.py`에서 관리한다.

- User roles: `guest`, `user`, `admin`
- User statuses: `active`, `suspended`, `deleted`, `pending`
- Recipe statuses: `draft`, `crawled`, `ai_parsed`, `ai_modified`, `pending_review`, `approved`, `rejected`, `hidden`
- Public recipe status: `approved`
- Source types: `youtube`, `blog`, `web`, `direct`, `ai_modified`
- Crawling statuses: `pending`, `allowed`, `blocked`, `collected`, `summarized`, `failed`, `expired`
- AI statuses: `queued`, `processing`, `pending_review`, `approved`, `rejected`, `failed`
- AI processing statuses: `queued`, `processing`, `completed`, `failed`
- AI prompt types: `recipe_summary`, `low_sodium`, `baby_food`, `taste_improvement`, `review_summary`
- Comment statuses: `visible`, `hidden`, `deleted`, `reported`
- Edit request statuses: `open`, `in_review`, `resolved`, `rejected`
- Report statuses: `open`, `in_review`, `actioned`, `rejected`
- Default categories: `일반`, `저염`, `이유식`, `다이어트`, `고단백`, `반찬`, `국/찌개`, `죽/미음`
- Default tags: `저염`, `이유식`, `고단백`, `다이어트`, `간단요리`, `부드러운 식감`

## Public Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/recipes` | 승인된 공개 레시피 목록 |
| GET | `/api/recipes/<dish_id>` | 승인된 요리 상세와 대표 버전 |
| GET | `/api/recipes/<dish_id>/versions` | 승인된 버전 목록 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>` | 승인된 버전 상세 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/source` | 원본 출처 링크 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/compare` | 기준 버전과 대상 버전 비교 |
| POST | `/api/recipes/<dish_id>/views` | 세션 기준 요리 조회수 증가 |
| POST | `/api/recipes/<dish_id>/versions/<version_id>/views` | 세션 기준 버전 조회수 증가 |

공개 Route는 controller 없이 실행되며 `approved` 상태만 반환한다.

## Admin Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/recipes` | 전체 상태 레시피 목록 |
| POST | `/api/admin/recipes` | 레시피 Dish 생성 |
| GET | `/api/admin/recipes/<dish_id>` | 레시피 Dish 상세 |
| PUT | `/api/admin/recipes/<dish_id>` | 레시피 Dish 수정 |
| DELETE | `/api/admin/recipes/<dish_id>` | 레시피 Dish 숨김 처리 |
| GET | `/api/admin/recipes/<dish_id>/versions` | 전체 상태 Version 목록 |
| POST | `/api/admin/recipes/<dish_id>/versions` | Version 생성 |
| GET | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 상세 |
| PUT | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 수정 |
| DELETE | `/api/admin/recipes/<dish_id>/versions/<version_id>` | Version 숨김 처리 |

관리자 Route는 `admin` controller를 사용하고, 모든 변경에 `AdminActionLog`를 남긴다.

## Admin Source Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/sources` | 출처 목록 |
| POST | `/api/admin/sources` | URL 등록과 중복 확인 |
| GET | `/api/admin/sources/<source_id>` | 출처 상세 |
| PUT | `/api/admin/sources/<source_id>` | 출처 메타데이터 수정 |
| DELETE | `/api/admin/sources/<source_id>` | 출처 만료 처리 |
| PUT | `/api/admin/sources/<source_id>/status` | robots/crawl 상태 수정 |

## Admin AI Prompt Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/ai/prompts` | AI 프롬프트 버전 목록 |
| POST | `/api/admin/ai/prompts` | AI 프롬프트 버전 생성 |
| GET | `/api/admin/ai/prompts/<prompt_id>` | AI 프롬프트 상세 |
| PUT | `/api/admin/ai/prompts/<prompt_id>` | AI 프롬프트 수정 |
| DELETE | `/api/admin/ai/prompts/<prompt_id>` | AI 프롬프트 비활성화 |
| PUT | `/api/admin/ai/prompts/<prompt_id>/activate` | 활성 프롬프트 버전 변경 |
| PUT | `/api/admin/ai/prompts/<prompt_id>/deactivate` | AI 프롬프트 비활성화 |

`promptVersion`은 `{promptKey}:{version}` 형식이며, `struct.ai.create_log()`는 명시된 `prompt_version`을 검증하거나 `prompt_key`의 활성 버전을 찾아 로그에 저장한다.

## Admin AI Pipeline Routes

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/admin/ai/recipe-summary` | URL/직접 입력 텍스트를 레시피 구조 후보로 요약하고 검수 대기 Version 생성 |
| POST | `/api/ai/recipe-modifications` | 로그인 사용자/관리자의 특수식단 개량안을 생성하고 검수 대기 AI Modification 저장 |

레시피 요약 파이프라인은 YouTube, blog, web URL과 직접 입력 텍스트를 처리한다. 외부 URL은 `crawled_source`와 연결하고, 생성 결과는 `pending_review` 상태의 `recipe_dish`/`recipe_version`으로 저장한다.
특수식단 개량 파이프라인은 승인된 레시피 버전 또는 관리자 권한의 내부 버전을 입력으로 받아 `ai_recipe_modification`에 `pending_review` 결과를 저장한다.

## Frontend Constants

```typescript
import {
    USER_ROLES,
    RECIPE_STATUSES,
    AI_PROMPT_TYPES,
    DEFAULT_CATEGORIES,
    DEFAULT_TAGS,
    STATUS_LABELS,
    PAGINATION,
} from '@wiz/libs/portal/recipe/constants';
```

프론트엔드 표시 텍스트는 `STATUS_LABELS`를 사용하고, 저장 값은 lowercase snake_case 상수를 사용한다.

## Struct API

```python
struct = wiz.model("portal/recipe/struct")
```

| 속성 | 역할 |
| --- | --- |
| `struct.auth` | 로그인, 로그아웃, 세션 사용자 조회, role 검증, 비밀번호 해시 |
| `struct.user` | 사용자, 로그인 기록, 취향 프로필 |
| `struct.recipe` | 레시피 Dish/Version 생성, 수정, 공개 검색, 조회수 |
| `struct.source` | 외부 URL 수집 이력, URL 해시 중복 판별, 크롤링 상태 |
| `struct.ai` | AI 프롬프트 버전, AI 요약 파이프라인, AI 개량 결과와 처리 로그, 관리자 승인/반려 |
| `struct.ai_diet` | 특수식단 개량 요청 처리, 목적별 프롬프트 fallback, AI Modification 생성 |
| `struct.safety` | 알레르기, 나트륨, 이유식, 생식/질식, 의료 표현 위험 후보 탐지 |
| `struct.comment` | 댓글, 즐겨찾기, 수정 요청, 신고 |
| `struct.admin_log` | 관리자 감사 로그와 before/after 마스킹 |

공개 조회는 기본적으로 `approved` 상태만 반환한다. AI 결과는 `pending_review`로 생성되며 관리자 승인 전까지 공개 데이터로 사용하지 않는다.
관리자 전체 상태 조회는 `struct.require_admin()`을 통과하는 `struct.recipe.admin_search_dishes()`와 `struct.recipe.admin_versions()`에서 처리한다.

## Auth API

```python
struct.auth.login(email, password)
struct.auth.logout()
struct.auth.current_user()
struct.auth.require_login()
struct.auth.require_admin()
```

- 일반 사용자와 관리자는 동일한 로그인 로직을 사용하고 `role`만 다르게 저장한다.
- 로그인 실패 5회부터 15분간 계정을 잠근다.
- `user` controller는 active 로그인 사용자만 통과시키고, `admin` controller는 admin role만 통과시킨다.
- 비밀번호 해시는 `pbkdf2_sha256$iterations$salt$digest` 형식이다.

## Seed API

```python
seed = wiz.model("portal/recipe/seed")
result = seed.run(admin_email="", admin_password_hash="")
```

- 고정 ID와 upsert 방식으로 동작하므로 여러 번 실행해도 중복 생성되지 않는다.
- 관리자 계정은 `admin_email`과 안전하게 생성된 `admin_password_hash`가 모두 전달될 때만 생성한다.
- 기본 실행은 샘플 공개 레시피, 검수 대기 AI 버전, 데모 사용자 취향 데이터를 준비한다.

## DB Models

| Model | Table | Purpose |
| --- | --- | --- |
| `user` | `recipe_user` | 이메일 기반 사용자와 역할/상태/잠금 정보 |
| `user_preference` | `recipe_user_preference` | 알레르기, 식단, 선호/비선호 재료, 조리 목표 |
| `recipe_dish` | `recipe_dish` | 레시피 그룹, 대표 메타데이터, 공개 상태 |
| `recipe_version` | `recipe_version` | 원본/개량 버전의 재료, 단계, 영양, 난이도 |
| `crawled_source` | `recipe_crawled_source` | 외부 출처 URL, robots 허용, 수집 상태, 중복 판정 |
| `ai_prompt_template` | `recipe_ai_prompt_template` | AI 프롬프트 템플릿, 버전, 활성 여부, 변경 사유 |
| `ai_recipe_modification` | `recipe_ai_modification` | AI 레시피 개량 결과와 관리자 검토 상태 |
| `ai_processing_log` | `recipe_ai_processing_log` | AI 요청 처리 상태, 지연시간, 비용, 오류 기록 |
| `comment` | `recipe_comment` | 레시피 버전별 댓글/대댓글과 숨김 처리 |
| `favorite_recipe` | `recipe_favorite` | 사용자별 즐겨찾기, 동일 사용자/버전 중복 방지 |
| `recipe_edit_request` | `recipe_edit_request` | 사용자 레시피 수정 제안과 검토 상태 |
| `report` | `recipe_report` | 댓글/레시피/사용자 신고와 처리 상태 |
| `admin_action_log` | `recipe_admin_action_log` | 관리자 주요 변경 행위 감사 로그 |

DB 모델은 schema만 담당하고, 업무 규칙은 `portal/recipe/struct` 계층에 둔다.

## Visibility Policy

- 공개 레시피는 반드시 `approved` 상태여야 한다.
- `draft`, `crawled`, `ai_parsed`, `ai_modified`, `pending_review`, `rejected`, `hidden` 상태는 일반 사용자 공개 목록에서 제외한다.
- 삭제성 조치는 MVP에서 물리 삭제보다 상태 변경(`hidden`)을 우선한다.

## Source Collection Policy

- 외부 URL은 `source_url_hash`로 중복 판정한다.
- 긴 URL 자체에는 unique index를 걸지 않는다.
- `raw_content_storage_policy` 기본값은 `summary_only`이며, 원문 전문 보관은 별도 승인 후 확장한다.

## AI Review Policy

- AI 개량 결과는 기본 `pending_review`로 생성한다.
- 관리자 승인 후에만 레시피 공개 후보가 된다.
- AI 로그에는 전체 프롬프트/원문 대신 요청 요약과 응답 요약을 저장한다.
- AI 로그의 `prompt_version`은 등록된 프롬프트 버전 또는 `prompt_key`의 활성 버전을 통해 추적한다.
- AI 요약 결과는 재료/계량/조리 순서/팁 후보로 저장하고, 불확실한 항목은 `failure_prevention_tips`에 확인 필요 문구로 남긴다.
- 특수식단 개량 결과는 `ai_recipe_modification`에 저장하며, 저염식/이유식/다이어트/고단백 등 목적별 근거와 주의사항을 구조화한다.
- 관리자 검수 API는 Version과 AI Modification 항목에 `safety`와 `riskFlags`를 포함해 알레르기, 고나트륨, 이유식 부적합, 생식/질식, 의료 표현 위험 후보를 표시한다.

## Engagement Policy

- 댓글은 기본 `visible` 상태로 생성한다.
- 신고/관리자 조치 시 댓글은 `hidden` 또는 `deleted` 상태로 전환한다.
- 즐겨찾기 추가/해제는 `struct.comment.toggle_favorite()`에서 사용자와 레시피 버전 조합 기준으로 처리한다.
- 즐겨찾기는 사용자와 레시피 버전 조합이 유일해야 한다.
- 같은 사용자가 같은 대상에 중복 신고하지 않도록 `reporter_user_id`, `target_type`, `target_id` 조합을 유일하게 둔다.

## Admin Audit Policy

- 관리자 주요 변경은 `admin_action_log`에 남긴다.
- `before_value`와 `after_value`에는 password, token, rawContent, allergies, medicalNotes 등 민감 정보를 원문으로 저장하지 않는다.
- 변경 이력은 화면에서 조회할 수 있도록 `action_type`, `target_type`, `target_id`, `admin_user_id`, `created_at` 기준 검색을 지원한다.

## Privacy Policy

- `SENSITIVE_PROFILE_FIELDS`에 정의된 프로필 정보는 AI 요청과 관리자 로그에 원문 저장하지 않는다.
- 알레르기/건강 메모는 레시피 개인화 계산에만 사용하고, 운영 로그에는 요약 또는 마스킹 값만 남긴다.

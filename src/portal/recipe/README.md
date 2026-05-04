# Recipe Taste Optimizer Portal Package

`recipe` 패키지는 Recipe Taste Optimizer의 도메인 모델, Struct, 프론트엔드 상수, 향후 공용 컴포넌트를 담는 재사용 패키지다.

상세 화면/API 계약은 [API.md](API.md)를 기준으로 한다.
관리자 운영 정책은 [OPERATIONS.md](OPERATIONS.md)를 기준으로 한다.
회귀 테스트 체크리스트는 [QA.md](QA.md)를 기준으로 한다.
배포 준비와 롤백 절차는 [DEPLOYMENT.md](DEPLOYMENT.md)를 기준으로 한다.
2026-05-01 통합 QA 결과는 [QA-RESULT-2026-05-01.md](QA-RESULT-2026-05-01.md)를 기준으로 한다.

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
- User statuses: `active`, `locked`, `deleted`
- Recipe statuses: `draft`, `pending_review`, `approved`, `rejected`, `archived`, `deleted`
- Public recipe status: `approved`
- Source types: `web`, `youtube`, `manual`, `admin_upload`
- Crawling statuses: `pending`, `allowed`, `blocked`, `collected`, `failed`, `duplicate`
- AI result statuses: `pending_review`, `approved`, `rejected`, `failed`
- AI processing statuses: `queued`, `processing`, `completed`, `failed`
- Comment statuses: `visible`, `hidden`, `deleted`
- Edit request statuses: `open`, `in_review`, `resolved`, `rejected`
- Edit request types: `error`, `measurement_issue`, `source_issue`, `taste_improvement`, `other`
- Report statuses: `open`, `in_review`, `actioned`, `rejected`
- Report targets: `comment`, `recipe_version`, `recipe_dish`
- Report reasons: `spam`, `inappropriate`, `wrong_info`, `safety_issue`, `copyright`, `other`

## Source Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/sources` | 출처 목록 |
| POST | `/api/admin/sources` | URL 등록과 중복 확인 |
| GET | `/api/admin/sources/<source_id>` | 출처 상세 |
| PUT | `/api/admin/sources/<source_id>` | 출처 메타데이터 수정 |
| DELETE | `/api/admin/sources/<source_id>` | 출처 만료 처리 |
| PUT | `/api/admin/sources/<source_id>/status` | robots/crawl 상태 수정 |

출처 Route는 `admin` controller를 사용하고, 원문 전문 저장 대신 요약 후보 중심으로 관리한다.

## Review Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/reviews/pending` | 검수 대기 Dish, Version, AI 결과 목록 |
| POST | `/api/admin/reviews/<target_type>/<target_id>/approve` | 검수 대상 승인 |
| POST | `/api/admin/reviews/<target_type>/<target_id>/reject` | 검수 대상 반려 |

검수 Route는 `admin` controller를 사용하고, 승인/반려 시 `AdminActionLog`를 남긴다.

## Engagement Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/recipes/<version_id>/comments` | 공개 레시피 버전 댓글 목록 |
| POST | `/api/recipes/<version_id>/comments` | 로그인 사용자 댓글 작성 |
| DELETE | `/api/comments/<comment_id>` | 댓글 작성자 또는 admin의 댓글 삭제 요청 |
| GET | `/api/recipes/<version_id>/favorite` | 현재 사용자의 즐겨찾기 여부 |
| POST | `/api/recipes/<version_id>/favorite` | 현재 사용자의 즐겨찾기 토글 |
| DELETE | `/api/recipes/<version_id>/favorite` | 현재 사용자의 즐겨찾기 해제 |
| GET | `/api/users/me/recent-views` | 현재 사용자의 최근 본 레시피 목록 |
| POST | `/api/users/me/recent-views` | 현재 사용자의 최근 본 레시피 저장 |

댓글 목록 조회는 guest에게 열려 있고, 댓글 작성/삭제와 즐겨찾기/최근 본 레시피 기능은 로그인 사용자만 사용할 수 있다.

## Feedback Routes

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/recipes/<version_id>/edit-requests` | 로그인 사용자 수정 요청 생성 |
| POST | `/api/reports` | 로그인 사용자 신고 생성 |
| GET | `/api/admin/edit-requests` | 관리자 수정 요청 목록 |
| PUT | `/api/admin/edit-requests/<request_id>/status` | 관리자 수정 요청 상태 변경 |
| GET | `/api/admin/reports` | 관리자 신고 목록 |
| PUT | `/api/admin/reports/<report_id>/status` | 관리자 신고 상태 변경 |

수정 요청과 신고 생성은 `user` controller를 사용하고, 관리자 목록/처리는 `admin` controller를 사용한다. 처리 API는 담당자, 처리 시각, 관리자 메모를 저장하고 `admin_action_log`에 변경 이력을 남긴다.

## My Page Routes

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/users/me` | 내 프로필 조회 |
| PUT | `/api/users/me` | 내 닉네임 수정 |
| GET | `/api/users/me/preferences` | 내 개인 선호도 조회 |
| PUT | `/api/users/me/preferences` | 내 개인 선호도 저장 |
| GET | `/api/users/me/activity` | 내 댓글, 수정 요청, AI 개량 요청, 즐겨찾기, 최근 본 레시피 목록 |

마이페이지 Route는 모두 `user` controller를 사용한다. 다른 사용자의 프로필/선호도/활동 내역 조회는 제공하지 않으며, AI 요청 활동은 목록 표시에 필요한 상태 중심 데이터만 반환한다.

## Public Frontend Pages

| Page App | Path | 설명 |
| --- | --- | --- |
| `page.recipe.home` | `/` | 공개 메인 화면 |
| `page.recipe.list` | `/recipes`, `/recipes/low-sodium`, `/recipes/baby-food` | 공개 레시피 검색/필터 목록, 저염/이유식 preset 전용 표시 |
| `page.recipe.detail` | `/recipes/detail/:dishId` | 공개 레시피 상세, 버전 비교, 댓글, 수정 요청 |
| `page.recipe.ai.modify` | `/ai/modify` | 로그인 사용자 AI 개량 요청 저장 |
| `page.mypage` | `/mypage` | 로그인 사용자 프로필, 활동 내역, 개인화 설정 |
| `page.dashboard` | `/dashboard` | 관리자 운영 지표와 검수 대기 현황 |
| `page.admin.recipes` | `/admin/recipes` | 관리자 레시피 등록, 수정, 상태 관리 |
| `page.admin.ai` | `/admin/ai` | 관리자 AI 결과 검수, 프롬프트, 처리 로그 관리 |
| `page.admin.sources` | `/admin/sources` | 관리자 외부 자료 출처, 수집 상태, 실패/재시도 관리 |
| `page.admin.feedback` | `/admin/feedback` | 관리자 댓글, 신고, 수정 요청 처리 관리 |
| `page.admin.logs` | `/admin/logs` | 관리자 작업, 로그인 실패, AI/크롤링 실패 로그 조회 |

상세 페이지는 목록 preset 경로와 충돌하지 않도록 `/recipes/detail/:dishId`를 사용한다.

## Frontend Constants

```typescript
import {
    USER_ROLES,
    RECIPE_STATUSES,
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
| `struct.user` | 사용자, 로그인 기록, 취향 프로필, 선호도 직렬화 |
| `struct.recipe` | 레시피 Dish/Version 생성, 수정, 공개 검색, 조회수 |
| `struct.source` | 외부 URL 수집 이력, URL 해시 중복 판별, 크롤링 상태 |
| `struct.ai` | AI 개량 결과와 처리 로그, 관리자 승인/반려 |
| `struct.comment` | 댓글, 즐겨찾기, 최근 본 레시피, 수정 요청, 신고 |
| `struct.admin_log` | 관리자 감사 로그와 before/after 마스킹 |

공개 조회는 기본적으로 `approved` 상태만 반환한다. AI 결과는 `pending_review`로 생성되며 관리자 승인 전까지 공개 데이터로 사용하지 않는다.
관리자 전체 상태 조회는 `struct.require_admin()`을 통과하는 `struct.recipe.admin_search_dishes()`와 `struct.recipe.admin_versions()`에서 처리한다.

## DB Models

| Model | Table | Purpose |
| --- | --- | --- |
| `user` | `recipe_user` | 이메일 기반 사용자와 역할/상태/잠금 정보 |
| `user_preference` | `recipe_user_preference` | 알레르기, 식단, 선호/비선호 재료, 조리 목표 |
| `recipe_dish` | `recipe_dish` | 레시피 그룹, 대표 메타데이터, 공개 상태 |
| `recipe_version` | `recipe_version` | 원본/개량 버전의 재료, 단계, 영양, 난이도 |
| `crawled_source` | `recipe_crawled_source` | 외부 출처 URL, robots 허용, 수집 상태, 중복 판정 |
| `ai_recipe_modification` | `recipe_ai_modification` | AI 레시피 개량 결과와 관리자 검토 상태 |
| `ai_processing_log` | `recipe_ai_processing_log` | AI 요청 처리 상태, 지연시간, 비용, 오류 기록 |
| `comment` | `recipe_comment` | 레시피 버전별 댓글과 상태 관리 |
| `favorite_recipe` | `recipe_favorite` | 사용자별 즐겨찾기, 동일 사용자/버전 중복 방지 |
| `recent_view` | `recipe_recent_view` | 사용자별 최근 본 레시피, 조회 횟수와 마지막 조회 시간 |
| `recipe_edit_request` | `recipe_edit_request` | 사용자 레시피 수정 제안과 검토 상태 |
| `report` | `recipe_report` | 댓글/레시피 신고와 처리 상태, 관리자 메모 |
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

## Stability Policy

- `base` controller는 세션 기준 60초 120회 요청 제한을 적용하며, 공개 Recipe REST Route도 `base` controller를 통과한다. `user`/`admin` controller는 `base`를 상속하므로 동일 제한을 받는다.
- 로그인 실패는 `struct.auth`에서 사용자별 5회 기준으로 잠금 처리하고, 성공 로그인 시 실패 횟수와 잠금 정보를 초기화한다.
- 댓글 작성은 `struct.comment`에서 같은 사용자의 연속 작성에 20초 제한을 적용한다.
- 이미지 URL이 없거나 로딩 실패한 경우 공개 홈, 목록, 상세 화면은 기본 음식 이미지를 보조 배경으로 표시한다.
- 크롤링 실패는 `struct.source.mark_failed()`에서 `failed` 상태, 실패 사유, `retry_count`, `last_checked_at`을 저장한다. 관리자 출처 관리 화면의 재시도는 상태를 `pending`으로 돌리고 재시도 횟수를 남긴다.
- 외부 링크 오류 감지 배치는 `allowed`/`collected` 출처 중 `last_checked_at`이 오래된 항목을 일정 수량으로 가져와 `HEAD` 우선, 실패 시 짧은 `GET`으로 확인한다. 2xx/3xx는 상태를 유지하고 점검 시각만 갱신하며, 4xx/5xx/timeout/DNS 오류는 `mark_failed()`로 기록해 `/admin/sources`와 `/admin/logs`에서 확인한다.
- AI 결과 재생성은 관리자 AI 화면에서 기존 개량 요청을 기준으로 새 `pending_review` 결과를 만들고 관리자 감사 로그를 남긴다.

## Security Policy

- 비밀번호는 `struct.auth`에서 `pbkdf2_sha256` + 개별 salt + 120000회 반복 해시로 저장하고, 로그인 검증은 `hmac.compare_digest()`를 사용한다.
- 인증은 세션 기반으로 처리한다. `base` controller는 내부 세션 키(`recipe_rate_limit`, `recipe_csrf_token`)를 공개 session payload에서 제거하고 `csrfToken`을 별도 제공한다.
- `layout.recipe`는 `me`/`login`/`logout` 응답의 `csrfToken`을 `window.recipeCsrfToken`에 저장하며, `wiz.call()`과 관리자 레시피 fetch 호출은 `X-CSRF-Token` 헤더를 자동 첨부한다. 서버 측 엄격 검증이 필요한 API는 `base.is_valid_csrf_token()`을 사용한다.
- 관리자 화면과 REST Route는 `admin` controller 또는 `struct.require_admin()`으로 role 검증을 수행한다. 사용자 API는 현재 세션 사용자 ID 기준으로만 마이페이지/즐겨찾기/최근 본 레시피 데이터를 반환한다.
- 댓글, 수정 요청, 신고 상세 내용은 `struct.clean_user_text()`를 통과해 제어문자와 `<script>`, `javascript:`, HTML 이벤트 속성 등 고위험 패턴을 차단한다. 화면 출력은 Angular/Pug의 기본 escaping을 유지한다.
- 외부 출처 URL, 레시피 원본 URL, 대표 이미지 URL, 썸네일 URL, 수정 요청 첨부 URL은 `struct.source.validate_url()` 정책을 사용한다. `http`/`https`만 허용하고 사용자 정보 포함 URL, localhost, 내부망/loopback/link-local/multicast/reserved IP를 차단한다.
- MVP에는 파일 업로드 endpoint가 없으며, 신규 업로드 기능을 추가할 때는 `struct.validate_upload_file()`로 `jpg`, `jpeg`, `png`, `webp`, `gif`, `pdf`와 5MB 이하 제한을 먼저 적용한다.
- 관리자 감사 로그는 `struct.mask_sensitive()`로 중첩 dict/list까지 재귀 마스킹하며 password, token, secret, rawContent, 알레르기/건강 메모 등 민감 필드를 원문 저장하지 않는다.

## AI Review Policy


## Admin AI Pipeline Routes

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/admin/ai/recipe-summary` | URL/직접 입력 텍스트를 레시피 구조 후보로 요약하고 검수 대기 Version 생성 |

레시피 요약 파이프라인은 YouTube, blog, web URL과 직접 입력 텍스트를 처리한다. 외부 URL은 `crawled_source`와 연결하고, 생성 결과는 `pending_review` 상태의 `recipe_dish`/`recipe_version`으로 저장한다.

## Engagement Policy
- AI 요약 결과는 재료/계량/조리 순서/팁 후보로 저장하고, 불확실한 항목은 `failure_prevention_tips`에 확인 필요 문구로 남긴다.

- 댓글은 기본 `visible` 상태로 생성한다.
- 댓글 작성은 로그인 사용자에게만 허용하고, 같은 사용자의 연속 작성에는 20초 기본 제한을 적용한다.
- 신고/관리자 조치 시 댓글은 `hidden` 또는 `deleted` 상태로 전환한다.
- 즐겨찾기 추가/해제는 `struct.comment.toggle_favorite()`에서 사용자와 레시피 버전 조합 기준으로 처리한다.
- 즐겨찾기는 사용자와 레시피 버전 조합이 유일해야 한다.
- 최근 본 레시피는 사용자와 레시피 버전 조합이 유일해야 하며, 재조회 시 `view_count`와 `viewed_at`을 갱신한다.
- 수정 요청 유형은 오류, 계량 문제, 출처 문제, 맛 개선 요청, 기타로 제한한다.
- 같은 사용자가 같은 대상에 중복 신고하지 않도록 `reporter_user_id`, `target_type`, `target_id` 조합을 유일하게 둔다.
- 신고 처리 시 `handled_by`, `handled_at`, `admin_memo`를 저장한다.

## Admin Audit Policy

- 관리자 주요 변경은 `admin_action_log`에 남긴다.
- `before_value`와 `after_value`에는 password, token, rawContent, allergies, medicalNotes 등 민감 정보를 원문으로 저장하지 않는다.
- 변경 이력은 화면에서 조회할 수 있도록 `action_type`, `target_type`, `target_id`, `admin_user_id`, `created_at` 기준 검색을 지원한다.

## Privacy Policy

- `SENSITIVE_PROFILE_FIELDS`에 정의된 프로필 정보는 AI 요청과 관리자 로그에 원문 저장하지 않는다.
- 알레르기/건강 메모는 레시피 개인화 계산에만 사용하고, 운영 로그에는 요약 또는 마스킹 값만 남긴다.
- 마이페이지 API는 현재 로그인 사용자 자신의 정보만 반환하고, `password_hash`, 로그인 실패 횟수, 잠금 정보는 응답하지 않는다.

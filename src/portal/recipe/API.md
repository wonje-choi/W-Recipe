# Recipe Taste Optimizer API Contract

이 문서는 Recipe Taste Optimizer 화면과 백엔드가 공유하는 요청/응답 계약이다. App API는 `wiz.call(functionName, data)`로 호출하며, HTTP REST Route는 `FormData` 또는 `URLSearchParams` 기반 form-urlencoded 요청을 사용한다.

## Common Contract

### Response Envelope

성공 응답은 WIZ `wiz.response.status(code, **data)` 형식을 따른다.

```json
{
  "code": 200,
  "data": {
    "items": [],
    "page": 1,
    "dump": 20,
    "total": 0
  }
}
```

오류 응답은 동일 envelope에 `message`를 포함한다.

```json
{
  "code": 400,
  "data": {
    "message": "요청 값을 확인해주세요."
  }
}
```

### Request Rules

- `wiz.call()`은 현재 App의 `api.py` 함수만 호출한다.
- REST Route의 JSON 객체 payload는 `data=<json string>` form field로 전달한다. 단순 field는 query/form field로도 전달할 수 있다.
- 날짜/시간 문자열은 `YYYY-MM-DD HH:MM:SS` 형식을 기본으로 한다.
- 페이지네이션은 `page`, `dump`를 사용하고, 기본 `dump=20`, 최대 `dump=100`을 따른다.
- 브라우저 App API 호출은 `X-CSRF-Token` 헤더를 자동 첨부한다.
- 필드명은 화면 편의를 위해 camelCase를 우선 문서화하며, 대부분의 REST payload는 snake_case도 함께 허용한다.

### Roles

| Role | 의미 | 대표 controller |
| --- | --- | --- |
| `guest` | 비로그인 사용자 | `base` |
| `user` | 로그인 사용자 | `user` |
| `admin` | 관리자 | `admin` |

`user`와 `admin` controller는 `base`를 상속하므로 공통 세션, rate limit, CSRF token bootstrap 정책을 함께 적용받는다.

## DTO Summary

### User

```json
{
  "id": "user_id",
  "email": "user@example.com",
  "nickname": "사용자",
  "role": "user",
  "status": "active"
}
```

### Recipe Dish

```json
{
  "id": "dish_id",
  "name": "두부조림",
  "description": "짭조름한 반찬",
  "category": "반찬",
  "tags": ["저염"],
  "thumbnailUrl": "https://example.com/image.jpg",
  "viewCount": 10,
  "status": "approved",
  "createdAt": "2026-05-01 10:00:00"
}
```

### Recipe Version

```json
{
  "id": "version_id",
  "dishId": "dish_id",
  "title": "저염 두부조림",
  "sourceType": "web",
  "sourceUrl": "https://example.com/recipe",
  "summary": "간장 양을 줄인 두부조림",
  "ingredients": [],
  "steps": [],
  "nutritionInfo": {},
  "sodiumInfo": {},
  "allergenInfo": [],
  "difficulty": "normal",
  "cookingTime": 20,
  "servingSize": "2인분",
  "status": "approved"
}
```

### AI Modification

```json
{
  "id": "modification_id",
  "recipeVersionId": "version_id",
  "purpose": "low_sodium",
  "targetUserType": "adult",
  "status": "pending_review",
  "riskFlags": [],
  "createdAt": "2026-05-01 10:00:00"
}
```

### Comment / Feedback

```json
{
  "id": "comment_id",
  "recipeVersionId": "version_id",
  "userId": "user_id",
  "content": "맛있어요.",
  "status": "visible",
  "reportCount": 0,
  "createdAt": "2026-05-01 10:00:00"
}
```

## Auth APIs

App: `layout.recipe/api.py`  
Controller: `base`

| Function | Method | Role | Request | Response |
| --- | --- | --- | --- | --- |
| `wiz.call("me")` | POST | guest | `{}` | `{ user, csrfToken }`; 비로그인 시 `user=null` |
| `wiz.call("login")` | POST | guest | `{ email, password }` | `{ user, csrfToken }` |
| `wiz.call("logout")` | POST | guest | `{}` | `{ csrfToken }` |

로그인 실패는 5회 기준으로 잠금 처리되며, 성공 로그인 시 실패 횟수와 잠금 정보가 초기화된다.

## User / Mypage APIs

### App APIs

App: `page.mypage/api.py`  
Controller: `user`

| Function | Method | Role | Request | Response |
| --- | --- | --- | --- | --- |
| `load` | POST | user | `{}` | `{ profile, preference, activity, options }` |
| `save_profile` | POST | user | `{ nickname }` | `{ profile }` |
| `save_preference` | POST | user | preference fields | `{ preference }` |

### REST APIs

| Method | Path | Role | Request | Response |
| --- | --- | --- | --- | --- |
| GET | `/api/users/me` | user | none | `{ profile }` |
| PUT/POST | `/api/users/me` | user | `data={ nickname }` | `{ profile }` |
| GET | `/api/users/me/preferences` | user | none | `{ preference }` |
| PUT/POST | `/api/users/me/preferences` | user | `data={ allergies, preferredDietTypes, sodiumPreference, ... }` | `{ preference }` |
| GET | `/api/users/me/activity` | user | `page`, `dump` | `{ comments, favorites, editRequests, aiModifications }` |
| GET | `/api/users/me/recent-views` | user | `page`, `dump` | `{ items, page, dump, total }` |

마이페이지 API는 현재 세션 사용자 자신의 데이터만 반환하며 `password_hash`, 로그인 실패 횟수, 잠금 정보는 응답하지 않는다.

## Public Recipe APIs

### REST APIs

| Method | Path | Role | Request | Response |
| --- | --- | --- | --- | --- |
| GET | `/api/recipes` | guest | `page`, `dump`, `text`, `category`, `tag`, `sort` | `{ items, page, dump, total, empty }` |
| GET | `/api/recipes/<dish_id>` | guest | none | `{ dish, version, versions }` |
| GET | `/api/recipes/<dish_id>/versions` | guest | `page`, `dump` | `{ items, page, dump, total }` |
| GET | `/api/recipes/<dish_id>/versions/<version_id>` | guest | none | `{ dish, version }` |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/source` | guest | none | `{ source }` |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/compare` | guest | `targetVersionId` | `{ baseVersion, targetVersion, comparison }` |
| POST | `/api/recipes/<dish_id>/views` | guest | none | `{ counted, viewCount }` |
| POST | `/api/recipes/<dish_id>/versions/<version_id>/views` | guest | none | `{ counted, viewCount }` |

공개 API는 `approved` 상태만 반환한다.

### Page App APIs

| App | Function | Role | Request | Response |
| --- | --- | --- | --- | --- |
| `page.recipe.home` | `load` | guest | `{}` | `{ popular, latest, randomItems, totals, keywords }` |
| `page.recipe.list` | `search` | guest | `{ page, dump, text, preset, category, tag, sort, babyStage }` | `{ items, filters, categories, tags, sorts, lowSodium, babyFood, page, dump, total }` |
| `page.recipe.detail` | `load` | guest | `{ dishId, versionId }` | `{ dish, version, versions, source, comparison, favorite, canComment }` |
| `page.recipe.detail` | `comments` | guest | `{ versionId, page, dump }` | `{ items, page, dump, total }` |
| `page.recipe.detail` | `create_comment` | user | `{ versionId, content }` | `{ comment }` |
| `page.recipe.detail` | `create_edit_request` | user | `{ versionId, requestType, content, attachmentUrl }` | `{ editRequest }` |

## Admin Recipe APIs

### REST APIs

Controller: `admin`

| Method | Path | Role | Request | Response |
| --- | --- | --- | --- | --- |
| GET | `/api/admin/recipes` | admin | `page`, `dump`, `text`, `category`, `tag`, `status`, `sort` | `{ items, page, dump, total, empty }` |
| POST | `/api/admin/recipes` | admin | `data={ name, description, category, tags, thumbnailUrl }` | `{ dish }` |
| GET | `/api/admin/recipes/<dish_id>` | admin | none | `{ dish, versions }` |
| PUT | `/api/admin/recipes/<dish_id>` | admin | `data={ name, description, category, tags, thumbnailUrl, status }` | `{ dish }` |
| DELETE | `/api/admin/recipes/<dish_id>` | admin | none | `{ dish }` hidden 처리 |
| GET | `/api/admin/recipes/<dish_id>/versions` | admin | `page`, `dump` | `{ items, page, dump, total }` |
| POST | `/api/admin/recipes/<dish_id>/versions` | admin | `data={ title, sourceType, sourceUrl, summary, ingredients, steps, ... }` | `{ version }` |
| GET | `/api/admin/recipes/<dish_id>/versions/<version_id>` | admin | none | `{ dish, version }` |
| PUT | `/api/admin/recipes/<dish_id>/versions/<version_id>` | admin | version fields | `{ version }` |
| DELETE | `/api/admin/recipes/<dish_id>/versions/<version_id>` | admin | none | `{ version }` hidden 처리 |

### Page App APIs

App: `page.admin.recipes/api.py` exposes `options()` for category, tag, status, source type, difficulty and sorting option metadata. The page uses the REST APIs above for CRUD.

## Admin Review APIs

Controller: `admin`

| Method | Path | Role | Request | Response |
| --- | --- | --- | --- | --- |
| GET | `/api/admin/reviews/pending` | admin | `page`, `dump` | `{ dishes, versions, aiModifications, counts }` |
| POST | `/api/admin/reviews/<target_type>/<target_id>/approve` | admin | `data={ reason }` | `{ target }` |
| POST | `/api/admin/reviews/<target_type>/<target_id>/reject` | admin | `data={ reason }` | `{ target }` |

`target_type`은 `recipe_dish`, `recipe_version`, `ai_modification` 중 하나다.

## AI APIs

### User AI Modification

| Method/Function | Role | Request | Response |
| --- | --- | --- | --- |
| `page.recipe.ai.modify.load` | guest | `{ text }` | `{ user, recipeOptions, total, purposes, targetUserTypes, policy }` |
| `page.recipe.ai.modify.search_recipes` | guest | `{ text }` | `{ recipeOptions, total }` |
| `page.recipe.ai.modify.submit` | user | `{ recipeVersionId, purpose, targetUserType, tasteDirection, additionalRequest, excludedIngredients, allergies, desiredCookingTime, babyAgeMonth, sodiumPreference, texturePreference, promptVersion }` | `{ modification, log, version }` |
| POST `/api/ai/recipe-modifications` | user | same fields | `{ modification, log, version }` |

AI modification results are created as `pending_review` and are not public until admin review.

### Admin AI

| Method/Function | Role | Request | Response |
| --- | --- | --- | --- |
| POST `/api/admin/ai/recipe-summary` | admin | `data={ sourceUrl, sourceType, inputText, promptVersion }` | `{ dish, version, source, log }` |
| GET `/api/admin/ai/prompts` | admin | `page`, `dump`, `promptKey`, `active` | `{ items, page, dump, total }` |
| POST `/api/admin/ai/prompts` | admin | `data={ promptKey, version, title, template, active }` | `{ prompt }` |
| GET `/api/admin/ai/prompts/<prompt_id>` | admin | none | `{ prompt }` |
| PUT `/api/admin/ai/prompts/<prompt_id>` | admin | prompt fields | `{ prompt }` |
| DELETE `/api/admin/ai/prompts/<prompt_id>` | admin | none | `{ prompt }` inactive |
| PUT `/api/admin/ai/prompts/<prompt_id>/activate` | admin | none | `{ prompt }` |
| PUT `/api/admin/ai/prompts/<prompt_id>/deactivate` | admin | none | `{ prompt }` |
| `page.admin.ai.options` | admin | `{}` | option metadata |
| `page.admin.ai.reviews` | admin | `{ page, dump, status, purpose, text }` | `{ items, page, dump, total, summary }` |
| `page.admin.ai.review_action` | admin | `{ id, action, reason }` | `{ review }` |
| `page.admin.ai.regenerate` | admin | `{ modificationId }` | `{ review }` |
| `page.admin.ai.prompts` | admin | filter fields | `{ items, page, dump, total }` |
| `page.admin.ai.save_prompt` | admin | prompt fields | `{ prompt }` |
| `page.admin.ai.prompt_action` | admin | `{ id, action }` | `{ prompt }` |
| `page.admin.ai.logs` | admin | `{ page, dump, status, promptKey, text }` | `{ items, page, dump, total, tokenTotal, costTotal }` |

## Comment / Favorite / Feedback APIs

| Method | Path | Role | Request | Response |
| --- | --- | --- | --- | --- |
| GET | `/api/recipes/<version_id>/comments` | guest | `page`, `dump` | `{ items, page, dump, total, empty }` |
| POST | `/api/recipes/<version_id>/comments` | user | `data={ content }` | `{ comment }` |
| DELETE | `/api/comments/<comment_id>` | owner/admin | none | `{ comment }` |
| GET | `/api/recipes/<version_id>/favorite` | user | none | `{ favorited, id }` |
| POST | `/api/recipes/<version_id>/favorite` | user | none | `{ favorited, id }` |
| DELETE | `/api/recipes/<version_id>/favorite` | user | none | `{ favorited:false }` |
| POST | `/api/recipes/<version_id>/edit-requests` | user | `data={ requestType, content, attachmentUrl }` | `{ editRequest }` |
| POST | `/api/reports` | user | `data={ targetType, targetId, reason, detail }` | `{ report }` |

Input safety rules:

- `content` and `detail` are length-checked and passed through `struct.clean_user_text()`.
- `attachmentUrl` must pass the external URL policy.
- duplicate open edit requests and duplicate reports are collapsed to the existing item ID.

## Admin Feedback APIs

| Method/Function | Role | Request | Response |
| --- | --- | --- | --- |
| GET `/api/admin/edit-requests` | admin | `page`, `dump`, `status`, `userId` | `{ items, page, dump, total }` |
| PUT `/api/admin/edit-requests/<request_id>/status` | admin | `data={ status, adminMemo }` | `{ editRequest }` |
| GET `/api/admin/reports` | admin | `page`, `dump`, `status`, `targetType` | `{ items, page, dump, total }` |
| PUT `/api/admin/reports/<report_id>/status` | admin | `data={ status, adminMemo }` | `{ report }` |
| `page.admin.feedback.options` | admin | `{}` | `{ statuses, requestTypes, reportReasons, summary }` |
| `page.admin.feedback.comments` | admin | filter fields | `{ items, page, dump, total }` |
| `page.admin.feedback.reports` | admin | filter fields | `{ items, page, dump, total }` |
| `page.admin.feedback.edit_requests` | admin | filter fields | `{ items, page, dump, total }` |
| `page.admin.feedback.comment_action` | admin | `{ id, action, reason }` | `{ comment }` |
| `page.admin.feedback.report_action` | admin | `{ id, status, adminMemo }` | `{ report }` |
| `page.admin.feedback.edit_request_action` | admin | `{ id, status, adminMemo }` | `{ editRequest }` |
| `page.admin.feedback.user_action` | admin | `{ userId, status }` | `{ user }` |

## Crawled Source APIs

| Method/Function | Role | Request | Response |
| --- | --- | --- | --- |
| GET `/api/admin/sources` | admin | `page`, `dump`, `status`, `sourceType` | `{ items, page, dump, total, empty }` |
| POST `/api/admin/sources` | admin | `data={ sourceUrl, sourceType, title, author, thumbnailUrl, robotsAllowed }` | `{ source }` |
| GET `/api/admin/sources/<source_id>` | admin | none | `{ source }` |
| PUT `/api/admin/sources/<source_id>` | admin | source fields | `{ source }` |
| DELETE `/api/admin/sources/<source_id>` | admin | none | `{ source }` expired |
| PUT `/api/admin/sources/<source_id>/status` | admin | `data={ crawlStatus, robotsAllowed, errorMessage }` | `{ source }` |
| `page.admin.sources.options` | admin | `{}` | `{ sourceTypes, crawlStatuses }` |
| `page.admin.sources.sources` | admin | filter fields | `{ items, page, dump, total, statusSummary }` |
| `page.admin.sources.save_source` | admin | source fields | `{ source }` |
| `page.admin.sources.status_action` | admin | `{ id, crawlStatus, robotsAllowed, errorMessage }` | `{ source }` |
| `page.admin.sources.retry_source` | admin | `{ id }` | `{ source }` |
| `page.admin.sources.expire_source` | admin | `{ id }` | `{ source }` |

Crawling statuses: `pending`, `allowed`, `blocked`, `collected`, `summarized`, `failed`, `expired`.

## Admin Logs / Dashboard APIs

| Function | Role | Request | Response |
| --- | --- | --- | --- |
| `page.admin.logs.options` | admin | `{}` | `{ types, severities, summary }` |
| `page.admin.logs.logs` | admin | `{ page, dump, type, severity, actor, text, dateFrom, dateTo }` | `{ items, page, dump, total, summary }` |
| `page.dashboard.overview` | admin | `{}` | `{ metrics, reviewQueue, operations }` |

`page.dashboard.overview.operations` includes daily activity (`visitors`, `recipeViews`, `signups`, `comments`, `reports`, `aiRequests`), recipe view totals (`totalRecipeViews`, `lowSodiumViews`, `babyFoodViews`, `popularRecipes`), review counts, approval/rejection ratio, AI request/failure/token/cost totals, crawling source failure rate, recent sources, and failed AI logs. Daily visitor and recipe view values are based on logged-in `recent_view` activity in the current MVP.

Admin log entries mask sensitive keys recursively and expose summarized events for admin actions, login failures, AI failures, crawling failures, API errors, and permission errors.

## Required Examples

### Login

```typescript
const { code, data } = await wiz.call('login', {
  email: 'admin@example.com',
  password: 'secret'
});
```

```json
{
  "code": 200,
  "data": {
    "user": { "id": "u1", "email": "admin@example.com", "role": "admin", "status": "active" },
    "csrfToken": "token"
  }
}
```

### Public Recipe Search

```bash
curl -s "http://localhost:3000/api/recipes?page=1&dump=12&text=두부&sort=popular"
```

```json
{
  "code": 200,
  "data": {
    "items": [],
    "page": 1,
    "dump": 12,
    "total": 0,
    "empty": true
  }
}
```

### Admin Recipe Create

```bash
curl -s -X POST \
  -H "X-CSRF-Token: token" \
  -d 'data={"name":"두부조림","category":"반찬","tags":["저염"]}' \
  "http://localhost:3000/api/admin/recipes"
```

```json
{
  "code": 201,
  "data": {
    "dish": { "id": "dish_id", "name": "두부조림", "status": "draft" }
  }
}
```

### AI Modification Submit

```typescript
await wiz.call('submit', {
  recipeVersionId: 'version_id',
  purpose: 'low_sodium',
  targetUserType: 'adult',
  sodiumPreference: 'low',
  additionalRequest: '간장을 줄여주세요.'
});
```

```json
{
  "code": 200,
  "data": {
    "modification": { "id": "modification_id", "status": "pending_review" },
    "log": { "status": "completed" },
    "version": { "id": "version_id" }
  }
}
```

### Comment Create

```typescript
await wiz.call('create_comment', {
  versionId: 'version_id',
  content: '아이도 잘 먹었어요.'
});
```

```json
{
  "code": 201,
  "data": {
    "comment": { "id": "comment_id", "status": "visible" }
  }
}
```

## Status Values

| Group | Values |
| --- | --- |
| User role | `guest`, `user`, `admin` |
| User status | `active`, `suspended`, `deleted`, `pending` |
| Recipe status | `draft`, `crawled`, `ai_parsed`, `ai_modified`, `pending_review`, `approved`, `rejected`, `hidden` |
| AI status | `queued`, `processing`, `pending_review`, `approved`, `rejected`, `failed` |
| AI processing status | `queued`, `processing`, `completed`, `failed` |
| Source type | `youtube`, `blog`, `web`, `direct`, `ai_modified` |
| Crawling status | `pending`, `allowed`, `blocked`, `collected`, `summarized`, `failed`, `expired` |
| Comment status | `visible`, `hidden`, `deleted`, `reported` |
| Edit request status | `open`, `in_review`, `resolved`, `rejected` |
| Report status | `open`, `in_review`, `actioned`, `rejected` |

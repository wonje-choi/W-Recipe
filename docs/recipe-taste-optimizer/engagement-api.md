# 사용자 참여 API

Recipe Taste Optimizer의 댓글, 즐겨찾기, 최근 본 레시피 API이다. 공개 댓글 조회는 guest에게 열려 있고, 쓰기 요청은 로그인된 `user` 이상만 사용할 수 있다.

## 댓글

### 목록 조회

```http
GET /api/recipes/{version_id}/comments?page=1&dump=20
```

응답:

```json
{
  "comments": [
    {
      "id": "comment_id",
      "recipeVersionId": "version_id",
      "userId": "user_id",
      "content": "맛있게 만들었어요.",
      "status": "visible",
      "reportCount": 0,
      "createdAt": "2026-05-01 12:00:00",
      "updatedAt": "2026-05-01 12:00:00"
    }
  ],
  "page": 1,
  "dump": 20,
  "total": 1,
  "empty": false
}
```

- `approved` 상태의 공개 레시피 버전 댓글만 조회된다.
- 조회는 로그인 없이 가능하다.

### 작성

```http
POST /api/recipes/{version_id}/comments
```

Form payload:

```json
{
  "data": "{\"content\":\"댓글 내용\"}"
}
```

- 로그인이 필요하다.
- 댓글은 2자 이상 1000자 이하로 제한한다.
- 같은 사용자가 댓글을 연속 작성할 때 20초 기본 제한을 적용한다.

### 삭제 요청

```http
DELETE /api/comments/{comment_id}
```

- 로그인이 필요하다.
- 댓글 작성자 또는 admin만 삭제할 수 있다.
- 물리 삭제하지 않고 `deleted` 상태로 변경한다.

## 즐겨찾기

```http
GET /api/recipes/{version_id}/favorite
POST /api/recipes/{version_id}/favorite
DELETE /api/recipes/{version_id}/favorite
```

- 모두 로그인이 필요하다.
- `GET`은 현재 사용자의 즐겨찾기 여부를 반환한다.
- `POST`는 토글 방식으로 즐겨찾기를 추가하거나 해제한다.
- `DELETE`는 명시적으로 즐겨찾기를 해제한다.
- 공개 레시피 버전에만 적용된다.

## 최근 본 레시피

### 목록

```http
GET /api/users/me/recent-views?page=1&dump=20
```

응답:

```json
{
  "items": [
    {
      "id": "recent_id",
      "recipeVersionId": "version_id",
      "viewCount": 3,
      "viewedAt": "2026-05-01 12:00:00",
      "version": {
        "id": "version_id",
        "dishId": "dish_id",
        "title": "저염 된장국",
        "summary": "나트륨을 줄인 된장국",
        "sourceType": "ai_modified",
        "status": "approved",
        "aiModified": true,
        "createdAt": "2026-05-01 11:00:00",
        "updatedAt": "2026-05-01 11:00:00"
      }
    }
  ],
  "page": 1,
  "dump": 20,
  "total": 1,
  "empty": false
}
```

### 저장

```http
POST /api/users/me/recent-views
```

Form payload:

```json
{
  "data": "{\"recipeVersionId\":\"version_id\"}"
}
```

- 로그인이 필요하다.
- 동일 사용자와 레시피 버전 조합은 하나만 유지하며, 재조회 시 `viewCount`와 `viewedAt`을 갱신한다.
- 공개 레시피 버전에만 저장된다.

## 데이터 모델

- `recipe_comment`: 댓글. 삭제는 `deleted` 상태 변경으로 처리한다.
- `recipe_favorite`: 사용자별 즐겨찾기. `(user_id, recipe_version_id)` 유니크 제약이 있다.
- `recipe_recent_view`: 사용자별 최근 본 레시피. `(user_id, recipe_version_id)` 유니크 제약이 있고 조회 횟수와 마지막 조회 시간을 기록한다.

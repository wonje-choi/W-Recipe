# 마이페이지와 개인 선호도 API

로그인 사용자가 자신의 프로필, 개인 선호도, 활동 내역을 조회하는 API이다. 모든 API는 `user` controller를 사용하며, 다른 사용자의 민감 정보나 활동 내역은 조회하지 않는다.

## 내 프로필

```http
GET /api/users/me
PUT /api/users/me
```

`GET` 응답:

```json
{
  "profile": {
    "id": "user_id",
    "email": "user@example.com",
    "nickname": "요리초보",
    "role": "user",
    "status": "active",
    "lastLoginAt": "2026-05-01 12:00:00",
    "createdAt": "2026-05-01 10:00:00",
    "updatedAt": "2026-05-01 12:00:00"
  }
}
```

`PUT`은 현재 MVP에서 `nickname`만 수정한다. 이메일, role, status, 로그인 실패 횟수, 잠금 정보, 비밀번호 해시는 응답하거나 수정하지 않는다.

## 내 선호도

```http
GET /api/users/me/preferences
PUT /api/users/me/preferences
```

Form payload:

```json
{
  "data": "{\"preferredDietTypes\":[\"low_sodium\"],\"allergies\":[\"peanut\"],\"dislikedIngredients\":[\"cilantro\"],\"preferredCookingTime\":30,\"cookingTools\":[\"air_fryer\"],\"babyAgeMonth\":12,\"sodiumPreference\":\"low\",\"texturePreference\":\"soft\"}"
}
```

응답:

```json
{
  "preference": {
    "preferredDietTypes": ["low_sodium"],
    "allergies": ["peanut"],
    "dislikedIngredients": ["cilantro"],
    "preferredCookingTime": 30,
    "cookingTools": ["air_fryer"],
    "babyAgeMonth": 12,
    "sodiumPreference": "low",
    "texturePreference": "soft"
  }
}
```

- 배열 필드는 JSON 문자열로 저장하고 응답 시 배열로 복원한다.
- 선호도는 로그인 사용자 자신의 레코드만 조회/수정한다.

## 내 활동 내역

```http
GET /api/users/me/activity?page=1&dump=10
```

응답 그룹:

| 필드 | 설명 |
| --- | --- |
| `comments` | 내가 작성한 댓글 목록 |
| `editRequests` | 내가 생성한 수정 요청 목록 |
| `aiModifications` | 내가 요청한 AI 개량 요청 목록 |
| `favorites` | 내가 저장한 즐겨찾기 목록 |
| `recentViews` | 내가 최근 본 레시피 목록 |

AI 개량 요청 활동은 `purpose`, `targetUserType`, `status`, `riskFlags` 등 목록 표시에 필요한 값만 반환한다. 원문 요청 상세, 알레르기/건강 메모, 비선호 재료 같은 민감 입력 원문은 활동 목록에 노출하지 않는다.

## 개인정보 범위

- `password_hash`, `login_failed_count`, `locked_until`은 응답하지 않는다.
- 관리자도 이 API로 다른 사용자의 프로필이나 선호도를 조회할 수 없다.
- 개인 선호도는 자기 계정에서만 조회/수정 가능하다.
- 관리자 감사 로그에는 `struct.mask_sensitive()` 정책을 계속 적용한다.

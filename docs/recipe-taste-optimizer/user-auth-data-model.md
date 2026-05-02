# Recipe Taste Optimizer User and Auth Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0004
- **목적**: 사용자 계정, 권한, 로그인 실패 제한, 개인 선호도 저장 기반을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 |
|---|---|---|
| User | `src/portal/recipe/model/db/user.py` | `recipe_user` |
| UserPreference | `src/portal/recipe/model/db/user_preference.py` | `recipe_user_preference` |

DB 필드는 Python/WIZ 관례에 맞춰 snake_case로 저장한다. API 응답 또는 프론트엔드 DTO에서는 필요 시 camelCase로 변환한다.

## 2. User 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 사용자 ID, primary key |
| `email` | `email` | Char(190) | 로그인 이메일, unique |
| `passwordHash` | `password_hash` | Char(255) | 해시된 비밀번호 |
| `nickname` | `nickname` | Char(64) | 화면 표시 이름 |
| `role` | `role` | Char(16) | `guest`, `user`, `admin` 중 로그인 계정은 `user` 이상 |
| `status` | `status` | Char(16) | `active`, `suspended`, `deleted`, `pending` |
| `loginFailedCount` | `login_failed_count` | Integer | 로그인 실패 횟수 |
| `lastLoginAt` | `last_login_at` | DateTime nullable | 마지막 로그인 시각 |
| `lockedUntil` | `locked_until` | DateTime nullable | 로그인 실패 제한 잠금 만료 시각 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 3. UserPreference 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 선호도 ID, primary key |
| `userId` | `user_id` | Char(32) | 사용자 ID, unique |
| `preferredDietTypes` | `preferred_diet_types` | Text(JSON array) | 선호 식단: 저염, 이유식, 다이어트 등 |
| `allergies` | `allergies` | Text(JSON array) | 알레르기 재료 |
| `dislikedIngredients` | `disliked_ingredients` | Text(JSON array) | 선호하지 않는 재료 |
| `preferredCookingTime` | `preferred_cooking_time` | Integer | 선호 조리 시간, 분 단위. 0은 미설정 |
| `cookingTools` | `cooking_tools` | Text(JSON array) | 보유 조리도구 |
| `babyAgeMonth` | `baby_age_month` | Integer nullable | 아이 월령. 미설정 가능 |
| `sodiumPreference` | `sodium_preference` | Char(32) | 나트륨 선호 수준 |
| `texturePreference` | `texture_preference` | Char(32) | 식감 선호 수준 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 4. 비밀번호 저장 정책

- 비밀번호 원문은 저장하지 않는다.
- `password_hash`에는 bcrypt, argon2id 등 검증된 단방향 해시 결과만 저장한다.
- 프론트엔드에서 SHA256을 적용하더라도 서버 저장 시에는 별도 salt가 포함된 비밀번호 해시를 사용한다.
- 로그인 실패 횟수는 `login_failed_count`에 기록한다.
- 실패 횟수 임계치 초과 시 `locked_until`을 설정해 일정 시간 로그인을 제한한다.
- 로그인 성공 시 `login_failed_count`를 0으로 초기화하고 `last_login_at`을 갱신한다.

## 5. 민감 정보 보호 정책

다음 필드는 개인화와 안전 표시 목적으로만 사용한다.

- `allergies`
- `baby_age_month`
- `disliked_ingredients`
- `preferred_diet_types`
- `sodium_preference`
- `texture_preference`

운영/오류/AI 로그에는 위 값을 원문으로 저장하지 않는다. 필요한 경우 `설정됨/미설정`, 개수, 마스킹된 요약만 저장한다.

관리자 화면에서도 불필요한 민감 정보는 기본적으로 숨기고, 사용자 지원이나 안전 검수에 필요한 범위에서만 제한적으로 표시한다.

## 6. 완료 판정

이 문서는 FN-20260501-0004의 완료 기준을 충족한다.

- User 모델을 정의했다.
- UserPreference 모델을 정의했다.
- 비밀번호 해시 저장 정책과 로그인 실패 기록 필드를 설계했다.
- 민감 정보 로그 저장 금지 원칙을 문서화했다.

# AI Special Diet Modification API

`POST /api/ai/recipe-modifications`는 로그인 사용자 또는 관리자가 기존 공개 레시피 버전을 특수식단 목적에 맞게 개량 요청하는 API다. 결과는 즉시 공개하지 않고 `ai_recipe_modification`에 `pending_review` 상태로 저장한다.

## Endpoint

| Method | Path | Controller | 설명 |
| --- | --- | --- | --- |
| POST | `/api/ai/recipe-modifications` | `user` | 특수식단 개량안 생성 |

관리자도 로그인 세션이 있으면 같은 API를 사용할 수 있다. 일반 사용자는 `approved` 버전만 개량 요청할 수 있고, 관리자는 전체 상태 버전을 대상으로 요청할 수 있다.

## Payload

```json
{
  "recipeVersionId": "version_id",
  "purpose": "low_sodium",
  "targetUserType": "hypertension_care",
  "excludedIngredients": ["고수"],
  "allergies": ["새우", "대두"],
  "desiredCookingTime": 20,
  "tasteDirection": "감칠맛은 유지하고 짠맛은 줄이기",
  "babyAgeMonth": 10,
  "promptVersion": "low_sodium:v1"
}
```

## Supported Purpose Values

| Value | 처리 방향 |
| --- | --- |
| `tastier` | 맛/식감 개선 중심 |
| `low_sodium` | 고나트륨 재료 감소와 풍미 보완 |
| `baby_food` | 월령, 입자 크기, 소금/설탕 제한, 보관 방법 중심 |
| `diet` | 채소 비중, 기름 사용량, 과도한 열량 표현 제한 |
| `high_protein` | 단백질 재료 보강 |
| `shorter_time` | 조리 단계 단순화 |
| `simpler_ingredients` | 재료 수 축소 |
| `softer_texture` | 부드러운 식감 조정 |

## Processing Rules

1. `recipeVersionId`의 원본 재료와 조리 단계를 읽는다.
2. 일반 사용자는 공개 승인된 Version만 요청할 수 있다.
3. 제외 재료는 개량안에서 제거한다.
4. 알레르기 후보가 원본에 포함되면 `allergenWarnings`와 `riskFlags`에 표시한다.
5. 저염식은 소금, 간장, 된장, 고추장, 액젓 등 고나트륨 재료를 줄이고 대체 풍미 근거를 생성한다.
6. 이유식은 월령, 입자 크기, 소금/설탕 제한, 보관 주의사항을 `babyFoodSafetyNotes`에 저장한다.
7. 다이어트식은 기름 사용량과 채소 비중 조정, 극단적 열량 제한 금지 문구를 남긴다.
8. 결과는 `ai_recipe_modification.status = pending_review`로 저장한다.
9. AIProcessingLog는 요청 조건 요약, promptVersion, 생성된 modification id를 기록한다.

## Response

```json
{
  "version": { "id": "version_id", "status": "approved" },
  "modification": {
    "id": "modification_id",
    "recipeVersionId": "version_id",
    "purpose": "low_sodium",
    "modifiedIngredients": ["간장 1큰술 - 양을 30~50% 줄이고 향채/식초/육수로 보완"],
    "modifiedSteps": ["재료를 손질한 뒤 목적에 맞게 간을 조절하고 충분히 익힌다"],
    "sodiumReductionPoint": "고나트륨 양념을 줄이고 향채, 식초, 육수, 감칠맛 재료로 풍미를 보완한다.",
    "riskFlags": ["allergy_review_required"],
    "status": "pending_review"
  },
  "log": {
    "requestType": "low_sodium",
    "targetId": "modification_id",
    "promptVersion": "low_sodium:heuristic-v1",
    "status": "completed"
  }
}
```

## Prompt Fallback

`promptVersion`이 없으면 목적에 따라 활성 프롬프트를 찾는다.

| Purpose | Prompt Key |
| --- | --- |
| `low_sodium` | `low_sodium` |
| `baby_food` | `baby_food` |
| 기타 목적 | `taste_improvement` |

활성 프롬프트가 없으면 관리자 세션에서는 MVP용 내장 `{promptKey}:heuristic-v1` 프롬프트를 생성해 사용한다. 일반 사용자 세션에서는 프롬프트 자동 생성을 하지 않고 관리자 설정이 필요하다는 오류를 반환한다.

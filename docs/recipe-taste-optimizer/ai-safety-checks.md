# AI Safety Checks

AI 안전성 체크는 공개 전 관리자 검수 단계에서 위험 후보를 표시하기 위한 규칙 기반 로직이다. `struct.safety`가 레시피 Version과 AI Modification 텍스트를 분석하고, 관리자 검수 API는 각 항목에 `safety`와 `riskFlags`를 포함한다.

## Checked Risks

| Risk Flag | Severity | 설명 |
| --- | --- | --- |
| `allergen_candidate` | warning | 대두, 달걀, 우유, 밀, 땅콩, 견과류, 갑각류 등 알레르기 후보 |
| `high_sodium_candidate` | warning | 소금, 간장, 된장, 고추장, 액젓, 가공육 등 나트륨 과다 가능 재료 |
| `baby_food_unsuitable` | danger | 꿀, 견과류, 고추, 소금/설탕 등 이유식 부적합 후보 |
| `raw_food_risk` | danger | 생식, 덜 익은 재료, 회, 생달걀 등 영유아/취약 사용자 위험 후보 |
| `choking_risk` | danger | 통째, 딱딱함, 큰 덩어리, 끈적임 등 질식 위험 후보 |
| `medical_claim` | danger | 치료, 완치, 예방, 질병 개선 보장처럼 보일 수 있는 표현 |

## Struct API

```python
safety = struct.safety.check_version(version)
safety = struct.safety.check_modification(ai_modification)
```

반환 형식:

```json
{
  "hasRisk": true,
  "riskFlags": ["allergen_candidate"],
  "issues": [
    {
      "type": "allergen_candidate",
      "severity": "warning",
      "message": "알레르기 유발 가능 재료가 포함되어 있습니다.",
      "matched": ["대두"]
    }
  ],
  "summary": "위험 요소 확인 필요"
}
```

## Admin Review API Integration

`GET /api/admin/reviews/pending`의 `versions`와 `aiModifications` 항목은 다음 필드를 포함한다.

```json
{
  "riskFlags": ["high_sodium_candidate"],
  "safety": {
    "hasRisk": true,
    "summary": "위험 요소 확인 필요",
    "issues": []
  }
}
```

Dish 단독 검수 항목은 재료/단계 정보가 없으므로 빈 safety 결과를 반환한다.

## AI Modification Persistence

`struct.ai_diet`는 특수식단 개량 결과 생성 시 `struct.safety.check_text()`를 실행해 주요 위험 플래그를 `ai_recipe_modification.risk_flags`에 함께 저장한다. 관리자 검수 API는 저장된 `risk_flags`와 실시간 안전성 체크 결과를 병합해 반환한다.

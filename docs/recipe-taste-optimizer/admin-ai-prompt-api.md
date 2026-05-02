# Admin AI Prompt API

Recipe Taste Optimizer의 AI 프롬프트 템플릿은 관리자만 생성, 수정, 활성화, 비활성화할 수 있다. 모든 프롬프트는 `promptKey`와 `version` 조합으로 `promptVersion`을 생성하며, AI 처리 로그는 이 값을 `prompt_version`에 저장한다.

## Prompt Types

| Key | 용도 |
| --- | --- |
| `recipe_summary` | 외부 자료를 레시피 구조로 요약 |
| `low_sodium` | 저염식 개량 |
| `baby_food` | 이유식 개량 |
| `taste_improvement` | 맛 개선/식감 개선 |
| `review_summary` | 관리자 검수 요약 |

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/ai/prompts` | 프롬프트 목록 조회 |
| POST | `/api/admin/ai/prompts` | 프롬프트 버전 생성 |
| GET | `/api/admin/ai/prompts/<prompt_id>` | 프롬프트 상세 조회 |
| PUT | `/api/admin/ai/prompts/<prompt_id>` | 프롬프트 메타데이터/본문 수정 |
| DELETE | `/api/admin/ai/prompts/<prompt_id>` | 프롬프트 비활성화 |
| PUT | `/api/admin/ai/prompts/<prompt_id>/activate` | 해당 버전을 활성화하고 같은 promptKey의 기존 활성 버전을 비활성화 |
| PUT | `/api/admin/ai/prompts/<prompt_id>/deactivate` | 해당 버전을 비활성화 |

## Create Payload

```json
{
  "promptKey": "recipe_summary",
  "version": "v1",
  "title": "레시피 요약 기본 프롬프트",
  "description": "외부 자료에서 재료/단계/팁 후보를 추출한다.",
  "template": "...",
  "inputSchema": { "sourceType": "string", "summary": "string" },
  "outputSchema": { "ingredients": "array", "steps": "array" },
  "modelHint": "general",
  "isActive": true,
  "changeReason": "초기 등록"
}
```

- `promptKey`는 `AI_PROMPT_TYPES` 값 중 하나여야 한다.
- `version`은 같은 `promptKey` 안에서 중복될 수 없다.
- `promptVersion`은 `{promptKey}:{version}` 형식으로 자동 생성된다.
- `isActive=true`로 생성하거나 활성화하면 같은 `promptKey`의 기존 활성 버전은 자동 비활성화된다.

## AIProcessingLog 연결

`struct.ai.create_log()`는 다음 규칙으로 `prompt_version`을 채운다.

1. `prompt_version`이 명시되면 등록된 프롬프트 버전인지 검증한다.
2. `prompt_key`가 전달되고 `prompt_version`이 비어 있으면 해당 `promptKey`의 활성 버전을 찾아 `prompt_version`에 저장한다.
3. 둘 다 없으면 기존처럼 프롬프트 버전 없이 로그를 생성할 수 있다.

```python
struct.ai.create_log({
    "request_type": "recipe_summary",
    "target_id": source_id,
    "prompt_key": "recipe_summary",
    "input_summary": "source summary only",
})
```

## Audit Policy

프롬프트 생성, 수정, 활성화, 비활성화는 `admin_action_log`에 기록한다.

| Action Type | 설명 |
| --- | --- |
| `ai_prompt_create` | 새 프롬프트 버전 생성 |
| `ai_prompt_update` | 프롬프트 메타데이터/본문 수정 |
| `ai_prompt_activate` | 활성 버전 변경 |
| `ai_prompt_deactivate` | 비활성화 |

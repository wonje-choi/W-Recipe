# Admin AI Recipe Summary API

`POST /api/admin/ai/recipe-summary`는 YouTube, blog, web URL 또는 직접 입력 텍스트를 레시피 구조 후보로 변환한다. 외부 AI SDK가 없는 MVP 환경에서는 내장 규칙 기반 파이프라인을 사용하며, 결과는 관리자 검수 전용 `pending_review` 레시피 Dish/Version으로 저장한다.

## Endpoint

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/admin/ai/recipe-summary` | 입력 자료를 재료/단계/팁 후보로 요약하고 검수 대기 레시피 생성 |

## Payload

```json
{
  "sourceId": "optional_crawled_source_id",
  "sourceUrl": "https://example.com/recipe",
  "sourceType": "web",
  "sourceTitle": "원본 제목",
  "sourceAuthor": "작성자 또는 채널",
  "sourceSummary": "수집된 요약 후보",
  "text": "직접 입력 원문 또는 요약 후보",
  "dishName": "관리자에게 보일 레시피명",
  "category": "일반",
  "tags": ["AI요약", "web"],
  "promptVersion": "recipe_summary:v1"
}
```

- `sourceId`가 있으면 기존 `crawled_source`를 사용한다.
- `sourceUrl`만 있으면 URL 해시로 기존 출처를 찾고, 없으면 새 출처 이력을 생성한다.
- URL이 없으면 `direct` 입력으로 처리한다.
- `promptVersion`이 없으면 활성 `recipe_summary` 프롬프트를 사용한다.
- 활성 프롬프트가 없으면 MVP용 내장 `recipe_summary:heuristic-v1` 프롬프트를 관리자 권한으로 자동 생성하고 사용한다.

## Processing Rules

1. 원본 제목, 작성자, URL, 수집일을 Version의 source 필드에 저장한다.
2. 재료 후보는 계량 단위와 재료 섹션을 기준으로 추출한다.
3. 조리 순서 후보는 단계 번호와 조리 동사를 기준으로 추출한다.
4. 팁, 대체 재료, 실패 방지 문구는 각각 tips 필드로 분리한다.
5. 재료나 조리 단계가 부족하면 `failurePreventionTips`에 `확인 필요` 문구를 저장한다.
6. 알레르기 후보는 일반 알레르기 키워드 매칭으로 `allergenInfo`에 저장한다.
7. 생성된 Dish와 Version은 모두 `pending_review` 상태로 저장한다.
8. 연결된 출처는 `summarized` 상태로 갱신한다.
9. `AIProcessingLog`는 요청 요약, 출력 요약, `promptVersion`, 완료/실패 상태를 기록한다.

## Response

```json
{
  "dish": { "id": "...", "status": "pending_review" },
  "version": {
    "id": "...",
    "status": "pending_review",
    "ingredients": ["두부 100g"],
    "steps": ["두부를 넣고 끓인다"],
    "failurePreventionTips": ["재료 후보를 자동 확정하지 못했습니다..."]
  },
  "source": { "id": "...", "crawlStatus": "summarized" },
  "candidate": {
    "summary": "...",
    "uncertainties": []
  },
  "log": {
    "requestType": "recipe_summary",
    "targetId": "version_id",
    "promptVersion": "recipe_summary:heuristic-v1",
    "status": "completed"
  }
}
```

## Audit Policy

성공 시 `admin_action_log`에 `ai_recipe_summary_create` action을 남긴다. 로그에는 생성된 Dish, Version, Source, AIProcessingLog의 요약 DTO만 저장한다.

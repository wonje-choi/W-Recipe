# 레시피 상세 버전 조회와 조회수 API

## 목적
하나의 요리 안에서 여러 레시피 버전을 안전하게 조회하고, 상세 화면의 버전 전환/출처 링크/원본 대비 AI 개량 비교에 필요한 응답을 제공한다.

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/recipes/<dish_id>/versions/<version_id>` | 버전 상세 조회 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/source` | 원본 출처 링크 조회 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/compare` | 기준 버전과 대상 버전 비교 |
| POST | `/api/recipes/<dish_id>/views` | 요리 조회수 증가 |
| POST | `/api/recipes/<dish_id>/versions/<version_id>/views` | 버전 조회수 증가 |

## 공개 정책
- Dish와 Version 모두 `approved` 상태일 때만 조회된다.
- `pending_review` AI 개량 버전은 공개 상세/비교 API에서 제외한다.
- Version의 `dish_id`가 URL의 `dish_id`와 다르면 404를 반환한다.

## 조회수 중복 방지
- 중복 기준은 session + target type + target id + 날짜다.
- 같은 세션에서 같은 대상은 하루에 한 번만 카운트한다.
- 이미 집계된 대상이면 `counted: false`와 현재 viewCount를 반환한다.

## Compare Query

| 이름 | 기본값 | 설명 |
| --- | --- | --- |
| `baseVersionId` | 빈 값 | 지정하지 않으면 같은 Dish의 공개 non-AI 버전을 기준으로 선택 |

## Compare Response

```json
{
  "code": 200,
  "baseVersion": {},
  "targetVersion": {},
  "comparison": {
    "ingredientsChanged": true,
    "stepsChanged": true,
    "nutritionChanged": false,
    "sodiumChanged": true,
    "targetAiModified": true,
    "sourceTypeChanged": true
  }
}
```

## Source Response

```json
{
  "code": 200,
  "source": {
    "available": false,
    "sourceType": "direct",
    "sourceUrl": "",
    "sourceTitle": "",
    "sourceAuthor": "",
    "sourceCollectedAt": "",
    "message": "등록된 원본 출처 링크가 없습니다."
  }
}
```

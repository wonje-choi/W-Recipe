# 공개 레시피 조회 API

## 목적
비로그인 사용자도 승인된 레시피 목록과 상세, 버전 목록을 조회할 수 있게 한다. 공개 API는 `approved` 상태의 Dish/Version만 반환한다.

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/recipes` | 공개 레시피 목록 |
| GET | `/api/recipes/<dish_id>` | 공개 요리 상세와 대표 버전 |
| GET | `/api/recipes/<dish_id>/versions` | 공개 버전 목록 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>` | 공개 버전 상세 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/source` | 원본 출처 링크 |
| GET | `/api/recipes/<dish_id>/versions/<version_id>/compare` | 기준 버전 비교 |
| POST | `/api/recipes/<dish_id>/views` | 요리 조회수 증가 |
| POST | `/api/recipes/<dish_id>/versions/<version_id>/views` | 버전 조회수 증가 |

## 목록 Query

| 이름 | 기본값 | 설명 |
| --- | --- | --- |
| `text` | `""` | 요리 이름 부분 검색 |
| `category` | `""` | 카테고리 필터 |
| `tag` | `""` | 태그 부분 검색 |
| `sort` | `latest` | `latest`, `popular`, `view_count` |
| `page` | `1` | 페이지 번호 |
| `dump` | `20` | 페이지 크기, 최대 `100` |

## 목록 응답

```json
{
  "code": 200,
  "items": [],
  "page": 1,
  "dump": 20,
  "total": 0,
  "empty": true,
  "message": "승인된 레시피가 없습니다."
}
```

## Detail Response

```json
{
  "code": 200,
  "dish": {
    "id": "dish_low_sodium_soup",
    "name": "저염 된장국",
    "thumbnailUrl": "",
    "hasImage": false,
    "status": "approved"
  },
  "representativeVersion": null,
  "versionCount": 0,
  "hasVersion": false
}
```

## Error Response

| Status | 조건 |
| --- | --- |
| 404 | 공개 가능한 Dish/Version이 없거나 지원하지 않는 경로 |
| 405 | 지원하지 않는 HTTP 메서드 |

## 공개 정책
- Dish와 Version 모두 `approved` 상태만 반환한다.
- `pending_review` AI 개량 버전은 관리자 승인 전까지 공개 API에서 제외한다.
- 이미지가 없으면 `thumbnailUrl`은 빈 문자열, `hasImage`는 `false`로 반환한다.
- 조회수 증가는 세션 기준 같은 대상 하루 1회만 집계한다.

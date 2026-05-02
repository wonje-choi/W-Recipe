# 이유식레시피 페이지 UI

이유식레시피 화면은 `page.recipe.list`의 `/recipes/baby-food` preset 화면으로 구현한다. `/recipes/:preset?` 목록 라우트를 유지하면서 이유식 전용 월령 단계, 안전 확인 항목, 보호자 안내를 추가한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/recipes/baby-food` | 이유식 카테고리/태그가 적용된 승인 레시피 목록 |
| `/recipes/baby-food?babyStage=early` | 초기 이유식 보기 |
| `/recipes/baby-food?babyStage=middle` | 중기 이유식 보기 |
| `/recipes/baby-food?babyStage=late` | 후기 이유식 보기 |
| `/recipes/baby-food?babyStage=complete` | 완료기 이유식 보기 |

## 단계 기준

| 값 | 표시 | 권장 월령 | 입자 크기 |
| --- | --- | --- | --- |
| `early` | 초기 | 만 4~6개월 | 곱게 간 미음 |
| `middle` | 중기 | 만 7~8개월 | 작게 으깬 죽 |
| `late` | 후기 | 만 9~11개월 | 잇몸으로 으깰 수 있는 무른 입자 |
| `complete` | 완료기 | 만 12개월 이후 | 작게 자른 부드러운 고형식 |

## 데이터 확장

`page.recipe.list/api.py`는 `preset=baby-food`일 때 각 Dish의 대표 승인 Version을 조회해 `babyPreview`를 추가한다.

| 필드 | 설명 |
| --- | --- |
| `stageLabel` | 요청 단계 또는 콘텐츠 기반 추정 단계 |
| `recommendedAge` | 단계별 권장 월령 표시 |
| `particleSize` | 단계별 입자 크기 안내 |
| `storage` | 보관 방법 안내 |
| `freezing` | 냉동 가능 여부와 주의 |
| `allergens` | 재료명 기반 알레르기 후보 |
| `warnings` | 꿀, 견과류, 생식, 질식 위험, 과도한 간 관련 경고 |
| `aiModified` | AI 개량 버전 여부 |

## UI 구성

- 이유식 전용 헤더 문구
- 초기/중기/후기/완료기 단계 필터
- 안전 확인 키워드 swatch
- 보호자 확인과 전문가 상담 안내 문구
- 카드별 권장 월령, 입자 크기, 보관/냉동 안내
- 카드별 알레르기 후보와 안전 경고

## 정책

이유식 정보는 보호자의 판단을 대체하지 않는다. 월령, 알레르기 이력, 질식 위험은 보호자가 최종 확인하고 필요하면 전문가 상담을 권장하는 문구를 고정 노출한다.

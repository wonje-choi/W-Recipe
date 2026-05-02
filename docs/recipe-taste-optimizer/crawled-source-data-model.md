# Recipe Taste Optimizer Crawled Source Data Model

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0006
- **목적**: 외부 자료를 원본 대체가 아닌 출처 안내와 요약/재구성 기반으로 관리하기 위한 수집 이력 DB 모델을 정의한다.

## 1. 구현 파일

| 모델 | 파일 | 테이블 | 역할 |
|---|---|---|---|
| CrawledSource | `src/portal/recipe/model/db/crawled_source.py` | `recipe_crawled_source` | 외부 URL, 수집 상태, 출처 메타데이터, 실패 로그 관리 |

## 2. CrawledSource 모델

| API 필드 | DB 필드 | 타입 예시 | 설명 |
|---|---|---|---|
| `id` | `id` | Char(32) | 수집 이력 ID, primary key |
| `sourceType` | `source_type` | Char(32) | `youtube`, `blog`, `web`, `direct` 등 |
| `sourceUrl` | `source_url` | Text | 원본 URL |
| `sourceUrlHash` | `source_url_hash` | Char(64) | URL 정규화 후 SHA-256 등으로 생성한 중복 감지용 해시 |
| `title` | `title` | Char(300) | 원본 제목 |
| `author` | `author` | Char(160) | 원본 작성자/채널명 |
| `thumbnailUrl` | `thumbnail_url` | Char(1024) | 썸네일 URL |
| `collectedTextSummary` | `collected_text_summary` | Text | 원문 전문이 아닌 요약/추출 후보 |
| `rawContentStoragePolicy` | `raw_content_storage_policy` | Char(32) | `summary_only`, `private_raw`, `none` 등 |
| `crawlStatus` | `crawl_status` | Char(32) | `pending`, `allowed`, `blocked`, `collected`, `summarized`, `failed`, `expired` |
| `robotsAllowed` | `robots_allowed` | Boolean | robots.txt/약관/운영 정책상 수집 가능 여부 |
| `duplicateOf` | `duplicate_of` | Char(32) | 중복 URL이면 원본 CrawledSource ID |
| `collectedAt` | `collected_at` | DateTime nullable | 수집 완료 시각 |
| `retryCount` | `retry_count` | Integer | 수집 실패 재시도 횟수 |
| `lastCheckedAt` | `last_checked_at` | DateTime nullable | 링크 유효성 또는 수집 가능 여부 마지막 확인 시각 |
| `errorMessage` | `error_message` | Text | 실패 사유. 민감 정보와 원문 전문 저장 금지 |
| `createdAt` | `created_at` | DateTime | 생성 시각 |
| `updatedAt` | `updated_at` | DateTime | 수정 시각 |

## 3. URL 중복 감지 전략

긴 URL을 직접 unique index로 만들면 DB 엔진/문자셋에 따라 인덱스 길이 제한 문제가 생길 수 있다. 따라서 다음 구조를 사용한다.

1. URL을 정규화한다.
2. 정규화 URL로 `source_url_hash`를 만든다.
3. `source_url_hash`에 unique index를 적용한다.
4. 중복이면 신규 수집 대신 `duplicate_of`에 기존 수집 이력 ID를 연결한다.

## 4. 원문 저장 정책

MVP 기본 정책은 `summary_only`다.

| 정책 | 설명 | 사용자 공개 여부 |
|---|---|---:|
| `summary_only` | 원문 전문 저장 없이 요약/추출 후보만 저장 | 요약만 공개 |
| `private_raw` | 운영상 필요한 경우 비공개 원문 스냅샷 저장 | 비공개 |
| `none` | URL과 메타데이터만 저장 | 원문 없음 |

사용자 화면에는 원본 제목, 작성자, URL, 출처 유형, 수집일, 원본 이동 버튼만 제공한다. 원문 전문을 그대로 노출하지 않는다.

## 5. 수집 상태 정책

| 상태 | 설명 |
|---|---|
| `pending` | 수집 대기 |
| `allowed` | 수집 가능 확인 |
| `blocked` | robots.txt/약관/차단 도메인 등으로 수집 제한 |
| `collected` | 수집 완료 |
| `summarized` | 요약 완료 |
| `failed` | 수집 실패 |
| `expired` | 링크 만료 또는 접근 불가 |

## 6. 인덱스 전략

| 목적 | 필드 |
|---|---|
| 중복 URL 감지 | `source_url_hash` unique |
| 출처 유형 필터 | `source_type` |
| 수집 상태 필터 | `crawl_status` |
| robots 허용 여부 필터 | `robots_allowed` |
| 중복 원본 연결 | `duplicate_of` |
| 최근 수집 정렬 | `collected_at`, `created_at` |

## 7. 완료 판정

이 문서는 FN-20260501-0006의 완료 기준을 충족한다.

- CrawledSource 모델을 정의했다.
- URL 중복 감지를 위한 unique hash 전략을 설계했다.
- 원문 전문 공개 금지와 요약 저장 중심 정책을 반영했다.
- 링크 만료/수집 실패/재시도 상태를 저장할 수 있게 했다.

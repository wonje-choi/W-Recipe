# 외부 URL 입력과 출처 관리 API

## 목적
자동 대량 크롤링 전 단계로 관리자가 수집 대상 URL과 처리 상태를 관리할 수 있게 한다. 본문 전문 저장은 하지 않고 요약 후보 중심으로 관리한다.

## 권한
모든 endpoint는 `admin` controller를 사용한다.

## Endpoints

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/admin/sources` | 출처 목록 |
| POST | `/api/admin/sources` | URL 등록 |
| GET | `/api/admin/sources/<source_id>` | 출처 상세 |
| PUT | `/api/admin/sources/<source_id>` | 출처 메타데이터 수정 |
| DELETE | `/api/admin/sources/<source_id>` | 출처 만료 처리 |
| PUT | `/api/admin/sources/<source_id>/status` | robots/crawl 상태 수정 |

## URL 등록 정책
- `sourceType`을 주지 않으면 URL host 기준으로 자동 판정한다.
- `youtube.com`, `youtu.be`는 `youtube`로 판정한다.
- `blog.*`, `tistory.com`, `medium.com`은 `blog`로 판정한다.
- 그 외는 `web`으로 판정한다.
- `source_url_hash`로 중복을 확인하고, 이미 있으면 새 row를 만들지 않고 `duplicate: true`로 기존 항목을 반환한다.

## 차단 도메인
- `constants.BLOCKED_SOURCE_DOMAINS`에 포함된 host 또는 하위 도메인은 blocked 처리한다.
- blocked URL은 `robotsAllowed=false`, `crawlStatus=blocked`, `errorMessage=Blocked domain`으로 저장한다.

## Payload

| API 필드 | DB 필드 | 설명 |
| --- | --- | --- |
| `sourceUrl` | `source_url` | 수집 대상 URL |
| `sourceType` | `source_type` | `youtube`, `blog`, `web`, `direct` 등 |
| `title` | `title` | 영상/문서 제목 |
| `author`, `channel` | `author` | 작성자 또는 유튜브 채널 |
| `thumbnailUrl` | `thumbnail_url` | 유튜브/문서 썸네일 |
| `summary`, `description`, `collectedTextSummary` | `collected_text_summary` | 본문 전문이 아닌 요약 후보 |
| `robotsAllowed` | `robots_allowed` | robots 허용 여부 |
| `crawlStatus` | `crawl_status` | 수집 처리 상태 |
| `errorMessage` | `error_message` | 오류 사유 |

## 상태 관리
- 상태 수정 시 `last_checked_at`을 갱신한다.
- 삭제는 물리 삭제 대신 `crawl_status=expired`로 처리한다.
- 등록/수정/상태 변경/만료 처리는 AdminActionLog에 기록한다.

## 원문 저장 정책
- `raw_content_storage_policy` 기본값은 `summary_only`다.
- 블로그/웹문서는 전문 저장 대신 요약 후보와 출처 메타데이터만 보관한다.

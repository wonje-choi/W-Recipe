# 관리자 Crawled Source Management UI

`page.admin.sources`는 외부 URL 수집 이력과 출처 상태를 운영자가 확인하고 보정하는 관리자 화면이다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/admin/sources` | 관리자 외부 자료 관리 화면 |
| `/admin/sources?status=failed` | 실패 상태 필터 화면 |

## 화면 구성

| 영역 | 설명 |
| --- | --- |
| 상태 요약 | 크롤링 상태별 외부 자료 수 표시와 빠른 필터 |
| 목록 | URL, 출처 유형, 원본 제목, 작성자, 수집 일자, 수집 상태 표시 |
| 검수 플래그 | 수집 허용, 중복 자료, 요약 완료, 관리자 검수, 링크 만료 여부 표시 |
| 편집 패널 | URL 메타데이터, 요약, 실패 사유, robots 허용, 수집 상태 수정 |
| 액션 | 원본 열기, 재시도, 허용 처리, 실패 처리, 만료 처리 |

## 앱 API

| 함수 | 설명 |
| --- | --- |
| `options()` | 출처 유형과 크롤링 상태 옵션 반환 |
| `sources()` | 필터링된 외부 자료 목록과 상태별 요약 반환 |
| `save_source()` | URL 등록 또는 출처 메타데이터 수정 |
| `status_action()` | 수집 상태, robots 허용 여부, 실패 사유 수정 |
| `retry_source()` | 실패/차단/만료 항목을 재시도 대기 상태로 전환 |
| `expire_source()` | 외부 링크를 만료 상태로 전환 |

## 상태 표시

목록과 편집 패널은 다음 운영 플래그를 함께 표시한다.

- 수집 허용 여부: `robots_allowed`
- 중복 자료 여부: 동일 URL 해시 또는 `duplicate_of`
- 요약 완료 여부: `collected_text_summary` 또는 `summarized` 상태
- 관리자 검수 여부: 검수성 상태 전환 또는 `last_checked_at`
- 링크 만료 여부: `expired` 상태

## 감사 로그

생성, 수정, 상태 변경, 재시도, 만료 처리 작업은 `admin_action_log`에 기록한다. before/after 값은 `struct.admin_log.create()`의 마스킹 정책을 따른다.

## 권한

`page.admin.sources`는 `admin` controller를 사용한다. 일반 사용자는 화면과 API를 사용할 수 없다.

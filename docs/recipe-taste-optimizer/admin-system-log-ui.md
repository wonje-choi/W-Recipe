# 관리자 System Log UI

`page.admin.logs`는 운영 중 발생하는 관리자 작업, 로그인 실패, AI 실패, 크롤링 실패 이벤트를 통합 조회하는 관리자 화면이다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/admin/logs` | 관리자 시스템 로그 화면 |
| `/admin/logs?type=ai_failure` | AI 실패 로그 필터 화면 |
| `/admin/logs?type=crawling_failure` | 크롤링 실패 로그 필터 화면 |

## 표시 로그 유형

| 유형 | 저장소 | 설명 |
| --- | --- | --- |
| 관리자 작업 | `admin_action_log` | 관리자 변경 행위와 before/after 마스킹 값 |
| 로그인 실패 | `user.login_failed_count`, `locked_until` | 실패 횟수와 계정 잠금 상태 |
| AI 실패 | `ai_processing_log` | 실패 상태의 AI 요청, 프롬프트 버전, 오류 메시지 |
| 크롤링 실패 | `crawled_source` | 실패, 차단, 만료 상태의 외부 자료 |
| API 오류 | 향후 영속 로그 저장소 | 현재 저장된 이벤트가 없으면 빈 상태로 표시 |
| 권한 오류 | 향후 영속 로그 저장소 | 현재 저장된 이벤트가 없으면 빈 상태로 표시 |

## 필터

- 유형
- 심각도
- 관리자 ID
- 대상 유형
- 시작일/종료일
- 키워드 검색

## 민감 정보 마스킹

화면 API는 다음 값을 노출 전에 다시 마스킹한다.

- 이메일 로컬 파트
- IP 마지막 옥텟
- password, token, apiKey, session, rawContent 계열 키
- 알레르기, 의료 메모 등 민감 프로필 키
- URL query string과 fragment

`admin_action_log` 자체도 `struct.admin_log.create()`의 before/after 마스킹 정책을 통과한다.

## 권한

`page.admin.logs`는 `admin` controller를 사용한다. 일반 사용자는 화면과 API를 사용할 수 없다.

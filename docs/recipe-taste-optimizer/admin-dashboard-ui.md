# 관리자 Dashboard UI

`page.dashboard`는 Recipe 운영자를 위한 관리자 첫 화면이다. 기존 일반 게시물 대시보드를 `layout.recipe`와 `admin` controller 기반 운영 지표 화면으로 교체한다.

## 경로

| 경로 | 설명 |
| --- | --- |
| `/dashboard` | 관리자 운영 대시보드 |

## API 함수

| 함수 | 설명 |
| --- | --- |
| `overview()` | 운영 지표, 검수 대기 큐, 외부 자료/AI 처리 상태 반환 |

## 표시 지표

- 전체 레시피 수
- 검수 대기 수
- 사용자 수
- 댓글 수
- 수정 요청 수
- AI 요청 수
- 최근 수집 외부 자료 수
- 외부 자료 오류 수
- AI 실패율
- 승인/반려 비율

## 검수 대기 큐

- 레시피 Dish 검수
- 레시피 Version 검수
- AI 결과 검수
- 수정 요청 처리
- 신고 처리

각 항목은 향후 관리자 세부 화면 경로로 이동하는 액션을 가진다.

## 운영 로그

- 최근 수집 외부 자료 5건
- AI 실패 로그 5건

## 권한

`page.dashboard`는 `admin` controller를 사용한다. `layout.recipe` 내비게이션의 관리자 메뉴는 `role=admin` 사용자에게만 표시된다.

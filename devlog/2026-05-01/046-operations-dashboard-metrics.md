# Recipe Taste Optimizer 운영 대시보드 지표 수집 구현

- **ID**: 046
- **날짜**: 2026-05-01
- **유형**: 기능 추가 / 문서 업데이트

## 작업 요약
관리자 Dashboard의 `overview` API가 운영 핵심 지표를 계산하도록 확장했다. 일간 활동, 레시피 조회, 저염식/이유식 조회, AI 요청/실패율/토큰/비용, 검수 대기, 승인/반려 비율, 참여 지표, 크롤링 실패율, 인기 레시피를 응답하고 화면에서 확인할 수 있게 했다.

## 변경 파일 목록

### Dashboard App
- `src/app/page.dashboard/api.py` — 운영 지표 집계 로직 확장, daily/review/recipe/AI/source/engagement metrics 응답 추가.
- `src/app/page.dashboard/view.ts` — 확장된 `operations` 응답 기본값과 렌더링 상태 반영.
- `src/app/page.dashboard/view.pug` — 오늘의 운영 신호, 레시피 조회 지표, 사용자 참여, AI 사용량, 크롤링 실패율, 인기 레시피 섹션 추가.

### 문서
- `src/portal/recipe/API.md` — Dashboard overview 응답 계약에 확장 지표 설명 추가.

## 검증
- diagnostics 오류 없음.
- `python3 -m py_compile src/app/page.dashboard/api.py` 통과.
- WIZ normal build 성공.
- 관리자 세션으로 `page.dashboard.overview` App API 호출 성공: `code=200`, metrics 6개, reviewQueue 5개, daily/인기 레시피/AI 실패율/크롤링 실패율 응답 확인.

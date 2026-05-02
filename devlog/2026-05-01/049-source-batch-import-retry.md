# 출처 배치 URL 등록과 실패 재시도 스케줄링 구현

- **ID**: 049
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자 출처 관리 페이지에 줄바꿈, 쉼표, CSV 형식의 URL 배치 등록 폼을 추가했다.
배치 등록은 요청당 최대 50개로 제한하며, robots.txt 확인, 중복 URL 판정, 차단 상태 저장을 처리한다.
실패한 출처 중 `retry_count < 3` 항목을 재시도 대기 상태로 되돌리는 일괄 재시도 기능과 현황 배지를 추가했다.

## 변경 파일 목록
- `src/portal/recipe/model/struct/source.py`: 실패 출처 재시도 대기열 조회 메서드 추가
- `src/app/page.admin.sources/api.py`: 배치 URL 파싱, robots.txt 확인, `batch_import()`, `retry_failed()` API와 재시도 요약 추가
- `src/app/page.admin.sources/view.ts`: 배치 등록 상태, 일괄 등록 호출, 실패 재시도 호출 상태 추가
- `src/app/page.admin.sources/view.pug`: 배치 URL 입력 패널, 실패/재시도 가능 배지, 일괄 재시도 버튼 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 관리자 출처 관리 템플릿 문법 확인
- 단일 URL 등록과 기존 개별 재시도 함수가 유지되는지 코드 경로 확인

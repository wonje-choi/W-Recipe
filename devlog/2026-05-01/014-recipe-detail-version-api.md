# Recipe Taste Optimizer 레시피 상세 버전 조회와 조회수 API 구현

- **ID**: 014
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
공개 레시피 상세 Route에 버전 상세, 원본 출처 링크, 기준 버전 비교, 조회수 증가 API를 추가했다. 조회수는 세션과 날짜 기준으로 같은 대상 하루 1회만 집계하도록 처리했다.

## 변경 파일 목록

### Route
- `src/route/recipe-public-detail/controller.py` — 버전 상세, 출처 링크, 비교 응답, 요리/버전 조회수 증가 API 추가

### 문서
- `docs/recipe-taste-optimizer/recipe-detail-version-api.md` — 상세 버전/출처/비교/조회수 API와 중복 방지 정책 정리
- `docs/recipe-taste-optimizer/public-recipe-api.md` — 공개 API endpoint 목록 갱신
- `src/portal/recipe/README.md` — Public Routes 목록 갱신

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

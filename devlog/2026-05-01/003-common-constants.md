# Recipe Taste Optimizer 공통 상태값과 정책 상수 정의

- **ID**: 003
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
백엔드 모델, API, 프론트엔드 필터 UI에서 공통으로 사용할 상태값과 정책 상수를 정의했다. 신규 `recipe` Portal Package 골격을 만들고 Python/TypeScript 상수 파일을 추가했으며, canonical value는 lowercase snake_case로 통일했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/portal.json` — recipe 패키지 메타데이터 추가
- `src/portal/recipe/README.md` — 패키지 범위와 상수 사용법 문서화
- `src/portal/recipe/model/constants.py` — 백엔드 공통 상수 Model 추가
- `src/portal/recipe/libs/constants.ts` — 프론트엔드 공통 상수와 타입 추가

### 문서
- `docs/recipe-taste-optimizer/common-constants.md` — 공통 상태값과 정책 상수 문서화

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- `portal.json` JSON 구문 검증 통과.
- Python 상수 파일 py_compile 통과.
- WIZ 일반 빌드 성공.
- 빌드 중 기존 npm 의존성 취약점 경고가 출력됐으나 이번 변경으로 인한 빌드 실패는 없음.

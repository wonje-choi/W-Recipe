# Recipe Taste Optimizer 수정 요청과 신고 API 구현

- **ID**: 023
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
사용자 수정 요청과 신고 생성 API, 관리자 목록/상태 변경 API를 구현했다. 수정 요청 유형과 신고 대상/사유를 상수로 정의하고, 처리 시 담당자와 처리 시각, 관리자 메모를 저장하도록 정리했다.

## 변경 파일 목록

### 정책 상수와 데이터 모델
- `src/portal/recipe/model/constants.py`: 수정 요청 유형, 신고 대상, 신고 사유 상수를 추가했다.
- `src/portal/recipe/libs/constants.ts`: 프론트엔드 상수와 표시 라벨, 타입 정의를 추가했다.
- `src/portal/recipe/model/db/report.py`: 신고 상세 내용과 관리자 메모 필드를 추가했다.

### 비즈니스 로직
- `src/portal/recipe/model/struct/comment.py`: 수정 요청 생성/목록/처리, 신고 생성/목록/처리 로직을 실제 DB 필드에 맞춰 정리했다.
- `src/portal/recipe/model/struct/comment.py`: 중복 open 수정 요청 방지, 중복 신고 방지, 댓글 신고 시 report_count 증가와 reported 상태 전환을 구현했다.

### API Route
- `src/route/recipe-edit-requests/`: 로그인 사용자 수정 요청 생성 API를 추가했다.
- `src/route/recipe-reports/`: 로그인 사용자 신고 생성 API를 추가했다.
- `src/route/recipe-admin-edit-request-list/`: 관리자 수정 요청 목록 API를 추가했다.
- `src/route/recipe-admin-edit-request-status/`: 관리자 수정 요청 상태 변경 API를 추가했다.
- `src/route/recipe-admin-report-list/`: 관리자 신고 목록 API를 추가했다.
- `src/route/recipe-admin-report-status/`: 관리자 신고 상태 변경 API를 추가했다.

### 문서
- `docs/recipe-taste-optimizer/feedback-api.md`: 수정 요청과 신고 API 계약을 문서화했다.
- `src/portal/recipe/README.md`: Feedback Route, 타입 상수, 처리 정책을 패키지 문서에 반영했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 변경된 Python 파일 문법 검사 통과.
- 신규 Route 반영을 위해 clean WIZ build 수행, 빌드 성공.

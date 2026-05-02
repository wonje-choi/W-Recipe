# Recipe Taste Optimizer 마이페이지와 개인 선호도 API 구현

- **ID**: 024
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
로그인 사용자의 내 프로필, 개인 선호도, 활동 내역 API를 구현했다. 선호도 배열 필드를 JSON 문자열로 정규화하고, 활동 API는 댓글/수정 요청/AI 개량 요청/즐겨찾기/최근 본 레시피 목록을 자기 계정 범위로만 반환하도록 구성했다.

## 변경 파일 목록

### 비즈니스 로직
- `src/portal/recipe/model/struct/user.py`: 안전한 프로필 응답, 닉네임 수정, 선호도 정규화/저장/응답 변환 로직을 추가했다.

### API Route
- `src/route/recipe-my-profile/`: 내 프로필 조회와 닉네임 수정 API를 추가했다.
- `src/route/recipe-my-preferences/`: 내 개인 선호도 조회/저장 API를 추가했다.
- `src/route/recipe-my-activity/`: 내 댓글, 수정 요청, AI 개량 요청, 즐겨찾기, 최근 본 레시피 목록 API를 추가했다.

### 문서
- `docs/recipe-taste-optimizer/mypage-api.md`: 마이페이지 API 계약과 개인정보 응답 범위를 문서화했다.
- `src/portal/recipe/README.md`: My Page Route와 개인정보 정책을 패키지 문서에 반영했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 변경된 Python 파일 문법 검사 통과.
- 신규 Route 반영을 위해 clean WIZ build 수행, 빌드 성공.

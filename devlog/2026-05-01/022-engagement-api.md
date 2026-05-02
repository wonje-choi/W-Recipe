# Recipe Taste Optimizer 사용자 참여 API 구현

- **ID**: 022
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
로그인 사용자의 댓글, 즐겨찾기, 최근 본 레시피 API를 구현했다. 댓글 조회는 guest에게 열어두고, 댓글 작성/삭제와 즐겨찾기/최근 본 레시피 쓰기 요청은 로그인 사용자만 사용할 수 있도록 분리했다.

## 변경 파일 목록

### 데이터 모델
- `src/portal/recipe/model/db/recent_view.py`: 사용자별 최근 본 레시피 테이블을 추가하고 사용자/레시피 버전 조합 유니크 제약을 정의했다.
- `src/portal/recipe/model/struct.py`: `recent_view` 테이블 초기화를 추가했다.

### 비즈니스 로직
- `src/portal/recipe/model/struct/comment.py`: 댓글 작성/조회/삭제, 즐겨찾기 상태/토글, 최근 본 레시피 저장/조회 로직을 정리했다.
- `src/portal/recipe/model/struct/comment.py`: 댓글 작성 시 공개 레시피 버전 검증, 길이 제한, 20초 연속 작성 제한을 적용했다.

### API Route
- `src/route/recipe-comments/`: 공개 댓글 조회와 로그인 댓글 작성 API를 추가했다.
- `src/route/recipe-comment-detail/`: 작성자 또는 admin의 댓글 삭제 요청 API를 추가했다.
- `src/route/recipe-favorite/`: 현재 사용자의 즐겨찾기 상태 조회, 토글, 해제 API를 추가했다.
- `src/route/recipe-recent-views/`: 현재 사용자의 최근 본 레시피 저장/조회 API를 추가했다.

### 문서
- `docs/recipe-taste-optimizer/engagement-api.md`: 사용자 참여 API 계약과 요청/응답 형식을 문서화했다.
- `src/portal/recipe/README.md`: 참여 Route, 최근 본 레시피 모델, 참여 정책을 패키지 문서에 반영했다.

## 검증
- `get_errors`로 변경 파일 오류 없음 확인.
- `python3 -m py_compile`로 변경된 Python 파일 문법 검사 통과.
- 신규 Route와 DB model 반영을 위해 clean WIZ build 수행, 빌드 성공.

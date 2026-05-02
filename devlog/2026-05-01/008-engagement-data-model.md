# Recipe Taste Optimizer 참여 기능 데이터 모델 구현

- **ID**: 008
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
댓글, 즐겨찾기, 수정 요청, 신고 기능의 저장 기반을 recipe 패키지에 추가했다. 즐겨찾기와 신고는 사용자별 중복 생성을 방지하기 위해 composite unique index를 적용했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/comment.py` — 레시피 버전 댓글 DB 모델 추가
- `src/portal/recipe/model/db/favorite_recipe.py` — 사용자별 즐겨찾기 DB 모델과 중복 방지 index 추가
- `src/portal/recipe/model/db/recipe_edit_request.py` — 레시피 수정 요청 DB 모델 추가
- `src/portal/recipe/model/db/report.py` — 댓글/레시피 신고 DB 모델과 중복 신고 방지 index 추가
- `src/portal/recipe/README.md` — 참여 기능 모델과 중복 방지 정책 추가

### 문서
- `docs/recipe-taste-optimizer/engagement-data-model.md` — 참여 기능 필드 매핑, 권한/운영 정책, 중복 방지 기준 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

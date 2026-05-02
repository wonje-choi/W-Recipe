# 영양사 전문가 배정과 검수 의견 관리 구현

- **ID**: 055
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
영양사 등 전문가 정보를 관리하는 테이블과 레시피 수정 요청/AI 개량 결과에 연결 가능한 전문가 배정 테이블을 추가했다.
관리자 참여 관리 화면에는 전문가 탭을 추가해 전문가 목록을 등록·수정할 수 있게 했고, 수정 요청 목록 행과 상세 패널에서 담당 전문가, 배정 상태, 검수 의견을 저장할 수 있게 했다.

## 변경 파일 목록
- `src/portal/recipe/model/db/expert.py`: `recipe_expert` 테이블 모델 추가
- `src/portal/recipe/model/db/expert_assignment.py`: `recipe_expert_assignment` 테이블 모델 추가
- `src/portal/recipe/model/struct/expert.py`: 전문가 CRUD, 대상 검증, 배정/검수 의견 저장 로직 추가
- `src/portal/recipe/model/constants.py`: 전문가 상태, 배정 상태, 배정 대상 타입 상수 추가
- `src/portal/recipe/model/struct.py`: 전문가 테이블 초기화와 `struct.expert` 연결 추가
- `src/app/page.admin.feedback/api.py`: 전문가 목록/저장 API, 수정 요청 배정 API, 수정 요청 DTO 배정 정보 추가
- `src/app/page.admin.feedback/view.ts`: 전문가 탭 상태, 목록 로딩, 전문가 저장, 수정 요청 배정 저장 로직 추가
- `src/app/page.admin.feedback/view.pug`: 수정 요청 행 배정 드롭다운, 상세 검수 의견 UI, 전문가 관리 탭 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 관리자 참여 관리 템플릿 문법 확인
- 기존 댓글·신고·수정 요청·구독 탭의 페이지 전환 분기와 필터 분기가 유지되는지 코드 경로 확인

# 관리자 레시피 편집 AI 메타 생성 기능 구현

- **ID**: 052
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자 레시피 편집 화면에서 저장된 레시피 버전을 기반으로 제목, 설명, 영상 대본 후보를 생성할 수 있도록 했다.
생성 결과는 미리보기로 표시하고, 관리자가 적용 버튼을 누른 항목만 기존 입력 필드에 반영되도록 해 실패나 취소 시 기존 폼 값을 보존한다.

## 변경 파일 목록
- `src/portal/recipe/model/struct/ai.py`: `generate_recipe_meta(dish_id)` 추가
- `src/app/page.admin.recipes/api.py`: `generate_meta()` API 추가
- `src/app/page.admin.recipes/view.ts`: 생성 상태, 결과 상태, 필드별 적용 메서드 추가
- `src/app/page.admin.recipes/view.pug`: 레시피 편집 폼 내부 AI 생성 버튼과 미리보기/적용 UI 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 관리자 레시피 템플릿 문법 확인
- 생성 실패 경로에서 기존 폼 값이 초기화되지 않는 흐름 확인

# 레시피 상세 출처 원문 토글과 관리자 원문 저장 구현

- **ID**: 048
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자 출처 관리 화면에서 출처 원문 전문을 입력하고 저장할 수 있도록 `raw_content` 필드를 추가했다.
레시피 상세 페이지는 연결된 출처의 원문 보관 정책이 `full`이고 원문이 있을 때만 접기/펼치기 토글과 저작권 안내 문구를 표시한다.

## 변경 파일 목록
- `src/portal/recipe/model/db/crawled_source.py`: `raw_content` 컬럼 추가
- `src/portal/recipe/model/struct.py`: SQLite 기존 테이블용 `raw_content` 컬럼 보강 마이그레이션 추가
- `src/portal/recipe/model/struct/source.py`: 원문 저장/조회 정책 처리 추가
- `src/app/page.admin.sources/api.py`: 출처 DTO와 저장 payload에 `rawContent` 반영
- `src/app/page.admin.sources/view.ts`: 원문 입력 폼 상태 바인딩 추가
- `src/app/page.admin.sources/view.pug`: 원문 입력 textarea와 안내 문구 추가
- `src/app/page.recipe.detail/api.py`: 상세 출처 DTO에 원문과 저장 정책 포함
- `src/app/page.recipe.detail/view.ts`: 원문 토글 상태와 표시 조건 추가
- `src/app/page.recipe.detail/view.pug`: 원문 접기/펼치기 영역과 저작권 안내 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 변경 Pug 템플릿 2종 문법 확인
- 기존 상세 페이지는 원문이 없거나 정책이 `full`이 아니면 토글을 표시하지 않도록 확인

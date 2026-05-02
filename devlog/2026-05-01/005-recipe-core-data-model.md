# Recipe Taste Optimizer 레시피 핵심 데이터 모델 구현

- **ID**: 005
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
요리 단위와 레시피 버전을 분리하는 핵심 DB 모델을 추가했다. `recipe_dish`는 요리명, 설명, 카테고리, 태그, 대표 이미지, 조회수, 공개 상태를 관리하고, `recipe_version`은 출처별/AI 개량별 레시피 상세와 검수 상태를 관리한다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/recipe_dish.py` — 요리 단위 DB 모델 추가
- `src/portal/recipe/model/db/recipe_version.py` — 출처별/AI 개량별 레시피 버전 DB 모델 추가
- `src/portal/recipe/README.md` — 레시피 DB 모델과 공개 조회 정책 추가

### 문서
- `docs/recipe-taste-optimizer/recipe-core-data-model.md` — RecipeDish/RecipeVersion 필드 매핑, JSON 필드 정책, 인덱스 전략, 공개 조회 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

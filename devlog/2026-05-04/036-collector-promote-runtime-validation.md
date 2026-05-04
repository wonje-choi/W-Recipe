# 수집 결과 → 검수 대기 레시피 등록 런타임 검증

- **ID**: 036
- **날짜**: 2026-05-04
- **유형**: 검증

## 작업 요약
관리자 세션으로 `/wiz/api/page.admin.collector/promote_results` API를 호출하여 수집 결과(`recipe_collection_result`)가 `recipe_dish` / `recipe_version`으로 검수 대기(`pending_review`) 상태로 정상 등록되는지, 중복 호출이 차단되는지, 공개 페이지에 노출되지 않는지 확인했다.

## 검증 환경
- 서버: `localhost:3000` (운영 중인 wiz 서버, 재시작 없음)
- 프로젝트: `main`
- 관리자 세션: `admin_41180dnjswp` (`role=admin`)
- 사용 결과 ID: `yotfanjkxembufdaseqvspnbhurmhono` (`https://www.google.com/search?q=...` 키워드 폴백 결과)

## 검증 결과

### 1차 promote_results 호출
응답:
```json
{"code":200,"data":{"created":1,"skipped":0,"failed":0,
  "items":[{"resultId":"yotfanjk...","status":"created",
            "dishId":"lhgvhfqawtovfwfhomksmliubftvgtwk",
            "versionId":"vcbanfmzaaqndqetavbikuccvivuwelm"}]}}
```
- created=1 ✓
- dishId / versionId 응답에 포함 ✓

### DB 상태 확인 (recipe.db)
- `recipe_dish.status` = `pending_review` ✓
- `recipe_version.status` = `pending_review` ✓
- `recipe_version.source_url` = 원문 Google 검색 URL ✓
- `recipe_version` 카운트 = 1 (중복 미생성) ✓
- `recipe_collection_result.raw_metadata`에 `promotedRecipeDishId`, `promotedRecipeVersionId`, `promotedAt`, `promotedBy=admin_41180dnjswp` 기록 ✓

### 2차 promote_results 호출 (중복)
응답:
```json
{"code":200,"data":{"created":0,"skipped":1,"failed":0,
  "items":[{"resultId":"yotfanjk...","status":"skipped",
            "reason":"이미 검수 대기 레시피로 등록된 결과입니다.",
            "dishId":"lhgvhfqawtovfwfhomksmliubftvgtwk",
            "versionId":"vcbanfmzaaqndqetavbikuccvivuwelm"}]}}
```
- skipped=1, 같은 dish/version id 반환 ✓
- DB 재조회 결과 새 행 미생성 (dishes 5건, versions 4건 유지) ✓

### 공개 노출 차단 확인
- `page.recipe.list/search?text=이유식&dump=50` 응답에 promoted dish 미포함 (approved인 `qa_dish_baby`만 노출) ✓
- `page.recipe.detail/load?dishId=lhgvhfqawtovfwfhomksmliubftvgtwk` 응답: `404 "레시피를 찾을 수 없습니다."` (public=True 필터에 차단) ✓

## 결론
TODO `수집 결과 레시피화 런타임 검증`의 모든 완료 기준을 통과했다.
- 수집 결과 선택 시 `recipe_dish`/`recipe_version`이 실제 생성된다.
- 생성된 dish/version 모두 `pending_review` 상태로 저장된다.
- 승인 전 공개 페이지에 노출되지 않는다.
- 같은 원문 URL은 중복 등록되지 않는다 (raw_metadata 플래그 + source_url 양쪽 가드).
- 관리자 응답에서 created/skipped/failed 카운트를 확인할 수 있다.

## 한계
- 브라우저 UI 클릭 검증은 수행하지 못했다 (curl로 동일 API 직접 호출).
- 키워드 폴백 결과(`recipePrompt` 포함)만 검증했다. 실제 외부 호출 결과(`fallback=False`) 케이스는 미검증.

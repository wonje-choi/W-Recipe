# Recipe Taste Optimizer 안정성 요구사항 구현

- **ID**: 039
- **날짜**: 2026-05-01
- **유형**: 기능 추가 / 문서 업데이트

## 작업 요약
세션 기반 요청 제한을 공통 `base` controller에 추가하고 공개 Recipe REST Route도 `base` controller를 통과하도록 조정했다. 공개 홈, 목록, 상세 화면은 이미지 URL 로딩 실패 시 기본 음식 이미지를 보조 배경으로 표시하도록 보강했다.

기존에 구현되어 있던 로그인 실패 제한, 댓글 연속 작성 제한, 크롤링 실패 재시도/로그, AI 결과 재생성 기능을 확인하고 Recipe 패키지 README에 안정성 정책과 외부 링크 오류 감지 배치 설계를 정리했다.

## 변경 파일 목록
- `src/controller/base.py`: 세션 기준 60초 120회 요청 제한 추가
- `src/route/recipe-public-list/app.json`: 공개 목록 Route의 controller를 `base`로 변경
- `src/route/recipe-public-detail/app.json`: 공개 상세 Route의 controller를 `base`로 변경
- `src/route/recipe-comments/app.json`: 댓글 목록/작성 Route의 controller를 `base`로 변경
- `src/route/recipe-comment-detail/app.json`: 댓글 상세 Route의 controller를 `base`로 변경
- `src/app/page.recipe.home/view.ts`: 홈 카드 이미지 다중 배경 fallback 적용
- `src/app/page.recipe.list/view.ts`: 목록 카드 이미지 다중 배경 fallback 적용
- `src/app/page.recipe.detail/view.ts`: 상세 대표 이미지 다중 배경 fallback 적용
- `src/portal/recipe/README.md`: 안정성 정책과 외부 링크 오류 감지 배치 설계 문서화

## 검증
- `python3 -m py_compile src/controller/base.py` 통과
- VS Code diagnostics: 변경한 Python/TypeScript/README 파일 오류 없음
- WIZ normal build 성공 (`success: true`, `errors: null`)

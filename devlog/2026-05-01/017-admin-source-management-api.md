# Recipe Taste Optimizer 외부 URL 입력과 출처 관리 API 구현

- **ID**: 017
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자가 수집 대상 URL과 처리 상태를 관리할 수 있도록 출처 관리 Route를 추가했다. URL 등록 시 sourceType 자동 판정, source_url_hash 중복 확인, 차단 도메인 처리, robots/crawl 상태 관리를 수행하며 원문 전문이 아닌 요약 후보 중심으로 저장한다.

## 변경 파일 목록

### Route
- `src/route/recipe-admin-source-list/app.json` — `/api/admin/sources` 관리자 출처 목록/등록 Route 설정
- `src/route/recipe-admin-source-list/controller.py` — URL 등록, 중복 확인, 목록 조회 구현
- `src/route/recipe-admin-source-detail/app.json` — `/api/admin/sources/<path:path>` 관리자 출처 상세 Route 설정
- `src/route/recipe-admin-source-detail/controller.py` — 출처 상세/수정/만료/상태 변경 구현

### Portal Package
- `src/portal/recipe/model/constants.py` — 차단 도메인 상수 추가
- `src/portal/recipe/model/struct/source.py` — sourceType 자동 판정과 차단 도메인 확인 유틸리티 추가
- `src/portal/recipe/README.md` — Source Routes 섹션 추가

### 문서
- `docs/recipe-taste-optimizer/admin-source-management-api.md` — 출처 관리 API, URL 등록 정책, payload 매핑, 원문 저장 정책 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- 새 Route 추가로 WIZ 클린 빌드 수행 및 성공.
- 빌드 출력에 npm audit 취약점 경고가 표시되었으나 이번 변경의 빌드 오류는 아님.

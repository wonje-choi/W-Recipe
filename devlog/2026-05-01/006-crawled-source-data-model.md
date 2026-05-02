# Recipe Taste Optimizer 외부 출처와 수집 이력 모델 구현

- **ID**: 006
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
외부 자료의 URL, 출처 메타데이터, 수집 상태, robots 허용 여부, 중복 URL, 링크 만료/실패 로그를 관리하는 CrawledSource DB 모델을 추가했다. 긴 URL unique index 문제를 피하기 위해 원본 URL은 Text로 보존하고, 중복 감지는 `source_url_hash` unique 필드로 처리하도록 설계했다.

## 변경 파일 목록

### Portal Package
- `src/portal/recipe/model/db/crawled_source.py` — 외부 자료 수집 이력 DB 모델 추가
- `src/portal/recipe/README.md` — 출처 수집 정책과 URL 중복 감지 기준 추가

### 문서
- `docs/recipe-taste-optimizer/crawled-source-data-model.md` — CrawledSource 필드 매핑, 원문 저장 정책, 수집 상태, 인덱스 전략 정리

## 검토 결과
- VS Code 문제 진단 기준 오류 없음.
- Python py_compile 통과.
- WIZ 일반 빌드 성공.

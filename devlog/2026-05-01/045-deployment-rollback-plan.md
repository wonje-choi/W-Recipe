# Recipe Taste Optimizer 배포 준비와 롤백 계획 작성

- **ID**: 045
- **날짜**: 2026-05-01
- **유형**: 문서 업데이트

## 작업 요약
개발, 스테이징, 운영 환경별 배포 기준과 설정 체크리스트, DB 초기화/seed 절차, 관리자 배포 후 검증, 로그 확인, 코드/DB/콘텐츠 롤백 기준을 정리했다. README에서 배포 문서를 바로 찾을 수 있도록 링크를 추가했다.

## 변경 파일 목록

### 문서
- `src/portal/recipe/DEPLOYMENT.md` — 환경 매트릭스, config/secret 체크리스트, build 기준, DB 초기화와 seed, 관리자 검증, 로그/헬스 체크, 롤백 계획, go/no-go 기준 작성.
- `src/portal/recipe/README.md` — 배포 준비와 롤백 절차 문서 링크 추가.

## 검증
- 문서 diagnostics 오류 없음.
- WIZ normal build 성공.

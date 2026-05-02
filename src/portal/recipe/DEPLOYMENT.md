# Recipe Taste Optimizer Deployment And Rollback Plan

이 문서는 Recipe Taste Optimizer MVP를 개발, 스테이징, 운영 환경에 반영하기 전 확인해야 할 배포 준비, 초기화, 검증, 롤백 절차를 정리한다. 실제 배포 명령은 운영 플랫폼의 승인된 절차를 따른다.

## 1. Release Scope

MVP 배포 범위는 아래 항목까지다.

- 공개 레시피 메인/목록/상세 조회
- 저염식/이유식 표시와 안전 문구
- 로그인, 마이페이지, 댓글, 즐겨찾기, 수정 요청, 신고
- 관리자 레시피/출처/AI/참여/로그 관리
- AI 요약/특수식단 개량 후보 생성과 관리자 검수
- `recipe` SQLite namespace 기반 데이터 저장

## 2. Environment Matrix

| Environment | Purpose | Data Policy | Deployment Gate |
| --- | --- | --- | --- |
| Development | 기능 구현과 로컬 QA | 개발 DB, 재생성 가능 | WIZ normal build 통과 |
| Staging | 운영 전 리허설 | 운영과 유사한 샘플 또는 익명화 데이터 | 통합 QA 핵심 시나리오 통과 |
| Production | 실제 운영 | 실데이터, 백업 필수 | 운영자 승인, 백업 완료, 롤백 경로 확인 |

## 3. Configuration Checklist

현재 MVP 코드가 직접 읽는 필수 OS 환경 변수는 없다. 설정의 최종 기준은 WIZ project config와 운영 런타임 설정이다.

### Required Project Config

- `project/main/config/database.py`에 `recipe` namespace가 있어야 한다.
- SQLite 운영 기준 기본값:

```python
recipe = season.util.stdClass(type="sqlite", path="data/recipe.db")
```

### Operator-Managed Secrets

아래 값은 코드 저장소에 커밋하지 않고 운영자 금고나 배포 플랫폼 secret으로 관리한다.

| Secret | Use |
| --- | --- |
| 초기 관리자 이메일 | 최초 seed 실행 시 `admin_email`로만 사용 |
| 초기 관리자 임시 비밀번호 | 해시 생성 후 폐기하고 운영자는 최초 로그인 뒤 변경 |
| WIZ/Flask session secret | 플랫폼 공통 config에서 관리 |
| 외부 AI provider key | 현재 MVP 휴리스틱 흐름에는 필수 아님. 외부 모델 연동 시 별도 secret으로 추가 |

## 4. Pre-Deployment Checklist

배포 전 아래 항목을 순서대로 확인한다.

- [ ] `currentProject`가 배포 대상 프로젝트인지 확인한다.
- [ ] `config/database.py`에 `recipe` namespace가 설정되어 있다.
- [ ] `src/portal/recipe/README.md`, `API.md`, `OPERATIONS.md`, `QA.md`, `DEPLOYMENT.md`가 최신 상태다.
- [ ] 새 API 함수 추가/삭제/이름 변경이 없다면 normal build를 사용한다.
- [ ] 새 API 함수 추가/삭제/이름 변경이 있었다면 clean build를 1회 수행한다.
- [ ] SQLite 운영 DB 파일을 배포 전에 백업한다.
- [ ] 초기 관리자 계정 생성 절차와 임시 비밀번호 전달 경로를 운영자와 확인한다.
- [ ] 통합 QA 결과 문서의 핵심 smoke가 staging에서 재현된다.

## 5. Build Procedure

일반 변경 배포 전에는 WIZ normal build를 기준으로 한다.

```bash
# WIZ MCP build 또는 승인된 WIZ 빌드 절차 사용
clean=false
```

Clean build가 필요한 경우는 다음으로 제한한다.

- 새 `api.py` 함수 추가
- 기존 API 함수 삭제 또는 이름 변경
- `socket.py` 추가/수정
- 일반 build 후 API endpoint 캐시 문제가 확인된 경우

`build/`, `bundle/` 산출물은 직접 수정하지 않는다.

## 6. Database Initialization And Migration

### Fresh Environment

1. `config/database.py`에 `recipe` namespace를 설정한다.
2. WIZ runtime에서 `portal/recipe/struct`가 로드되면 필요한 테이블은 `create_table(safe=True)`로 생성된다.
3. 초기 관리자 비밀번호 해시를 WIZ runtime에서 생성한다.
4. seed를 실행해 샘플 레시피, 데모 사용자, 선택적 관리자 계정을 준비한다.

WIZ runtime 예시:

```python
struct = wiz.model("portal/recipe/struct")
seed = wiz.model("portal/recipe/seed")
admin_password_hash = struct.auth.create_admin_password_hash("<temporary-password>")
result = seed.run(admin_email="admin@example.com", admin_password_hash=admin_password_hash)
```

실행 후 운영자는 즉시 임시 비밀번호를 폐기하고, 최초 로그인 뒤 비밀번호를 변경한다.

### Existing Environment

현재 MVP에는 별도 schema migration script가 없다. `Struct._init_tables()`가 누락 테이블을 safe create로 보강한다.

배포 전 데이터 변경 위험이 있는 경우:

1. `data/recipe.db`를 타임스탬프가 포함된 파일명으로 백업한다.
2. Staging DB에서 같은 코드로 build와 핵심 QA를 먼저 수행한다.
3. 운영 DB에는 물리 삭제보다 상태 변경(`hidden`, `rejected`, `expired`)을 우선한다.
4. 수동 schema 변경이 필요하면 별도 migration task를 만들고, 이 문서만으로 처리하지 않는다.

## 7. Seed Data Procedure

Seed는 고정 ID와 upsert 방식이므로 반복 실행해도 같은 샘플 데이터가 중복 생성되지 않는다.

Seed가 준비하는 데이터:

- 공개 저염식 레시피
- 공개 이유식 레시피
- 공개 고단백 레시피
- 검수 대기 AI 개량 후보
- 데모 사용자 취향 데이터
- 선택적 관리자 계정

운영 배포에서는 샘플 레시피가 실제 공개 데이터와 섞이는 것이 부적절하면 staging에서만 seed를 실행한다. 운영에서는 관리자 계정 생성만 별도 초기화 절차로 수행한다.

## 8. Admin Release Verification

배포 직후 관리자는 아래 흐름을 확인한다.

- [ ] 관리자 로그인 성공과 `me` 응답의 role 확인
- [ ] `/admin/recipes` 목록 로딩
- [ ] `/admin/sources` 실패/대기 출처 필터 확인
- [ ] `/admin/ai` 프롬프트 목록과 활성 프롬프트 확인
- [ ] `/admin/feedback` 신고/수정 요청 목록 확인
- [ ] `/admin/logs` 관리자 작업 로그 확인
- [ ] 검수 대기 레시피 또는 AI 후보 1건을 승인/반려 리허설
- [ ] 공개 화면에서 승인 항목 노출, 숨김 항목 미노출 확인

## 9. Log And Health Checks

배포 직후 30분 동안 아래 항목을 확인한다.

- WIZ build output에 error가 없는지 확인
- `/api/recipes`가 200과 예상 total을 반환하는지 확인
- `/api/admin/recipes`가 admin cookie로 200을 반환하는지 확인
- user cookie로 `/api/admin/*` 접근 시 401이 반환되는지 확인
- XSS payload 댓글이 400으로 차단되는지 확인
- AI 요청 실패 시 사용자 응답에는 내부 stack trace가 노출되지 않는지 확인
- 관리자 로그에 password, token, allergy, raw content가 원문 노출되지 않는지 확인

## 10. Rollback Plan

### Code Rollback

1. 운영 배포 전 code artifact 또는 git revision을 기록한다.
2. 새 배포 후 build 실패 또는 핵심 smoke 실패가 발생하면 이전 artifact로 되돌린다.
3. 되돌린 뒤 normal build를 수행한다.
4. API 함수 목록 변경이 포함된 배포였다면 rollback 후 clean build를 1회 수행한다.
5. 문제 원인과 영향 범위를 devlog 또는 incident note에 남긴다.

### Database Rollback

1. 배포 직전 `data/recipe.db` 백업 파일을 준비한다.
2. 데이터 손상이 확인되면 서비스를 쓰기 차단 상태로 전환한 뒤 백업 DB로 교체한다.
3. 백업 복원 후 공개 목록, 관리자 목록, 로그인, 로그 조회 smoke를 다시 수행한다.
4. 상태 전환 실수는 가능하면 DB 복원보다 관리자 상태값(`approved`, `hidden`, `rejected`, `expired`) 수정으로 회복한다.

### Content Rollback

콘텐츠 오류는 물리 삭제보다 상태 전환으로 처리한다.

- 공개 레시피 오류: `recipe_dish` 또는 `recipe_version`을 `hidden`으로 전환
- AI 결과 오류: `ai_recipe_modification`을 `rejected`로 전환
- 출처 오류: `crawled_source`를 `expired` 또는 `blocked`로 전환
- 댓글/신고 오류: 댓글은 `hidden`, 신고는 `in_review`로 전환 후 재검토

## 11. Go / No-Go Criteria

### Go

- Build 성공
- 공개 목록/상세 200
- 관리자 목록/검수 200
- user/admin 권한 분리 확인
- XSS/SSRF 대표 실패 케이스 차단
- DB 백업과 code rollback 경로 확인

### No-Go

- 공개 API 500 발생
- admin controller 우회 가능
- 개인정보 또는 비밀번호 해시 응답 노출
- AI 결과가 검수 없이 공개됨
- DB 백업이 없거나 복원 경로가 확인되지 않음
- route 충돌로 list/detail API가 서로 다른 handler에 잘못 매칭됨

## 12. Post-Deployment Tasks

- [ ] QA 결과 문서를 배포 revision과 함께 보관한다.
- [ ] 초기 관리자 임시 비밀번호를 폐기했는지 확인한다.
- [ ] 관리자 로그에서 배포 직후 오류 이벤트를 확인한다.
- [ ] 운영자가 승인/숨김/반려 절차를 1회 리허설한다.
- [ ] 다음 개선 task에 운영 중 발견된 issue를 TODO로 등록한다.

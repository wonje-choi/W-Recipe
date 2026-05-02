# 인증과 Role 기반 권한 정책

## 목적
프론트엔드 버튼 노출 여부와 무관하게 백엔드에서 guest, user, admin 권한을 강제한다. 일반 로그인과 관리자 로그인은 동일한 인증 흐름을 사용하며, 관리자 여부는 `role` 값으로만 구분한다.

## 진입점

```python
struct = wiz.model("portal/recipe/struct")
user = struct.auth.login(email, password)
struct.auth.logout()
current = struct.auth.current_user()
```

## 비밀번호 해시
- `struct.auth.hash_password(password)`는 `pbkdf2_sha256$iterations$salt$digest` 형식을 사용한다.
- 검증은 `hmac.compare_digest`로 수행한다.
- seed 관리자 계정은 원문 비밀번호가 아니라 `struct.auth.create_admin_password_hash(password)` 결과를 전달해 생성한다.

## 세션 키
로그인 성공 시 season session에 다음 값만 저장한다.

| 키 | 설명 |
| --- | --- |
| `id` | 사용자 ID |
| `email` | 사용자 이메일 |
| `nickname` | 표시명 |
| `role` | `user` 또는 `admin` |
| `status` | 사용자 상태 |

## 권한 컨트롤러

| Controller | 조건 | 사용처 |
| --- | --- | --- |
| `base` | 세션 초기화 | 공개 페이지/API |
| `user` | 로그인 상태 + active 사용자 | 즐겨찾기, 댓글, 수정 요청, 신고 |
| `admin` | 로그인 상태 + admin role | 관리자 CRUD, 승인/반려, 감사 로그 |

`user.py`와 `admin.py`는 `portal/recipe/struct.auth`의 `require_login()`, `require_admin()`을 사용한다.

## 로그인 실패 제한
- 연속 실패 5회부터 15분간 `locked_until`이 설정된다.
- 잠금 중인 계정은 올바른 비밀번호를 입력해도 로그인할 수 없다.
- 성공 로그인 시 `login_failed_count`, `locked_until`이 초기화되고 `last_login_at`이 갱신된다.

## Access Page API

| 함수 | 설명 |
| --- | --- |
| `login` | 이메일/비밀번호로 인증하고 세션 저장 |
| `logout` | 인증 관련 세션 키 삭제 |
| `me` | 현재 로그인 사용자 조회 |

## 권한 매트릭스

| Role | 권한 |
| --- | --- |
| `guest` | 공개 레시피 조회 |
| `user` | 공개 레시피 조회, 즐겨찾기, 댓글, 수정 요청, 신고 |
| `admin` | 공개 레시피 조회, 레시피 관리, 승인/반려, 사용자 관리, 감사 로그 조회 |

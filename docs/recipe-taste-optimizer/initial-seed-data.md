# 초기 데이터와 샘플 레시피 시드

## 목적
개발과 QA에서 빈 화면 없이 공개 목록, 상세, 관리자 검수 흐름을 확인할 수 있도록 최소 샘플 데이터를 제공한다. 시드는 고정 ID와 upsert 방식으로 작성되어 여러 번 실행해도 중복 생성되지 않는다.

## 실행 진입점

```python
seed = wiz.model("portal/recipe/seed")
result = seed.run(admin_email="", admin_password_hash="")
```

`admin_email`과 `admin_password_hash`를 비워 두면 관리자 계정은 생성하지 않고 레시피/데모 사용자/AI 검수 샘플만 준비한다.

## 기본 카테고리
- 일반
- 저염
- 이유식
- 다이어트
- 고단백
- 반찬
- 국/찌개
- 죽/미음

## 기본 태그
- 저염
- 이유식
- 고단백
- 다이어트
- 간단요리
- 부드러운 식감

## 샘플 데이터

| 구분 | ID | 상태 | 목적 |
| --- | --- | --- | --- |
| Dish | `dish_low_sodium_soup` | `approved` | 공개 목록과 저염 필터 확인 |
| Version | `ver_soup_original` | `approved` | 공개 상세와 버전 조회 확인 |
| Version | `ver_soup_ai_pending` | `pending_review` | AI 개량 버전이 공개되지 않는지 확인 |
| AI Modification | `ai_low_sodium_pending` | `pending_review` | 관리자 검수 대기 목록 확인 |
| Dish | `dish_baby_porridge` | `approved` | 이유식 안전 표시 확인 |
| Version | `ver_baby_porridge` | `approved` | 이유식 상세 데이터 확인 |
| Dish | `dish_tofu_salad` | `approved` | 고단백/다이어트 필터 확인 |
| Version | `ver_tofu_salad` | `approved` | 간단요리 상세 데이터 확인 |

## 관리자 계정 생성 절차
1. `FN-0012` 인증 구현 후 프로젝트의 안전한 해시 함수로 초기 비밀번호 해시를 생성한다.
2. 관리자 전용 초기화 API 또는 콘솔에서 `wiz.model("portal/recipe/seed").run(admin_email, admin_password_hash)`를 1회 실행한다.
3. 초기 로그인 후 운영자는 즉시 비밀번호를 변경한다.
4. 원문 비밀번호와 해시 값은 코드, devlog, 관리자 감사 로그에 남기지 않는다.

## QA 체크
- 공개 목록에는 `approved` 상태의 Dish/Version만 노출되어야 한다.
- `ver_soup_ai_pending`과 `ai_low_sodium_pending`은 관리자 검수 화면에서만 보여야 한다.
- 카테고리/태그 필터는 기본 상수의 값을 사용한다.

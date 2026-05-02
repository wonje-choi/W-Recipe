# 공통 레이아웃과 로그인 모달

`layout.recipe`는 Recipe Taste Optimizer 공개 화면에서 사용할 공통 레이아웃이다. 이후 메인, 레시피 목록, 상세, 저염식, 이유식, 마이페이지 화면은 `app.json`의 `layout` 값을 `layout.recipe`로 지정해 사용한다.

## 구성

- 상단 내비게이션: 메인페이지, 레시피, 저염레시피, 이유식레시피, 마이페이지
- 모바일 내비게이션: 햄버거 버튼과 슬라이드 패널
- 로그인 모달: 일반 로그인, 관리자 로그인 탭
- 로그인 상태 표시: 닉네임 또는 이메일과 로그아웃 버튼
- admin role: `Admin Dashboard` 버튼 노출
- 로딩/공통 모달: `wiz-portal-season-modal`, `wiz-portal-season-loading-season`

## 인증 API

`layout.recipe/api.py`는 레이아웃 자체에서 호출하는 함수형 API를 제공한다.

| 함수 | 설명 |
| --- | --- |
| `me()` | 현재 세션 사용자 조회, guest는 `user: null` 반환 |
| `login()` | 이메일/비밀번호 로그인 |
| `logout()` | 현재 세션 로그아웃 |

## 사용 예시

```json
{
  "mode": "page",
  "id": "page.recipe.home",
  "title": "/",
  "namespace": "recipe.home",
  "viewuri": "/",
  "controller": "base",
  "layout": "layout.recipe"
}
```

마이페이지처럼 로그인 필수 화면은 `controller`를 `user`로 지정한다. 내비게이션 표시 여부는 UI 편의 기능일 뿐이며, 최종 보안 기준은 각 API와 Page controller다.

## 개인정보와 role 노출

- 로그인 모달은 세션 사용자 정보 중 `id`, `email`, `nickname`, `role`, `status`만 사용한다.
- admin 전용 버튼은 `user.role === 'admin'`일 때만 노출한다.
- 비로그인 사용자는 공개 메뉴만 볼 수 있고, 마이페이지 메뉴는 숨긴다.

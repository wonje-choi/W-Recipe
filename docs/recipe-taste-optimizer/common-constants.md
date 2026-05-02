# Recipe Taste Optimizer Common Constants

- **작성일**: 2026-05-01
- **작업 ID**: FN-20260501-0003
- **목적**: 백엔드 모델, API, 프론트엔드 필터 UI에서 공통으로 사용할 상태값과 정책 상수를 확정한다.

## 1. Canonical Value 원칙

DB/API에서 저장하고 주고받는 값은 lowercase snake_case를 사용한다. 화면 표시에는 영어/한국어 label을 사용한다.

예: `pending_review`를 저장하고, 화면에는 `Pending Review` 또는 `검수 대기`로 표시한다.

이유:

- 공백과 대소문자 차이로 인한 필터 오류를 줄인다.
- DB 인덱스와 API 파라미터를 단순하게 유지한다.
- 프론트엔드 표시 문구 변경이 DB 마이그레이션으로 이어지지 않는다.

## 2. 상수 파일 위치

| 계층 | 파일 | 사용 방식 |
|---|---|---|
| Backend | `src/portal/recipe/model/constants.py` | `wiz.model("portal/recipe/constants")` |
| Frontend | `src/portal/recipe/libs/constants.ts` | `@wiz/libs/portal/recipe/constants` |
| Package | `src/portal/recipe/portal.json` | `use_model`, `use_libs` 활성화 |

## 3. User Role

| Code | Display | 설명 |
|---|---|---|
| `guest` | Guest | 비로그인 사용자. 공개 조회만 가능 |
| `user` | User | 일반 로그인 사용자. 참여 기능 가능 |
| `admin` | Admin | 관리자. 관리자 API 접근 가능 |

## 4. User Status

| Code | Display | 설명 |
|---|---|---|
| `active` | Active | 정상 계정 |
| `suspended` | Suspended | 일시 정지 계정 |
| `deleted` | Deleted | 탈퇴 또는 비활성 계정 |
| `pending` | Pending | 인증 또는 승인 대기 계정 |

## 5. Recipe Status

| Code | Display | 공개 여부 | 설명 |
|---|---|---:|---|
| `draft` | Draft | 비공개 | 관리자가 작성 중 |
| `crawled` | Crawled | 비공개 | 외부 자료 수집 완료 |
| `ai_parsed` | AI Parsed | 비공개 | AI 요약/정리 완료 |
| `ai_modified` | AI Modified | 비공개 | AI 개량 완료 |
| `pending_review` | Pending Review | 비공개 | 관리자 검수 대기 |
| `approved` | Approved | 공개 | 관리자 승인 완료 |
| `rejected` | Rejected | 비공개 | 반려 |
| `hidden` | Hidden | 비공개 | 운영상 숨김 |

공개 화면의 기본 조회 조건은 `status == approved`로 고정한다.

## 6. AI Processing Status

| Code | Display | 설명 |
|---|---|---|
| `queued` | Queued | 처리 대기 |
| `processing` | Processing | 처리 중 |
| `pending_review` | Pending Review | 생성 완료 후 관리자 검수 대기 |
| `approved` | Approved | 관리자 승인 |
| `rejected` | Rejected | 관리자 반려 |
| `failed` | Failed | 처리 실패 |

AI 결과는 `pending_review` 상태로 저장하고, 승인 전 공개하지 않는다.

## 7. Source Type

| Code | Display | 설명 |
|---|---|---|
| `youtube` | YouTube | 유튜브 영상/채널 기반 자료 |
| `blog` | Blog | 블로그 기반 자료 |
| `web` | Web | 일반 웹문서 기반 자료 |
| `direct` | Direct | 관리자 또는 사용자가 직접 입력한 텍스트 |
| `ai_modified` | AI Modified | AI가 기존 레시피를 개량한 버전 |

## 8. Comment Status

| Code | Display | 설명 |
|---|---|---|
| `visible` | Visible | 공개 댓글 |
| `hidden` | Hidden | 관리자 숨김 댓글 |
| `deleted` | Deleted | 삭제 처리 댓글 |
| `reported` | Reported | 신고 접수 댓글 |

## 9. Edit Request Status

| Code | Display | 설명 |
|---|---|---|
| `open` | Open | 접수됨 |
| `in_review` | In Review | 검토 중 |
| `resolved` | Resolved | 처리 완료 |
| `rejected` | Rejected | 반려 |

## 10. Report Status

| Code | Display | 설명 |
|---|---|---|
| `open` | Open | 신고 접수 |
| `in_review` | In Review | 관리자 검토 중 |
| `actioned` | Actioned | 조치 완료 |
| `rejected` | Rejected | 신고 반려 |

## 11. Crawling Status

| Code | Display | 설명 |
|---|---|---|
| `pending` | Pending | 수집 대기 |
| `allowed` | Allowed | 수집 가능 확인 |
| `blocked` | Blocked | robots.txt/약관/차단 도메인 등으로 수집 제한 |
| `collected` | Collected | 수집 완료 |
| `summarized` | Summarized | 요약 완료 |
| `failed` | Failed | 수집 실패 |
| `expired` | Expired | 링크 만료 또는 접근 불가 |

## 12. AI Purpose

| Code | 설명 |
|---|---|
| `tastier` | 더 맛있게 |
| `low_sodium` | 저염식으로 |
| `baby_food` | 이유식으로 |
| `diet` | 다이어트식으로 |
| `high_protein` | 고단백식으로 |
| `shorter_time` | 조리시간 단축 |
| `simpler_ingredients` | 재료 단순화 |
| `softer_texture` | 부드러운 식감 |

## 13. Diet Type

| Code | 설명 |
|---|---|
| `low_sodium` | 저염 |
| `baby_food` | 이유식 |
| `diet` | 다이어트 |
| `high_protein` | 고단백 |
| `vegetarian` | 채식 |
| `low_sugar` | 당 조절 |
| `soft_texture` | 부드러운 식감 |
| `quick_cook` | 간단 조리 |

## 14. Recipe Sort

| Code | 설명 |
|---|---|
| `view_count` | 조회수순 |
| `latest` | 최신순 |
| `popular` | 인기순 |
| `difficulty` | 난이도순 |
| `cooking_time` | 조리시간순 |
| `ai_modified` | AI 개량순 |

## 15. 정책 상수

| 상수 | 값 | 설명 |
|---|---|---|
| `PUBLIC_RECIPE_STATUS` | `approved` | 공개 화면에서 조회 가능한 레시피 상태 |
| `REVIEW_REQUIRED_STATUSES` | `crawled`, `ai_parsed`, `ai_modified`, `pending_review` | 관리자 검수 대상 상태 |
| `DEFAULT_PAGE` | `1` | 기본 페이지 번호 |
| `DEFAULT_DUMP` | `20` | 기본 페이지 크기 |
| `MAX_DUMP` | `100` | 최대 페이지 크기 |
| `SENSITIVE_PROFILE_FIELDS` | allergies 등 | 로그/관리자 화면에서 마스킹해야 할 개인화 필드 |

## 16. 완료 판정

이 문서는 FN-20260501-0003의 완료 기준을 충족한다.

- User role을 정의했다.
- Recipe status를 정의했다.
- AI status를 정의했다.
- Source type을 정의했다.
- Edit request, report, comment status를 정의했다.
- 백엔드와 프론트엔드가 사용할 공통 상수 파일을 생성했다.

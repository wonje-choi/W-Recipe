# 레시피 레이아웃 한국어/영어 전환 구현

- **ID**: 053
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
공통 레이아웃 헤더에 KO/EN 언어 전환 버튼을 추가하고, nav와 로그인 관련 공통 문자열을 JSON 사전 기반으로 표시하도록 변경했다.
언어 전환 시 현재 URL에 `lang` 쿼리 파라미터를 유지하고 즉시 레이아웃 텍스트를 갱신하며, 미정의 키는 한국어 또는 원문 fallback으로 처리한다.

## 변경 파일 목록
- `src/assets/lang/ko.json`: 공통 UI 한국어 문자열 정의
- `src/assets/lang/en.json`: 공통 UI 영어 문자열 정의
- `src/app/layout.recipe/view.ts`: 언어 감지, JSON 로드, `t(key)` fallback, URL 유지 전환 로직 추가
- `src/app/layout.recipe/view.pug`: nav/login 문자열 키 참조와 KO/EN 토글 추가

## 검증
- JSON 파싱으로 `ko.json`, `en.json` 형식 확인
- `pug.compileFile`로 레이아웃 템플릿 문법 확인
- 미정의 키가 `undefined` 대신 한국어/원문 fallback으로 표시되는 코드 경로 확인

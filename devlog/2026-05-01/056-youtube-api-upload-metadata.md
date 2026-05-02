# YouTube API 설정과 업로드 메타데이터 미리보기 구현

- **ID**: 056
- **날짜**: 2026-05-01
- **유형**: 기능 추가

## 작업 요약
관리자 AI 설정에 YouTube Data API v3 키 저장 UI를 추가하고, 레시피 편집 폼에서 영상 제목·설명·태그·업로드 엔드포인트를 미리 확인할 수 있게 했다.
YouTube 키는 `config/youtube_settings.json`에 저장하며, 관리자 로그에는 키 원문이 남지 않도록 마스킹된 상태만 기록한다.

## 변경 파일 목록
- `src/portal/recipe/model/struct/youtube.py`: YouTube 설정 로드/저장과 업로드 메타데이터 생성 로직 추가
- `src/portal/recipe/model/struct.py`: `struct.youtube` 연결 추가
- `src/app/page.admin.ai/api.py`: YouTube API Key 설정 조회/저장 API 추가
- `src/app/page.admin.ai/view.ts`, `view.pug`: 설정 탭과 YouTube API Key 입력 UI 추가
- `src/app/page.admin.recipes/api.py`: 레시피별 YouTube 업로드 메타데이터 생성 API 추가
- `src/app/page.admin.recipes/view.ts`, `view.pug`: 레시피 편집 폼의 유튜브 업로드 준비 미리보기 추가
- `src/app/layout.recipe/view.ts`, `src/assets/lang/ko.json`, `src/assets/lang/en.json`: 관리자 설정 nav 항목과 번역 키 추가

## 검증
- `python -m py_compile`로 변경 Python 파일 문법 확인
- `pug.compileFile`로 AI 관리, 레시피 관리, 레이아웃 템플릿 문법 확인
- `ko.json`, `en.json` JSON 파싱 확인
- YouTube API Key 원문이 관리자 로그에 기록되지 않는 코드 경로 확인

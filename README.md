# Luna Fitness App

Streamlit 앱으로 운동 루틴을 기록하고 Google Sheets에 자동 저장합니다.

## 보안 방식
- 최초 1회 Google API 키를 붙여넣으면 자동 암호화 저장
- 이후 실행 시 자동 연동

## 사용 방법
1. `streamlit run app.py`
2. Google 서비스 계정 키를 붙여넣기
3. 인증되면 시트와 자동 연결됨
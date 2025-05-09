# Luna Fitness App

Streamlit 웹앱으로 개인/제자 운동 루틴을 Google Sheets에 기록하고 통계로 확인합니다.

## 특징
- Google 서비스 계정 키(JSON) **1회 업로드** → 자동 암호화 → 이후 자동 인증
- 운동 루틴 입력(요일·세트·횟수·휴식)
- 완료 체크·코멘트 저장
- 주간 완료율 그래프

## 사용 방법 요약
1. Google Cloud에서 서비스 계정 키(JSON) 발급
2. 로컬에서 `encrypt_credentials.py` 실행 → `encrypted_key.json` `encryption_key.key` 생성
3. `app.py`, 두 키 파일, `requirements.txt`를 GitHub 저장소에 업로드
4. Streamlit Cloud에서 배포 (`app.py` 지정)
5. 첫 실행 후 Google Sheet 문서(`운동기록_템플릿`)에 서비스 계정 이메일 편집 권한 부여

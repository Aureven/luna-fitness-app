import streamlit as st
import os
import json
from cryptography.fernet import Fernet
import gspread
from google.oauth2.service_account import Credentials

# ===== 설정 =====
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
KEY_FILE = "encryption_key.key"
ENC_FILE = "encrypted_key.json"

def decrypt_credentials():
    if os.path.exists(KEY_FILE) and os.path.exists(ENC_FILE):
        with open(KEY_FILE, "rb") as kf:
            key = kf.read()
        fernet = Fernet(key)
        with open(ENC_FILE, "rb") as ef:
            encrypted_data = ef.read()
        decrypted = fernet.decrypt(encrypted_data)
        return json.loads(decrypted)
    return None

def save_encrypted_credentials(json_text):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as kf:
        kf.write(key)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json_text.encode())
    with open(ENC_FILE, "wb") as ef:
        ef.write(encrypted)

def authorize_gspread(creds_dict):
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

# ===== Streamlit 앱 시작 =====
st.set_page_config(page_title="Luna Fitness App", layout="centered")
st.title("🏋️ 루나 피트니스 루틴")

# 🔐 인증 여부 확인
creds_dict = decrypt_credentials()
if creds_dict:
    client = authorize_gspread(creds_dict)
    st.success("✅ 인증 성공 – 자동 연동 중입니다.")

    # 예시: 시트 열기 및 표시
    try:
        sheet = client.open("운동기록_템플릿").sheet1
        st.write("### 📄 운동기록 샘플")
        st.dataframe(sheet.get_all_records())
    except Exception as e:
        st.error(f"시트 접근 실패: {e}")

else:
    st.warning("🔐 관리자 인증이 필요합니다. 아래에 Google API 키를 붙여넣으세요.")
    json_input = st.text_area("Google 서비스 계정 JSON 전체 붙여넣기", height=300)
    if st.button("🔒 저장 및 연동"):
        try:
            creds_dict = json.loads(json_input)
            save_encrypted_credentials(json_input)
            st.success("🎉 키 저장 및 인증 성공! 앱을 새로고침해주세요.")
        except Exception as e:
            st.error(f"인증 실패: {e}")

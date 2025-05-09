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
SHEET_NAME = "운동기록_템플릿"

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

def save_encrypted_credentials_from_file(uploaded_file):
    try:
        json_bytes = uploaded_file.read()
        creds_dict = json.loads(json_bytes.decode("utf-8"))
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as kf:
            kf.write(key)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json_bytes)
        with open(ENC_FILE, "wb") as ef:
            ef.write(encrypted)
        return creds_dict
    except Exception as e:
        raise ValueError(f"❗ JSON 처리 오류: {e}")

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
    try:
        client = authorize_gspread(creds_dict)
        st.success("✅ 인증 성공 – Google Sheets에 자동 연결되었습니다.")

        try:
            sheet = client.open(SHEET_NAME).sheet1
            st.write("### 📄 운동기록 샘플")
            st.dataframe(sheet.get_all_records())
        except gspread.SpreadsheetNotFound:
            st.error(f"❗ 구글 시트 '{SHEET_NAME}' 를 찾을 수 없습니다. Google Drive에서 해당 이름으로 시트를 만들고, 서비스 계정 이메일에게 '편집자 권한'을 주세요.")
        except Exception as e:
            st.error(f"❗ 시트 접근 중 오류 발생: {e}")

    except Exception as e:
        st.error(f"❗ 인증 실패: {e}")
        st.info("👇 아래에서 JSON 키 파일을 다시 업로드할 수 있어요.")
        creds_dict = None  # fallback to file input

if not creds_dict:
    st.warning("🔐 관리자 인증이 필요합니다. 아래에 Google API 키(JSON 파일)를 업로드하세요.")
    uploaded_file = st.file_uploader("📁 JSON 파일 업로드", type=["json"])
    if uploaded_file is not None:
        try:
            creds_dict = save_encrypted_credentials_from_file(uploaded_file)
            st.success("🎉 키 저장 및 인증 성공! 앱을 새로고침해주세요.")
        except Exception as e:
            st.error(str(e))

import streamlit as st
import os, json, datetime as dt
from cryptography.fernet import Fernet
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
KEY_FILE = "encryption_key.key"
ENC_FILE = "encrypted_key.json"
SHEET_NAME = "운동기록_템플릿"

st.set_page_config(page_title="Luna Fitness (Debug)", layout="centered")
st.title("🏋️ Luna Fitness Routine – 디버그 버전")

try:
    if os.path.exists(KEY_FILE) and os.path.exists(ENC_FILE):
        with open(KEY_FILE, "rb") as kf:
            key = kf.read()
        fernet = Fernet(key)
        with open(ENC_FILE, "rb") as ef:
            data = fernet.decrypt(ef.read())
        creds_dict = json.loads(data)
        st.success("🔐 인증키 복호화 성공")
    else:
        st.warning("🔐 인증 키가 없습니다. JSON 파일 업로드 필요.")
        uploaded = st.file_uploader("credentials.json 업로드", type="json")
        if uploaded and st.button("저장"):
            try:
                raw = uploaded.read()
                creds_dict = json.loads(raw)
                key = Fernet.generate_key()
                with open(KEY_FILE, "wb") as kf:
                    kf.write(key)
                with open(ENC_FILE, "wb") as ef:
                    ef.write(Fernet(key).encrypt(raw))
                st.success("키 저장 및 암호화 완료. 새로고침해주세요.")
            except Exception as e:
                st.error(f"업로드 실패: {e}")
        st.stop()
except Exception as e:
    st.error(f"🔑 인증 처리 중 오류: {e}")
    st.stop()

try:
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    st.success("✅ Google 인증 완료")
except Exception as e:
    st.error(f"❌ Google 인증 실패: {e}")
    st.stop()

try:
    sheet = client.open(SHEET_NAME).sheet1
    st.success(f"📄 시트 '{SHEET_NAME}' 열기 성공")
except Exception as e:
    st.error(f"❌ 시트 열기 실패: {e}")
    st.stop()

st.header("📝 루틴 입력")
with st.form("routine"):
    day = st.selectbox("요일", ["월","화","수","목","금","토","일"])
    exercise = st.text_input("운동명")
    sets = st.number_input("세트", 1, 20, 3)
    reps = st.number_input("횟수", 1, 100, 15)
    rest = st.number_input("휴식(초)", 10, 300, 60)
    submitted = st.form_submit_button("저장")
    if submitted:
        try:
            sheet.append_row([
                dt.date.today().isoformat(), day, exercise,
                int(sets), int(reps), int(rest), "", ""
            ])
            st.success("루틴 저장 완료!")
        except Exception as e:
            st.error(f"루틴 저장 실패: {e}")

st.header("📋 오늘 루틴")
try:
    records = sheet.get_all_records()
    today = dt.date.today().isoformat()
    today_rows = [r for r in records if r["날짜"] == today]
    if not today_rows:
        st.info("오늘 저장된 루틴이 없습니다.")
    else:
        for idx, row in enumerate(today_rows, start=2):
            st.subheader(f"{row['요일']} – {row['운동']}")
            done = st.checkbox("완료", key=f"done{idx}")
            comment = st.text_input("코멘트", key=f"cmt{idx}")
            if st.button("업데이트", key=f"up{idx}"):
                try:
                    sheet.update_cell(idx, 7, "완료" if done else "")
                    sheet.update_cell(idx, 8, comment)
                    st.success("업데이트 완료!")
                except Exception as e:
                    st.error(f"업데이트 실패: {e}")
except Exception as e:
    st.error(f"루틴 조회 실패: {e}")

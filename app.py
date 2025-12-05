# app_landing.py (IMD Sales Bot - The Inception)
import streamlit as st
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------
# 0. 시스템 설정 & 스타일링 (Cyber-Noir)
# ---------------------------------------
st.set_page_config(page_title="IMD AI 도입 상담", page_icon="🧠", layout="centered")

# CSS: 압도적인 몰입감 (검정 배경 + 형광 텍스트)
custom_css = """
<style>
/* 전체 스타일 */
.stApp { background-color: #000000; font-family: 'Pretendard', sans-serif; color: #ffffff; }
h1, h2, h3 { color: #00E5FF !important; font-weight: 800; }
p, div, label, span { color: #eeeeee !important; font-size: 16px; }

/* 채팅창 스타일 */
.chat-container {
    max-width: 700px; margin: auto; padding-bottom: 100px;
}
.chat-bubble-ai {
    background-color: #1a1a1a; color: #fff !important; padding: 15px 20px;
    border-radius: 20px 20px 20px 5px; margin-bottom: 15px; width: fit-content; max-width: 85%;
    font-size: 16px; line-height: 1.5; border-left: 3px solid #00E5FF;
    animation: fadeIn 0.5s ease;
}
.chat-bubble-user {
    background-color: #00E5FF; color: #000 !important; padding: 12px 20px;
    border-radius: 20px 20px 5px 20px; margin-bottom: 15px; margin-left: auto;
    width: fit-content; max-width: 80%; font-size: 16px; font-weight: bold;
    animation: slideIn 0.3s ease; box-shadow: 0 4px 10px rgba(0, 229, 255, 0.3);
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

/* 버튼 스타일 (선택지) */
.stButton>button {
    width: 100%; background-color: #000; color: #00E5FF !important;
    border: 1px solid #00E5FF; padding: 15px; font-size: 16px; border-radius: 30px; font-weight: bold;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #00E5FF; color: #000 !important; box-shadow: 0 0 15px rgba(0, 229, 255, 0.5); transform: scale(1.02);
}

/* 입력폼 스타일 */
input[type="text"] { background-color: #222 !important; color: white !important; border: 1px solid #444 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 1. 리드 수집 로직
# ---------------------------------------
def save_lead(data):
    try:
        creds_dict = st.secrets["gcp_service_account"].to_dict()
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open(st.secrets.get("SHEET_NAME", "IMD_DB")).sheet1 
        row = [datetime.now().isoformat(), data['type'], data['status'], data['name'], data['contact'], "IMD_SALES_BOT"]
        sheet.append_row(row)
        return True
    except: return False

# ---------------------------------------
# 2. 대화 상태 관리
# ---------------------------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "text": "반갑습니다. <b>IMD 수석 아키텍트 AI</b>입니다.<br>대표님, 솔직히 말씀드리죠.<br><br>지금 <b>마케팅 비용 대비 효율(ROAS)</b>, 만족하시나요?"}
    ]
if 'step' not in st.session_state: st.session_state.step = 0
if 'user_type' not in st.session_state: st.session_state.user_type = ""

# ---------------------------------------
# 3. 화면 렌더링 (채팅창)
# ---------------------------------------
st.title("IMD AI Business Diagnosis")

# 채팅 내역 표시
for chat in st.session_state.chat_history:
    role_class = "chat-bubble-ai" if chat['role'] == "ai" else "chat-bubble-user"
    st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)

# ---------------------------------------
# 4. 인터랙티브 로직 (The Sales Script)
# ---------------------------------------
placeholder = st.empty()

# Step 0: 첫 질문 (효율 만족도)
if st.session_state.step == 0:
    with placeholder.container():
        col1, col2 = st.columns(2)
        if col1.button("아니요, 불만족스럽습니다 📉"):
            st.session_state.chat_history.append({"role": "user", "text": "아니요, 돈만 쓰고 효과가 없어서 답답합니다."})
            st.session_state.step = 1
            st.rerun()
        if col2.button("그럭저럭 괜찮습니다 😐"):
            st.session_state.chat_history.append({"role": "user", "text": "나쁘진 않은데, 더 올리고 싶긴 해요."})
            st.session_state.step = 1
            st.rerun()

# Step 1: 업종 확인
elif st.session_state.step == 1:
    time.sleep(0.5)
    if len(st.session_state.chat_history) < 3:
        st.session_state.chat_history.append({"role": "ai", "text": "대부분의 대표님들이 같은 고민을 하십니다. 광고로 사람을 데려오는 건 쉬워졌지만, <b>'결제'하게 만드는 건 훨씬 어려워졌기 때문이죠.</b><br><br>정확한 진단을 위해, 현재 운영 중인 업종이 어떻게 되시나요?"})
        st.rerun()
    
    with placeholder.container():
        col1, col2 = st.columns(2)
        if col1.button("🏥 병원/의원"):
            st.session_state.user_type = "병원"
            st.session_state.chat_history.append({"role": "user", "text": "병원(성형/피부/한의원)을 운영 중입니다."})
            st.session_state.step = 2
            st.rerun()
        if col2.button("🛍️ 쇼핑몰/커머스"):
            st.session_state.user_type = "쇼핑몰"
            st.session_state.chat_history.append({"role": "user", "text": "쇼핑몰/브랜드를 운영 중입니다."})
            st.session_state.step = 2
            st.rerun()

# Step 2: 페인 포인트 타격 (The Pain)
elif st.session_state.step == 2:
    time.sleep(0.5)
    if len(st.session_state.chat_history) < 5:
        if st.session_state.user_type == "병원":
            msg = "병원 마케팅의 핵심은 <b>'상담 전환'</b>입니다.<br>그런데 환자가 밤 10시에 '가격 얼마예요?' 카톡 남기면 누가 답장하나요?<br>직원들은 퇴근했고, 답변이 늦으면 환자는 다른 병원으로 가버립니다."
        else:
            msg = "쇼핑몰의 핵심은 <b>'구매 전환'</b>입니다.<br>고객 100명이 들어오면 98명은 그냥 나갑니다(이탈률 98%).<br>왜일까요? 상품이 너무 많아서 뭘 살지 모르기 때문입니다."
        
        st.session_state.chat_history.append({"role": "ai", "text": msg})
        st.rerun()

    with placeholder.container():
        if st.button("맞아요, 그게 제일 문제입니다 🤦‍♂️"):
            st.session_state.chat_history.append({"role": "user", "text": "맞아요. 그 놓치는 고객들 때문에 매출이 정체되어 있습니다."})
            st.session_state.step = 3
            st.rerun()

# Step 3: 솔루션 증명 (The Inception)
elif st.session_state.step == 3:
    time.sleep(0.5)
    if len(st.session_state.chat_history) < 7:
        st.session_state.chat_history.append({"role": "ai", "text": "<b>지금 저를 보세요.</b> 👀<br><br>저는 사람이 아니라 AI 봇입니다. 하지만 대표님은 저와의 대화에 몰입해서 여기까지 버튼을 누르며 따라오셨습니다.<br><br>만약 제가 대표님의 홈페이지에 심어져 있다면 어떨까요?<br><b>밤새도록 고객을 붙잡고, 설득하고, 상담 예약을 받아낼 겁니다.</b>"})
        st.rerun()

    with placeholder.container():
        if st.button("와... 진짜 그렇네요? 😲"):
            st.session_state.chat_history.append({"role": "user", "text": "듣고 보니 그렇네요. 제가 봇한테 설득당하고 있었군요."})
            st.session_state.step = 4
            st.rerun()

# Step 4: 전환 제안 (The Close)
elif st.session_state.step == 4:
    time.sleep(0.5)
    if len(st.session_state.chat_history) < 9:
        if st.session_state.user_type == "병원":
            benefit = "<b>야간/주말 예약 건수 30% 증가</b>"
        else:
            benefit = "<b>구매 전환율 1.5배 상승</b>"
            
        st.session_state.chat_history.append({"role": "ai", "text": f"바로 그겁니다. 😎<br>IMD 아키텍처 그룹은 단순한 챗봇이 아니라, <b>고객을 설득하는 세일즈 AI</b>를 설계합니다.<br><br>이 시스템을 도입하면 {benefit}를 보장합니다.<br>우리 병원/쇼핑몰에 딱 맞는 <b>'AI 설계도'</b>를 무료로 받아보시겠습니까?"})
        st.rerun()

    with placeholder.container():
        with st.form("lead_form"):
            st.markdown("### 🚀 무료 설계도 및 견적 신청")
            name = st.text_input("성함 / 직함")
            contact = st.text_input("연락처 (직통)")
            submit = st.form_submit_button("설계도 받기 (선착순 마감)")
            
            if submit:
                if name and contact:
                    data = {
                        "type": st.session_state.user_type,
                        "status": "Inception Complete",
                        "name": name,
                        "contact": contact
                    }
                    save_lead(data)
                    st.session_state.chat_history.append({"role": "ai", "text": f"감사합니다, {name}님! <br>담당 아키텍트가 24시간 내로 분석하여 <b>{contact}</b> 번호로 연락드리겠습니다.<br>이제 매출 걱정은 덜으셔도 됩니다."})
                    st.session_state.step = 5
                    st.rerun()
                else:
                    st.error("연락처를 입력해주세요.")

# Step 5: 완료 (End)
elif st.session_state.step == 5:
    st.balloons()
    if st.button("처음으로 돌아가기"):
        st.session_state.clear()
        st.rerun()

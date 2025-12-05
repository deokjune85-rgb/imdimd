# app_landing.py (Reset Security - Showcase & Sniper Edition)
import streamlit as st
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------
# 0. 시스템 설정 & 스타일링 (Cyber-Luxury)
# ---------------------------------------
st.set_page_config(page_title="리셋시큐리티 - 비즈니스 진단", page_icon="⚡", layout="centered")

# CSS: 압도적인 몰입감 & 가독성 (다크 모드 강제)
custom_css = """
<style>
/* 전체 스타일 */
.stApp { background-color: #000000; font-family: 'Pretendard', sans-serif; color: #ffffff; }
h1, h2, h3 { color: #D4AF37 !important; font-weight: 800; }
p, div, label, span { color: #eeeeee !important; }

/* 채팅창 스타일 */
.chat-container {
    background-color: #111; border-radius: 15px; padding: 20px;
    margin: 20px 0; border: 1px solid #333;
}
.chat-bubble-ai {
    background-color: #222; color: #fff !important; padding: 12px 16px;
    border-radius: 15px 15px 15px 0; margin-bottom: 10px; width: fit-content; max-width: 85%;
    font-size: 15px; border-left: 3px solid #D4AF37;
}
.chat-bubble-user {
    background-color: #D4AF37; color: #000 !important; padding: 12px 16px;
    border-radius: 15px 15px 0 15px; margin-bottom: 10px; margin-left: auto;
    width: fit-content; max-width: 85%; font-size: 15px; font-weight: bold;
}

/* 버튼 스타일 */
.stButton>button {
    width: 100%; background-color: #111; color: #D4AF37 !important;
    border: 1px solid #D4AF37; padding: 15px; font-size: 16px; border-radius: 8px; font-weight: bold;
}
.stButton>button:hover { background-color: #D4AF37; color: #000 !important; border: 1px solid #D4AF37; }

/* 손실 계산기 박스 (심장박동 애니메이션) */
.loss-box {
    background-color: #2a0a0a; border: 2px solid #ff4b4b; padding: 20px;
    border-radius: 10px; text-align: center; margin-top: 20px; animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
}
.loss-value { font-size: 28px; font-weight: 900; color: #ff4b4b !important; margin: 10px 0; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 1. 리드 수집 로직 (Google Sheets)
# ---------------------------------------
def save_lead(data):
    try:
        creds_dict = st.secrets["gcp_service_account"].to_dict()
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        # 시트 이름 확인 (기존에 만든 'IMD_DB' 사용)
        sheet = client.open(st.secrets.get("SHEET_NAME", "IMD_DB")).sheet1 
        
        row = [
            datetime.now().isoformat(), 
            data['industry'], 
            data['pain_point'], 
            data['name'], 
            data['contact'], 
            "RESET_SEC_SHOWCASE"
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        return False

# ---------------------------------------
# 2. 메인 로직
# ---------------------------------------
if 'step' not in st.session_state: st.session_state.step = 1
if 'industry' not in st.session_state: st.session_state.industry = None
if 'pain_point' not in st.session_state: st.session_state.pain_point = ""

# === Step 1: 산업군 선택 (The Trigger) ===
if st.session_state.step == 1:
    st.title("리셋시큐리티 비즈니스 진단")
    st.markdown("<h3 style='text-align: center; color: #ccc !important;'>AI로 당신의 매출 누수를 막아드립니다.</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("👇 현재 운영 중인 업종을 선택하여 시뮬레이션을 시작하세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        # st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=80) 
        if st.button("🏥 병원/의원\n(성형/피부/한방)"):
            st.session_state.industry = "의료"
            st.session_state.step = 2
            st.rerun()
    with col2:
        # st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=80) 
        if st.button("🛍️ 쇼핑몰/브랜드\n(패션/잡화/뷰티)"):
            st.session_state.industry = "쇼핑몰"
            st.session_state.step = 2
            st.rerun()

# === Step 2: 의료 시뮬레이션 (Medical Track) ===
elif st.session_state.step == 2 and st.session_state.industry == "의료":
    st.header("🏥 AI 야간 상담 실장 시연")
    st.markdown("**상황:** 밤 11시, 직원들은 퇴근했고 병원 문은 닫혔습니다. 그때 환자가 문의를 합니다.")
    st.markdown("---")

    if 'med_chat' not in st.session_state:
        st.session_state.med_chat = [{"role": "ai", "text": "안녕하세요! 리셋 성형외과 AI 야간 실장입니다. 🌙<br>진료 마감 후지만 무엇이든 물어보세요! (24시간 대기 중)"}]

    # 채팅 화면
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.med_chat:
        role_class = "chat-bubble-ai" if chat['role'] == "ai" else "chat-bubble-user"
        st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 인터랙티브 버튼
    col1, col2 = st.columns(2)
    if len(st.session_state.med_chat) == 1:
        with col1:
            if st.button("💰 리프팅 가격 얼마예요?"):
                st.session_state.med_chat.append({"role": "user", "text": "요즘 리프팅 시술 얼마인가요?"})
                st.rerun()
        with col2:
            if st.button("📅 내일 예약 가능한가요?"):
                st.session_state.med_chat.append({"role": "user", "text": "내일 오후에 원장님 상담 가능한가요?"})
                st.rerun()
    
    # 답변 로직 (자동 진행)
    if len(st.session_state.med_chat) == 2:
        time.sleep(0.7) # 타이핑 연출
        last_msg = st.session_state.med_chat[-1]['text']
        if "얼마" in last_msg:
            st.session_state.med_chat.append({"role": "ai", "text": "현재 12월 이벤트 진행 중입니다! ✨<br><br>💎 <b>울쎄라 300샷:</b> 99만원<br>💎 <b>인모드 풀페이스:</b> 15만원<br><br>지금 예약하시면 <b>추가 5% 할인</b> 혜택이 적용됩니다. 예약 가능 시간을 확인해 드릴까요?"})
        else:
            st.session_state.med_chat.append({"role": "ai", "text": "잠시만요, 원장님 스케줄 실시간 확인 중... ⏳<br><br>내일(금) <b>오후 2시, 4시 30분</b> 비어있습니다!<br>노쇼 방지를 위해 예약금 입금 시 확정됩니다. 진행해 드릴까요?"})
        st.rerun()

    if len(st.session_state.med_chat) > 2:
        st.success("✅ 확인: 직원이 퇴근한 후에도 AI가 상담부터 예약 확정까지 100% 자동 처리했습니다.")
        st.markdown("---")
        
        # 손실 계산기 (공포 마케팅)
        st.subheader("📉 우리 병원 숨은 손실 계산기")
        missed_calls = st.slider("하루에 놓치는 전화/문의는 대략 몇 통입니까?", 1, 30, 5)
        avg_ticket = st.select_slider("환자 1인당 평균 객단가는?", options=["10만원", "30만원", "50만원", "100만원", "300만원"], value="50만원")
        
        ticket_val = int(avg_ticket.replace("만원","")) * 10000
        monthly_loss = missed_calls * ticket_val * 30 * 0.2 # 전환율 20% 가정
        
        st.markdown(f"""
        <div class="loss-box">
            <div>원장님, 지금 놓치고 있는 월 매출은 최소</div>
            <div class="loss-value">{format(int(monthly_loss), ',')} 원</div>
            <div>입니다. 이 돈을 버리시겠습니까?</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 이 손실 막으러 가기 (솔루션 신청)"):
            st.session_state.pain_point = f"월 {format(int(monthly_loss), ',')}원 손실 예상"
            st.session_state.step = 3
            st.rerun()

# === Step 2: 쇼핑몰 시뮬레이션 (Commerce Track) ===
elif st.session_state.step == 2 and st.session_state.industry == "쇼핑몰":
    st.header("🛍️ AI 퍼스널 쇼퍼 시연")
    st.markdown("**상황:** 고객이 쇼핑몰에 들어왔지만 상품이 너무 많아 **'다음에 사야지'** 하고 나가려 합니다.")
    st.markdown("---")

    if 'shop_chat' not in st.session_state:
        st.session_state.shop_chat = [{"role": "ai", "text": "반가워요! 고객님께 딱 어울리는 옷을 찾아드릴게요. 👗<br>혹시 <b>퍼스널 컬러</b>가 어떻게 되세요?"}]

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in st.session_state.shop_chat:
        role_class = "chat-bubble-ai" if chat['role'] == "ai" else "chat-bubble-user"
        st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if len(st.session_state.shop_chat) == 1:
        with col1:
            if st.button("🧡 웜톤 (Warm)"):
                st.session_state.shop_chat.append({"role": "user", "text": "저는 웜톤이에요!"})
                st.session_state.tone = "웜톤"
                st.rerun()
        with col2:
            if st.button("💙 쿨톤 (Cool)"):
                st.session_state.shop_chat.append({"role": "user", "text": "저는 쿨톤이에요."})
                st.session_state.tone = "쿨톤"
                st.rerun()

    if len(st.session_state.shop_chat) == 2:
        time.sleep(0.7)
        tone = st.session_state.tone
        if tone == "웜톤":
            rec_text = "아하! 웜톤이시군요 🧡<br>그럼 얼굴에 형광등 켜주는 <b>'코랄 베이지 니트'</b>와 <b>'골드 네크리스'</b> 조합 어떠세요?"
            color_code = "#F5DEB3"
        else:
            rec_text = "오! 시크한 쿨톤이시네요 💙<br>고객님껜 <b>'차콜 그레이 코트'</b>에 <b>'실버 이어링'</b> 매칭이 베스트입니다!"
            color_code = "#E0FFFF"
            
        st.session_state.shop_chat.append({"role": "ai", "text": f"{rec_text}<br><br>👇 아래는 고객님 전용 <b>[{tone} 기획전]</b> 상품입니다."})
        st.rerun()

    if len(st.session_state.shop_chat) > 2:
        # 가상 상품 카드 시각화 (Wow Factor)
        color_code = "#F5DEB3" if st.session_state.tone == "웜톤" else "#E0FFFF"
        text_col = "#5c4033" if st.session_state.tone == "웜톤" else "#003366"
        st.markdown(f"""
        <div style="display:flex; gap:10px; justify-content:center; margin-bottom:20px;">
            <div style="background:{color_code}; width:100px; height:120px; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:{text_col}; font-weight:bold; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                <span>추천 A</span><span style='font-size:10px'>39,000원</span>
            </div>
            <div style="background:{color_code}; width:100px; height:120px; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:{text_col}; font-weight:bold; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
                <span>추천 B</span><span style='font-size:10px'>49,000원</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success(f"✅ 확인: 고객의 '{st.session_state.tone}' 취향을 분석하여 맞춤 상품을 제안, 이탈을 막고 구매를 유도했습니다.")
        
        st.markdown("---")
        # 매출 상승 계산기
        st.subheader("📈 내 쇼핑몰 매출 성장 예측")
        current_rev = st.text_input("현재 월 매출을 입력하세요 (숫자만)", value="30000000")
        try:
            curr = int(current_rev)
        except:
            curr = 30000000
        
        extra_rev = curr * 0.15 # 15% 상승 가정
        
        st.markdown(f"""
        <div class="loss-box" style="border-color: #00ff00;">
            <div style="color:#eee !important;">AI 도입 시 예상되는 월 추가 매출</div>
            <div class="loss-value" style="color:#00ff00 !important;">+ {format(int(extra_rev), ',')} 원</div>
            <div style="color:#aaa !important; font-size:12px;">(구매 전환율 15% 상승 기준)</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 내 쇼핑몰에 이 기능 설치하기"):
            st.session_state.pain_point = f"월 매출 +{format(int(extra_rev), ',')}원 상승 목표"
            st.session_state.step = 3
            st.rerun()

# === Step 3: 리드 수집 (The Closing) ===
elif st.session_state.step == 3:
    st.header("⚡ 리셋시큐리티 AI 도입 신청")
    st.write("지금 신청하시면 **업종별 맞춤 봇 설계도(PDF)**와 **설치 견적**을 무료로 보내드립니다.")
    st.warning("⚠️ 현재 문의 폭주로 인해 선착순 5팀만 무료 컨설팅이 진행됩니다.")

    with st.form("lead_form"):
        name = st.text_input("담당자 성함 / 업체명")
        contact = st.text_input("연락처 (필수)")
        req = st.text_area("고민사항 (선택)", placeholder="예: 노쇼가 너무 많아요, 상세페이지 이탈이 심해요")
        
        submit = st.form_submit_button("무료 컨설팅 신청하기")
        
        if submit:
            if name and contact:
                data = {
                    "industry": st.session_state.industry,
                    "pain_point": f"{st.session_state.pain_point} / {req}",
                    "name": name,
                    "contact": contact
                }
                save_lead(data)
                st.success("신청이 완료되었습니다! 담당 아키텍트가 24시간 내로 분석하여 연락드립니다.")
                st.balloons()
            else:
                st.error("연락처를 입력해주셔야 상담이 가능합니다.")

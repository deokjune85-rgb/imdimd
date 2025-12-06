# app.py (Mobile Optimized - Stable Engine)
import streamlit as st
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# 0. 시스템 설정 & 모바일 CSS (디자인 100% 유지)
# ============================================
st.set_page_config(page_title="AI 예진 시뮬레이터", page_icon="📱", layout="centered")

custom_css = """
<style>
/* 전체 다크 테마 */
.stApp { background-color: #121212; font-family: 'Pretendard', sans-serif; color: white; }

/* 1. 환자용 UI (밝은 카드 스타일) */
.patient-card {
    background-color: #ffffff; color: #333; padding: 20px;
    border-radius: 15px; margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    border-left: 6px solid #2E8B57; /* Medical Green */
    animation: slideIn 0.3s ease;
}
.patient-label { font-size: 12px; font-weight: bold; color: #888; text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 5px; }
.patient-text { font-size: 17px; font-weight: 700; color: #111; line-height: 1.4; }

/* 2. AI 원장님용 로그 (어두운 터미널 스타일) */
.admin-log {
    background-color: #000; color: #00E5FF; padding: 15px;
    border-radius: 10px; margin-bottom: 25px;
    font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5;
    border: 1px solid #333;
    animation: fadeIn 0.5s ease-in-out;
}
.log-header { color: #D4AF37; font-weight: bold; font-size: 12px; margin-bottom: 5px; display: block; border-bottom: 1px solid #333; padding-bottom: 5px;}
.log-highlight { color: #ffff00; font-weight: bold; text-decoration: underline; }

/* 3. 버튼 커스텀 */
.stButton>button {
    width: 100%; border-radius: 12px; height: 55px; font-size: 16px; font-weight: bold;
    background-color: #f0f2f6; color: #333; border: none;
    transition: 0.2s;
}
.stButton>button:hover { background-color: #e0e2e6; }
.stButton>button:active { background-color: #2E8B57; color: white; }

/* 애니메이션 */
@keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

/* 입력창 숨김 */
.stChatInput { display: none; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ============================================
# 1. 상태 관리 (히스토리 보존 핵심)
# ============================================
if 'history' not in st.session_state:
    # 초기 안내 멘트
    st.session_state.history = [
        {"type": "log", "header": "SYSTEM ONLINE", "text": "원장님, 환자가 '비싸요'라고 하는 진짜 이유는 돈이 없어서가 아닙니다.<br>내 몸이 그만큼 심각하다는 걸 <b>모르기 때문</b>입니다.<br><br>제가 질문 몇 개로 환자의 <b>'숨겨진 병리'</b>를 찾아내고, 스스로 지갑을 열게 만드는 과정을 보여드리겠습니다."},
        {"type": "patient", "label": "STEP 0. 시뮬레이션 시작", "text": "지금부터 원장님은 잠시 '만성 피로 환자' 역할을 해봐 주십시오.<br>편한 말투로 현재 상태를 한 줄만 말씀해 주세요."}
    ]
if 'step' not in st.session_state: 
    st.session_state.step = 0

# ============================================
# 2. 리드 수집 로직
# ============================================
def save_lead(data):
    try:
        creds_dict = st.secrets["gcp_service_account"].to_dict()
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open(st.secrets.get("SHEET_NAME", "IMD_DB")).sheet1 
        row = [datetime.now().isoformat(), "한의원", "Simulation", data['name'], data['phone'], "IMD_MOBILE_BOT"]
        sheet.append_row(row)
        return True
    except: return False

# ============================================
# 3. 화면 렌더링 (순차 출력 - 오류 해결)
# ============================================

# [헤더]
st.markdown("<h3 style='color:#D4AF37; text-align:center;'>IMD 메디컬 AI 시뮬레이터</h3>", unsafe_allow_html=True)
st.caption("👇 원장님이 '환자'가 되어 버튼을 눌러보세요. AI가 숨겨진 의도를 분석해드립니다.")
st.markdown("---")

# [기록된 히스토리 출력] - 여기가 핵심입니다. 
# 하나씩 따로 출력하여 브라우저 충돌을 방지합니다.
for item in st.session_state.history:
    if item['type'] == 'patient':
        st.markdown(f"""
        <div class="patient-card" style="{item.get('style', '')}">
            <span class="patient-label">{item['label']}</span>
            <div class="patient-text">{item['text']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    elif item['type'] == 'log':
        st.markdown(f"""
        <div class="admin-log" style="{item.get('style', '')}">
            <span class="log-header">{item['header']}</span>
            {item['text']}
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 4. 인터랙션 영역 (현재 단계에 맞는 버튼 노출)
# ============================================

# Step 0: 증상 선택
if st.session_state.step == 0:
    st.markdown("#### Q. 오늘 어디가 불편해서 오셨나요?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔋 만성 피로"):
            # 기록 저장
            st.session_state.history.append({
                "type": "patient", "label": "STEP 1. 증상 호소", "text": "선택: 🔋 만성 피로"
            })
            st.session_state.history.append({
                "type": "log", "header": "TARGET DETECTED", 
                "text": "고가 비급여(공진단/녹용) 타겟군 식별.<br>→ <b>'기력 회복'</b> 세일즈 시나리오 가동."
            })
            st.session_state.step = 1
            st.rerun()
            
    with col2:
        if st.button("🤕 통증 / 재활"):
            st.session_state.history.append({
                "type": "patient", "label": "STEP 1. 증상 호소", "text": "선택: 🤕 통증 / 재활"
            })
            st.session_state.history.append({
                "type": "log", "header": "TARGET DETECTED", 
                "text": "장기 내원(추나/약침) 타겟군 식별.<br>→ <b>'통증 원인 추적'</b> 시나리오 가동."
            })
            st.session_state.step = 1
            st.rerun()

# Step 1: 설진
elif st.session_state.step == 1:
    st.markdown("#### Q. 거울을 보고 혀 상태를 골라주세요.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👅 가장자리에 이빨 자국"):
            st.session_state.history.append({
                "type": "patient", "label": "STEP 2. 시각적 자가진단", "text": "선택: 👅 치흔설 (이빨 자국)"
            })
            st.session_state.history.append({
                "type": "log", "header": "DEEP ANALYSIS", 
                "text": "진단: <b>비위 허약 및 습담 정체.</b><br>전략: 단순 휴식으로는 회복 불가함을 강조하여 <span class='log-highlight'>장기 치료 티켓팅</span> 유도."
            })
            st.session_state.step = 2
            st.rerun()
            
    with c2:
        if st.button("👅 핏기 없고 하얀 혀"):
            st.session_state.history.append({
                "type": "patient", "label": "STEP 2. 시각적 자가진단", "text": "선택: 👅 담백설 (하얀 혀)"
            })
            st.session_state.history.append({
                "type": "log", "header": "DEEP ANALYSIS", 
                "text": "진단: <b>혈허 및 에너지 고갈.</b><br>전략: 즉각적인 에너지 보충 필요성 강조하여 <span class='log-highlight'>녹용/공진단</span> 제안."
            })
            st.session_state.step = 2
            st.rerun()

# Step 2: 결과 및 전환 유도
elif st.session_state.step == 2:
    # 자동 진행 (로딩 연출)
    # 히스토리의 마지막이 로그인지 확인하여 중복 실행 방지
    if st.session_state.history[-1]['type'] == 'log':
        with st.spinner("AI가 환자의 구매 가능성을 계산 중입니다..."):
            time.sleep(1.2)
            
        st.session_state.history.append({
            "type": "patient", "label": "ANALYSIS RESULT", 
            "text": "⚠️ <b>심각 단계 (42점)</b><br><br>단순 피로가 아닙니다. 몸의 엔진 오일이 말라붙은 <b>'기혈 양허'</b> 상태입니다.<br>지금 채워주지 않으면 <b>면역계 질환</b>으로 이어질 수 있습니다.",
            "style": "border-left: 6px solid #FF4B4B;"
        })
        st.session_state.history.append({
            "type": "log", "header": "💡 SALES OPPORTUNITY", 
            "text": "<b>원장님, 지금입니다.</b><br><br>환자는 자신의 상태가 '심각하다'고 인지했습니다.<br>이 타이밍에 <b>'프리미엄 3개월 프로그램'</b>을 제안하면 동의율이 80% 이상으로 올라갑니다.",
            "style": "border: 1px solid #D4AF37;"
        })
        st.rerun()
        
    # 버튼 표시
    if st.button("🚀 이 시스템, 우리 병원에 도입하기"):
        st.session_state.step = 3
        st.rerun()

# Step 3: 견적 요청 폼
elif st.session_state.step == 3:
    st.markdown("---")
    st.markdown("<h3 style='color:#D4AF37; text-align:center;'>도입 문의</h3>", unsafe_allow_html=True)
    st.info("이 시스템은 원장님의 진료 철학을 학습하여 커스터마이징됩니다.")
    
    with st.form("lead_form"):
        name = st.text_input("한의원명 / 원장님 성함")
        phone = st.text_input("연락처 (직통)")
        
        if st.form_submit_button("무료 도입 견적서 받기", use_container_width=True):
            if phone:
                save_lead({"name": name, "phone": phone})
                st.success("신청되었습니다. 담당자가 24시간 내로 연락드립니다.")
                st.balloons()
            else:
                st.error("연락처를 입력해주세요.")
    
    # 리셋 버튼
    if st.button("처음부터 다시 보기"):
        st.session_state.history = [
            {"type": "log", "header": "SYSTEM ONLINE", "text": "원장님, 환자가 '비싸요'라고 하는 진짜 이유는 돈이 없어서가 아닙니다.<br>내 몸이 그만큼 심각하다는 걸 <b>모르기 때문</b>입니다.<br><br>제가 질문 몇 개로 환자의 <b>'숨겨진 병리'</b>를 찾아내고, 스스로 지갑을 열게 만드는 과정을 보여드리겠습니다."},
            {"type": "patient", "label": "STEP 0. 시뮬레이션 시작", "text": "지금부터 원장님은 잠시 '만성 피로 환자' 역할을 해봐 주십시오.<br>편한 말투로 현재 상태를 한 줄만 말씀해 주세요."}
        ]
        st.session_state.step = 0
        st.rerun()

# ============================================
# 5. 푸터
# ============================================
st.markdown("""
<div style="text-align:center; padding:30px; color:#666; font-size:12px; margin-top:50px; border-top:1px solid #333;">
    IMD Strategic Consulting<br>
    한의원 전용 AI 매출 엔진 | 전국 일부 지역 독점 운영
</div>
""", unsafe_allow_html=True)

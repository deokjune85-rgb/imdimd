# app.py
"""
IMD Strategic Consulting - AI Sales Bot
완전히 새로 작성된 안정화 버전
"""

import time
import streamlit as st

# ============================================
# Config 로드
# ============================================
try:
    from config import COLOR_PRIMARY, COLOR_BORDER, TONGUE_TYPES
except Exception:
    COLOR_PRIMARY = "#111827"
    COLOR_BORDER = "#E5E7EB"
    TONGUE_TYPES = {}

# ============================================
# 모듈 import
# ============================================
from conversation_manager import get_conversation_manager
from lead_handler import LeadHandler

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="IMD Strategic Consulting",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================
# CSS - 간소화 버전
# ============================================
st.markdown(
    f"""
<style>
.stApp, .main {{ background: white !important; }}
.main .block-container {{
    padding: 0 !important;
    max-width: 720px !important;
    margin: 0 auto !important;
}}
header, .stDeployButton, footer {{ display: none !important; }}

.title-box {{
    text-align: center;
    padding: 20px;
    background: white;
}}
.title-box h1 {{
    font-size: 28px;
    font-weight: 700;
    color: {COLOR_PRIMARY};
    margin: 0;
}}
.title-box .sub {{
    font-size: 13px;
    color: #6B7280;
    margin-top: 4px;
}}

.chat-area {{
    padding: 12px 20px;
    background: white;
    min-height: 150px;
    margin-bottom: 200px;
}}

.ai-msg {{
    background: white;
    color: #111827;
    padding: 16px 20px;
    border-radius: 18px 18px 18px 4px;
    margin: 18px 0 10px 0;
    font-size: 18px;
    line-height: 1.6;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}}

.user-msg {{
    background: #E5E7EB;
    color: #111827;
    padding: 14px 20px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    font-size: 16px;
    display: inline-block;
    max-width: 70%;
}}

.msg-right {{
    text-align: right;
    margin-top: 16px;
}}

.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 12px 20px;
    text-align: center;
    font-size: 12px;
    color: #9CA3AF;
    border-top: 1px solid {COLOR_BORDER};
    z-index: 998;
}}

.stButton > button {{
    width: 100%;
    background: white;
    border: 2px solid {COLOR_PRIMARY};
    color: {COLOR_PRIMARY};
    font-weight: 600;
    padding: 12px;
    border-radius: 12px;
}}

.stButton > button:hover {{
    background: {COLOR_PRIMARY};
    color: white;
}}

@media (max-width: 768px) {{
    [data-testid="column"] {{
        min-width: 0 !important;
        width: 25% !important;
        flex: 0 0 25% !important;
    }}
    .stButton > button {{
        font-size: 11px !important;
        padding: 8px 4px !important;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
lead_handler = LeadHandler()

# 세션 상태 초기화
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

if "mode" not in st.session_state:
    st.session_state.mode = "simulation"

# 첫 메시지
if "app_initialized" not in st.session_state:
    initial_msg = (
        "<b>원장님, 환자가 '비싸요'라고 하는 진짜 이유는</b> "
        "돈이 없어서가 아닙니다.\n\n"
        "내 몸이 그만큼 심각하다는 걸 <b>모르기 때문</b>입니다.\n\n"
        "제가 질문 몇 개로 환자의 <b>'숨겨진 병리'</b>를 찾아내고,\n"
        "스스로 지갑을 열게 만드는 과정을 보여드리겠습니다.\n\n"
        "지금부터 원장님은 잠시 '만성 피로 환자' 역할을 해봐 주십시오.\n"
        "편한 말투로 현재 상태를 한 줄만 말씀해 주세요."
    )
    conv_manager.add_message("ai", initial_msg)
    conv_manager.update_stage("symptom_explore")
    st.session_state.app_initialized = True

# ============================================
# 헤더
# ============================================
st.markdown(
    """
<div class="title-box">
    <h1>IMD MEDICAL CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 학습한 'AI 수석 실장' 데모</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================
# 채팅 히스토리 출력
# ============================================
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

for msg in conv_manager.get_history():
    if msg["role"] == "ai":
        st.markdown(f'<div class="ai-msg">{msg["text"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "user":
        st.markdown(
            f'<div class="msg-right"><div class="user-msg">{msg["text"]}</div></div>',
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# 현재 단계 가져오기
# ============================================
current_stage = conv_manager.get_context().get("stage", "symptom_explore")

# ============================================
# 혀 선택 UI (tongue_select 단계에서만)
# ============================================
if current_stage == "tongue_select":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; font-weight:600; font-size:17px; margin:20px 0;'>"
        "거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요"
        "</div>",
        unsafe_allow_html=True,
    )
    
    cols = st.columns(4)
    tongue_list = ['담백설', '황태설', '치흔설', '자색설']
    
    for col, tongue_type in zip(cols, tongue_list):
        with col:
            if tongue_type in TONGUE_TYPES:
                info = TONGUE_TYPES[tongue_type]
                st.markdown(
                    f"<div style='font-size:50px; text-align:center;'>{info['emoji']}</div>",
                    unsafe_allow_html=True
                )
                
                if st.button(info['visual'], key=f"tongue_{tongue_type}", use_container_width=True):
                    # 사용자 메시지 추가
                    conv_manager.add_message("user", f"[선택: {info['visual']}]")
                    
                    # AI 분석 메시지
                    analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

{info['analysis']}

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 확인
2. "식사 후 졸리세요?" → 소화기능 저하 확인
3. 혀 사진 선택 → <b>시각적 증거 확보</b>

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
                    conv_manager.add_message("ai", analysis_msg)
                    conv_manager.update_context("selected_tongue", tongue_type)
                    conv_manager.update_stage("conversion")
                    st.session_state.mode = "closing"
                    st.rerun()

# ============================================
# CTA 폼 (conversion 단계 이후)
# ============================================
if current_stage == "conversion" or st.session_state.mode == "closing":
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; font-weight:600; font-size:18px; margin:20px 0;">'
        "이 시스템을 한의원에 도입하시겠습니까?"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            clinic_name = st.text_input("병원명", placeholder="서울한의원")
        with col2:
            director_name = st.text_input("원장님 성함", placeholder="홍길동")

        contact = st.text_input("연락처", placeholder="010-1234-5678")
        submitted = st.form_submit_button("무료 도입 견적서 받기", use_container_width=True)

        if submitted:
            if not clinic_name or not director_name or not contact:
                st.error("필수 정보를 모두 입력해주세요.")
            else:
                lead_data = {
                    "name": director_name,
                    "contact": contact,
                    "symptom": f"병원명: {clinic_name}",
                    "tongue_type": conv_manager.get_context().get("selected_tongue", ""),
                    "preferred_date": "즉시 상담 희망",
                    "chat_summary": conv_manager.get_summary(),
                    "source": "IMD_Strategic_Consulting",
                    "type": "Oriental_Clinic",
                }

                success, _ = lead_handler.save_lead(lead_data)

                if success:
                    completion_msg = f"""
견적서 발송이 완료되었습니다.

{director_name} 원장님, 감사합니다.

<b>{clinic_name}</b>에 최적화된 AI 실장 시스템 견적서를
<b>{contact}</b>로 24시간 내 전송해드리겠습니다.
"""
                    conv_manager.add_message("ai", completion_msg)
                    conv_manager.update_stage("complete")
                    st.success("견적서 신청이 완료되었습니다!")
                    time.sleep(1)
                    st.rerun()

# ============================================
# 텍스트 입력창 (tongue_select/conversion/complete 제외)
# ============================================
if current_stage not in ["tongue_select", "conversion", "complete"]:
    user_input = st.chat_input("원장님의 생각을 말씀해주세요")
    
    if user_input:
        # 사용자 메시지 추가
        conv_manager.add_message("user", user_input)
        st.session_state.conversation_count += 1
        
        # 단계별 응답
        if st.session_state.conversation_count == 1:
            response = """
원장님, 환자가 피로를 호소하고 있습니다.

<b>질문 1단계: 시간대 특정</b>

"언제 제일 힘드세요? 아침에 눈뜰 때인가요, 아니면 오후 3시쯤인가요?"
"""
            conv_manager.add_message("ai", response)
            conv_manager.update_stage("sleep_check")
            st.rerun()
        
        elif st.session_state.conversation_count == 2:
            response = """
역시 그렇군요. 아침부터 피곤하다는 건 단순 과로가 아닙니다.

<b>질문 2단계: 소화기능 확인</b>

"혹시 식사 후에 유독 졸리거나 속이 더부룩하진 않으신가요?"
"""
            conv_manager.add_message("ai", response)
            conv_manager.update_stage("digestion_check")
            st.rerun()
        
        elif st.session_state.conversation_count == 3:
            response = """
<b>분석 완료</b>

환자분의 증상을 정리하면:
- ✓ 아침 기상 시 피로
- ✓ 식후 졸음/더부룩함

이는 <b>비기허(脾氣虛) + 습담(濕痰) 정체</b>의 전형적 패턴입니다.

이제 혀 상태를 확인하여, 환자가 스스로 "내 몸이 망가졌구나"를 깨닫게 만들겠습니다.
"""
            conv_manager.add_message("ai", response)
            conv_manager.update_stage("tongue_select")
            st.rerun()

# ============================================
# 완료 후 액션 (complete 단계)
# ============================================
if current_stage == "complete":
    if st.button("새 상담 시작", use_container_width=True):
        conv_manager.reset_conversation()
        st.session_state.conversation_count = 0
        st.session_state.mode = "simulation"
        st.session_state.app_initialized = False
        st.rerun()

# ============================================
# 푸터
# ============================================
st.markdown(
    """
<div class="footer">
    <b>IMD Strategic Consulting</b><br>
    한의원 전용 AI 매출 엔진
</div>
""",
    unsafe_allow_html=True,
)

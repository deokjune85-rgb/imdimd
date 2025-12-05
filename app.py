# app_consulting.py
"""
IMD Strategic Consulting - AI Sales Bot (B2B)
한의원 원장님 대상 AI 실장 시스템 판매
"""

import streamlit as st
import time
from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler
from config import (
    COLOR_PRIMARY,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_AI_BUBBLE,
    COLOR_USER_BUBBLE,
    COLOR_BORDER
)

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="IMD Strategic Consulting",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS
# ============================================
st.markdown(f"""
<style>
/* 전체 흰색 배경 */
.stApp {{
    background: white !important;
}}

.main {{
    background: white !important;
}}

.main .block-container {{
    padding: 0 !important;
    max-width: 720px !important;
    margin: 0 auto !important;
    background: white !important;
}}

header, .stDeployButton {{
    display: none !important;
}}

footer {{
    display: none !important;
}}

/* 타이틀 */
.title-box {{
    text-align: center;
    padding: 20px 20px 12px 20px;
    background: white;
}}

.title-box h1 {{
    font-family: Arial, sans-serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: {COLOR_PRIMARY} !important;
    margin: 0 !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
}}

.title-box .sub {{
    font-size: 12px;
    color: #4B5563;
    margin-top: 4px;
}}

/* 채팅 영역 */
.chat-area {{
    padding: 12px 20px 4px 20px;
    background: white !important;
    min-height: 150px;
    margin-bottom: 100px;
}}

.ai-msg {{
    background: white !important;
    color: #1F2937 !important;
    padding: 14px 18px !important;
    border-radius: 18px 18px 18px 4px !important;
    margin: 16px 0 8px 0 !important;
    max-width: 85% !important;
    display: block !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    border: none !important;
    outline: none !important;
    clear: both !important;
}}

.ai-msg::before, .ai-msg::after {{
    content: none !important;
    display: none !important;
}}

.user-msg {{
    background: {COLOR_USER_BUBBLE} !important;
    color: #1F2937 !important;
    padding: 12px 18px !important;
    border-radius: 18px 18px 4px 18px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    display: inline-block !important;
    font-size: 15px !important;
    line-height: 1.4 !important;
    border: none !important;
    outline: none !important;
}}

.msg-right {{
    text-align: right !important;
    clear: both !important;
    display: block !important;
    width: 100% !important;
    margin-top: 16px !important;
}}

/* 입력창 */
.stChatInput {{
    position: fixed !important;
    bottom: 60px !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    background: white !important;
    padding: 10px 0 !important;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.08) !important;
    z-index: 999 !important;
    margin: 0 !important;
}}

.stChatInput > div {{
    max-width: 680px !important;
    margin: 0 auto !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 24px !important;
    background: white !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}}

.stChatInput input {{
    color: #1F2937 !important;
    background: white !important;
    -webkit-text-fill-color: #1F2937 !important;
}}

.stChatInput input::placeholder {{
    color: #D1D5DB !important;
    font-size: 15px !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #D1D5DB !important;
}}

/* 푸터 */
.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    background: white !important;
    padding: 12px 20px;
    text-align: center;
    font-size: 11px;
    color: #9CA3AF;
    border-top: 1px solid {COLOR_BORDER};
    z-index: 998;
}}

.footer b {{
    color: {COLOR_TEXT};
    font-weight: 600;
}}

/* 폼 */
.stForm {{
    background: white;
    padding: 20px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    margin: 16px 20px 180px 20px;
}}

.stForm label {{
    color: #1F2937 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}}

input, textarea, select {{
    border: 1px solid {COLOR_BORDER} !important;
    border-radius: 8px !important;
    background: white !important;
    color: #1F2937 !important;
}}

input::placeholder, textarea::placeholder {{
    color: #D1D5DB !important;
    opacity: 1 !important;
}}

/* 모바일 */
@media (max-width: 768px) {{
    .main .block-container {{
        padding-top: 0 !important;
    }}
    
    .title-box {{
        padding: 2px 16px 2px 16px !important;
    }}
    
    .title-box h1 {{
        font-size: 20px !important;
        line-height: 1.1 !important;
    }}
    
    .chat-area {{
        padding: 2px 16px 4px 16px !important;
    }}
    
    .ai-msg {{
        font-size: 14px !important;
        padding: 11px 15px;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
prompt_engine = get_prompt_engine()
lead_handler = LeadHandler()

# B2B 모드 시작 메시지
if 'app_initialized' not in st.session_state:
    initial_msg = """안녕하십니까, 원장님.

저는 24시간 잠들지 않는 AI 상담실장입니다.

환자들이 진료실에서 "비싸요, 그냥 침만 맞을게요"라고 할 때 힘빠지시죠?

저는 진료 전에 환자의 마음을 열고, 지갑을 열 준비를 시킵니다.

백문이 불여일견입니다. 
지금부터 원장님은 '만성 피로 환자'가 되어주세요. 
제가 어떻게 설득하는지 보여드리겠습니다."""
    
    conv_manager.add_message("ai", initial_msg)
    st.session_state.app_initialized = True
    st.session_state.mode = 'b2b_intro'  # b2b_intro -> simulation -> b2b_closing

# ============================================
# 헤더
# ============================================
st.markdown("""
<div class="title-box">
    <h1>IMD STRATEGIC CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 완벽하게 학습한 'AI 수석 실장'을 소개합니다</div>
    <div class="sub" style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">엑셀은 기록만 하지만, AI는 '매출'을 만듭니다 (체험시간: 2분)</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# 채팅 히스토리
# ============================================
chat_html = '<div class="chat-area">'

for msg in conv_manager.get_history():
    if msg['role'] == 'ai':
        chat_html += f'<div class="ai-msg">{msg["text"]}</div>'
    elif msg['role'] == 'user':
        chat_html += f'<div class="msg-right"><span class="user-msg">{msg["text"]}</span></div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ============================================
# 자동 CTA (시뮬레이션 완료 후)
# ============================================
chat_history = conv_manager.get_history()
last_msg_is_ai = chat_history and chat_history[-1]['role'] == 'ai'

# 시뮬레이션 완료 판단 (6회 이상 대화 + AI 답변으로 끝)
if len(chat_history) >= 6 and last_msg_is_ai and conv_manager.get_context()['stage'] != 'complete':
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:18px; margin:20px 0 10px;">이 시스템을 한의원에 도입하시겠습니까?</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#6B7280; font-size:14px; margin-bottom:20px;'>지역구 독점권은 선착순입니다. 무료 도입 견적서를 보내드립니다</p>",
        unsafe_allow_html=True
    )
    
    with st.form("consulting_form"):
        col1, col2 = st.columns(2)
        with col1:
            clinic_name = st.text_input("병원명", placeholder="서울한의원")
        with col2:
            director_name = st.text_input("원장님 성함", placeholder="홍길동")
        
        contact = st.text_input("연락처 (직통)", placeholder="010-1234-5678")
        
        submitted = st.form_submit_button("무료 도입 견적서 받기", use_container_width=True)
        
        if submitted:
            if not clinic_name or not director_name or not contact:
                st.error("필수 정보를 모두 입력해주세요.")
            else:
                lead_data = {
                    'name': director_name,
                    'contact': contact,
                    'symptom': f"병원명: {clinic_name}",
                    'preferred_date': '즉시 상담 희망',
                    'chat_summary': conv_manager.get_summary(),
                    'source': 'IMD_Strategic_Consulting',
                    'type': 'Oriental_Clinic'
                }
                
                success, message = lead_handler.save_lead(lead_data)
                
                if success:
                    completion_msg = f"""
견적서 발송이 완료되었습니다.

{director_name} 원장님, 감사합니다.

{clinic_name}에 최적화된 AI 실장 시스템 견적서를 
{contact}로 24시간 내 전송해드리겠습니다.

포함 내용:
- 맞춤형 시스템 구축 비용
- 월 운영비 및 유지보수
- 지역 독점권 계약 조건
- ROI 예상 시뮬레이션

담당 컨설턴트가 직접 연락드려 상세히 안내해드리겠습니다.
"""
                    conv_manager.add_message("ai", completion_msg)
                    conv_manager.update_stage('complete')
                    
                    st.success("견적서 신청이 완료되었습니다!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"오류: {message}")

# ============================================
# 입력창
# ============================================
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})
    
    context = conv_manager.get_context()
    history = conv_manager.get_formatted_history(for_llm=True)
    
    time.sleep(1.0)
    ai_response = generate_ai_response(user_input, context, history)
    
    conv_manager.add_message("ai", ai_response)
    st.rerun()

# ============================================
# 완료 후
# ============================================
if conv_manager.get_context()['stage'] == 'complete':
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("새 상담 시작", use_container_width=True):
            conv_manager.reset_conversation()
            st.rerun()
    
    with col2:
        if st.button("상담 내역 보기", use_container_width=True):
            with st.expander("상담 요약", expanded=True):
                st.markdown(conv_manager.get_summary())

# ============================================
# 푸터
# ============================================
st.markdown("""
<div class="footer">
    <b>IMD Strategic Consulting</b><br>
    한의원 전용 AI 매출 엔진 | 전국 200개 한의원 도입 완료
</div>
""", unsafe_allow_html=True)

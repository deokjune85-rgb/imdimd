# app_landing.py
"""
IMD Sales Bot - Main Application
AI 기반 세일즈 대화형 랜딩 페이지
"""

import streamlit as st
import time
from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler
from config import (
    APP_TITLE,
    APP_ICON,
    LAYOUT,
    COLOR_PRIMARY,
    COLOR_BG,
    COLOR_AI_BUBBLE,
    COLOR_USER_BUBBLE,
    URGENCY_OPTIONS
)

# ============================================
# 0. 페이지 설정
# ============================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT
)

# ============================================
# 1. CSS 스타일링 (Cyber-Noir)
# ============================================
def load_css():
    """커스텀 CSS 로드"""
    custom_css = f"""
    <style>
    /* 전체 배경 */
    .stApp {{
        background-color: {COLOR_BG};
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
        color: white;
    }}
    
    /* 타이틀 */
    h1, h2, h3 {{
        color: {COLOR_PRIMARY} !important;
        font-weight: 800;
        text-align: center;
    }}
    
    /* 채팅 컨테이너 */
    .chat-container {{
        max-width: 700px;
        margin: 20px auto;
        padding-bottom: 120px;
    }}
    
    /* AI 메시지 버블 */
    .chat-bubble-ai {{
        background-color: {COLOR_AI_BUBBLE};
        color: white !important;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 5px;
        margin-bottom: 15px;
        width: fit-content;
        max-width: 85%;
        font-size: 16px;
        line-height: 1.6;
        border-left: 3px solid {COLOR_PRIMARY};
        animation: fadeIn 0.5s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }}
    
    /* 사용자 메시지 버블 */
    .chat-bubble-user {{
        background-color: {COLOR_USER_BUBBLE};
        color: black !important;
        padding: 14px 20px;
        border-radius: 20px 20px 5px 20px;
        margin-bottom: 15px;
        margin-left: auto;
        width: fit-content;
        max-width: 80%;
        font-size: 16px;
        font-weight: 600;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 229, 255, 0.4);
    }}
    
    /* 애니메이션 */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    /* 추천 버튼 */
    .stButton > button {{
        width: 100%;
        background-color: transparent;
        color: {COLOR_PRIMARY} !important;
        border: 2px solid {COLOR_PRIMARY};
        padding: 14px 20px;
        font-size: 15px;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }}
    
    .stButton > button:hover {{
        background-color: {COLOR_PRIMARY};
        color: black !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
        transform: scale(1.03);
    }}
    
    /* 입력창 */
    .stChatInput > div {{
        background-color: #1a1a1a !important;
        border: 1px solid {COLOR_PRIMARY} !important;
    }}
    
    input[type="text"], textarea {{
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }}
    
    /* 폼 스타일 */
    .stForm {{
        background-color: #111;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid {COLOR_PRIMARY};
    }}
    
    /* 타이핑 인디케이터 */
    .typing-indicator {{
        display: inline-block;
        padding: 10px 15px;
        background-color: {COLOR_AI_BUBBLE};
        border-radius: 15px;
        margin-bottom: 10px;
    }}
    
    .typing-indicator span {{
        height: 8px;
        width: 8px;
        background-color: {COLOR_PRIMARY};
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: bounce 1.4s infinite ease-in-out;
    }}
    
    .typing-indicator span:nth-child(1) {{ animation-delay: -0.32s; }}
    .typing-indicator span:nth-child(2) {{ animation-delay: -0.16s; }}
    
    @keyframes bounce {{
        0%, 80%, 100% {{ transform: scale(0); }}
        40% {{ transform: scale(1); }}
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

load_css()

# ============================================
# 2. 초기화
# ============================================
conv_manager = get_conversation_manager()
prompt_engine = get_prompt_engine()
lead_handler = LeadHandler()

# 첫 방문 시 웰컴 메시지
if len(conv_manager.get_history()) == 0:
    initial_msg = prompt_engine.generate_initial_message()
    conv_manager.add_message("ai", initial_msg)

# ============================================
# 3. 헤더
# ============================================
st.title("🧠 IMD AI Business Diagnosis")
st.markdown("<p style='text-align:center; color:#888;'>AI가 직접 설득하는 세일즈 봇 - 실시간 대화 체험</p>", unsafe_allow_html=True)

# ============================================
# 4. 채팅 히스토리 렌더링
# ============================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for chat in conv_manager.get_history():
    role_class = "chat-bubble-ai" if chat['role'] == 'ai' else "chat-bubble-user"
    st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 5. 추천 버튼 (Quick Reply)
# ============================================
if not conv_manager.is_ready_for_conversion():
    st.markdown("---")
    st.markdown("#### 💬 빠른 선택 (또는 아래 채팅창에 자유롭게 입력하세요)")
    
    buttons = conv_manager.get_recommended_buttons()
    cols = st.columns(len(buttons))
    
    for idx, button_text in enumerate(buttons):
        with cols[idx]:
            if st.button(button_text, key=f"quick_{idx}"):
                # 버튼 클릭 = 사용자 입력으로 처리
                conv_manager.add_message("user", button_text, metadata={"type": "button"})
                
                # AI 응답 생성
                context = conv_manager.get_context()
                history = conv_manager.get_formatted_history(for_llm=True)
                
                with st.spinner(""):
                    time.sleep(0.8)  # 타이핑 느낌
                    ai_response = generate_ai_response(button_text, context, history)
                
                conv_manager.add_message("ai", ai_response)
                st.rerun()

# ============================================
# 6. 채팅 입력창 (자연어)
# ============================================
user_input = st.chat_input("💬 궁금한 점을 자유롭게 물어보세요...")

if user_input:
    # 사용자 메시지 추가
    conv_manager.add_message("user", user_input, metadata={"type": "text"})
    
    # AI 응답 생성
    context = conv_manager.get_context()
    history = conv_manager.get_formatted_history(for_llm=True)
    
    with st.spinner(""):
        time.sleep(1.0)  # 타이핑 시뮬레이션
        ai_response = generate_ai_response(user_input, context, history)
    
    conv_manager.add_message("ai", ai_response)
    st.rerun()

# ============================================
# 7. 리드 전환 폼 (적절한 타이밍에 표시)
# ============================================
if conv_manager.is_ready_for_conversion() and conv_manager.get_context()['stage'] != 'complete':
    st.markdown("---")
    st.markdown("### 🚀 무료 AI 설계도 + 견적 신청")
    st.markdown("**담당 아키텍트가 24시간 내 연락드립니다**")
    
    with st.form("lead_capture_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("성함 / 직함 *", placeholder="홍길동 / 대표")
        with col2:
            contact = st.text_input("연락처 *", placeholder="010-1234-5678")
        
        company = st.text_input("병원명 / 쇼핑몰명 (선택)", placeholder="예: 서울성형외과, ABC쇼핑몰")
        urgency = st.selectbox("도입 희망 시기 *", URGENCY_OPTIONS)
        
        submitted = st.form_submit_button("✅ 무료 설계도 받기", use_container_width=True)
        
        if submitted:
            if not name or not contact:
                st.error("❌ 성함과 연락처는 필수 입력 항목입니다.")
            else:
                # 리드 저장
                lead_data = {
                    'user_type': conv_manager.get_context().get('user_type', 'Unknown'),
                    'stage': 'Lead Converted',
                    'name': name,
                    'contact': contact,
                    'company': company,
                    'urgency': urgency,
                    'source': 'IMD_Sales_Bot_V2'
                }
                
                success, message = lead_handler.save_lead(lead_data)
                
                if success:
                    # 완료 메시지
                    completion_msg = lead_handler.format_lead_message(lead_data)
                    conv_manager.add_message("ai", completion_msg)
                    conv_manager.update_stage('complete')
                    
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

# ============================================
# 8. 하단 액션 (완료 후)
# ============================================
if conv_manager.get_context()['stage'] == 'complete':
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 처음부터 다시 시작", use_container_width=True):
            conv_manager.reset_conversation()
            st.rerun()
    
    with col2:
        if st.button("📊 대화 요약 보기", use_container_width=True):
            with st.expander("대화 요약 (관리자용)", expanded=True):
                st.markdown(conv_manager.get_summary())

# ============================================
# 9. 사이드바 (옵션)
# ============================================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/000000/00E5FF?text=IMD", width=150)
    st.markdown("### 📈 실시간 통계")
    st.metric("대화 진행도", f"{conv_manager.get_context()['trust_level']}%")
    st.metric("총 메시지", len(conv_manager.get_history()))
    
    st.markdown("---")
    st.markdown("### ⚙️ 개발자 모드")
    if st.checkbox("컨텍스트 보기"):
        st.json(conv_manager.get_context())
    
    if st.button("🗑️ 대화 초기화"):
        conv_manager.reset_conversation()
        st.rerun()

# ============================================
# 10. 푸터
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#666; font-size:12px;'>
        Powered by <b>IMD Architecture Group</b> | Gemini 2.0 Flash<br>
        © 2024 Reset Security. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

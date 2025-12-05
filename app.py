# app.py
"""
IMD Sales Bot - Main Application
다크 엘레강스 (McKinsey 컨설팅 스타일)
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
    COLOR_SECONDARY,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_AI_BUBBLE,
    COLOR_USER_BUBBLE,
    COLOR_BORDER,
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
# 1. CSS 스타일링 (다크 엘레강스)
# ============================================
def load_css():
    """다크 엘레강스 CSS"""
    custom_css = f"""
    <style>
    /* 전체 배경 */
    .stApp {{
        background: linear-gradient(135deg, {COLOR_BG} 0%, #1a1f35 100%);
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {COLOR_TEXT};
    }}
    
    /* 타이틀 */
    h1 {{
        color: {COLOR_PRIMARY} !important;
        font-weight: 700;
        text-align: center;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }}
    
    h2, h3 {{
        color: {COLOR_TEXT} !important;
        font-weight: 600;
    }}
    
    /* 서브타이틀 */
    .subtitle {{
        text-align: center;
        color: #94A3B8;
        font-size: 15px;
        margin-bottom: 32px;
        font-weight: 400;
    }}
    
    /* 채팅 컨테이너 */
    .chat-container {{
        max-width: 720px;
        margin: 24px auto;
        padding-bottom: 100px;
    }}
    
    /* AI 메시지 버블 */
    .chat-bubble-ai {{
        background: linear-gradient(135deg, {COLOR_AI_BUBBLE} 0%, #2d3748 100%);
        color: {COLOR_TEXT} !important;
        padding: 20px 24px;
        border-radius: 16px 16px 16px 4px;
        margin-bottom: 16px;
        width: fit-content;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.7;
        border-left: 3px solid {COLOR_PRIMARY};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: fadeIn 0.6s ease;
    }}
    
    /* 사용자 메시지 버블 */
    .chat-bubble-user {{
        background: {COLOR_USER_BUBBLE};
        color: {COLOR_TEXT} !important;
        padding: 16px 24px;
        border-radius: 16px 16px 4px 16px;
        margin-bottom: 16px;
        margin-left: auto;
        width: fit-content;
        max-width: 75%;
        font-size: 15px;
        font-weight: 500;
        animation: slideIn 0.4s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid {COLOR_BORDER};
    }}
    
    /* 애니메이션 */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(12px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    /* 추천 버튼 */
    .stButton > button {{
        width: 100%;
        background: transparent;
        color: {COLOR_PRIMARY} !important;
        border: 1.5px solid {COLOR_BORDER};
        padding: 14px 20px;
        font-size: 14px;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
    }}
    
    .stButton > button:hover {{
        background: {COLOR_AI_BUBBLE};
        border-color: {COLOR_PRIMARY};
        box-shadow: 0 0 16px rgba(212, 175, 55, 0.2);
        transform: translateY(-2px);
    }}
    
    /* 입력창 */
    .stChatInput > div {{
        background-color: {COLOR_AI_BUBBLE} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 12px !important;
    }}
    
    input[type="text"], textarea, .stSelectbox > div > div {{
        background-color: {COLOR_AI_BUBBLE} !important;
        color: {COLOR_TEXT} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }}
    
    /* 폼 스타일 */
    .stForm {{
        background: linear-gradient(135deg, {COLOR_AI_BUBBLE} 0%, #2d3748 100%);
        padding: 28px;
        border-radius: 16px;
        border: 1px solid {COLOR_PRIMARY};
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }}
    
    /* 섹션 제목 */
    .section-title {{
        color: {COLOR_PRIMARY};
        font-size: 18px;
        font-weight: 600;
        margin: 24px 0 12px 0;
        text-align: center;
    }}
    
    /* 구분선 */
    hr {{
        border-color: {COLOR_BORDER};
        opacity: 0.3;
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
st.title("IMD AI 전략 컨설팅")
st.markdown('<p class="subtitle">데이터 기반 비즈니스 성장 솔루션</p>', unsafe_allow_html=True)

# ============================================
# 4. 채팅 히스토리 렌더링
# ============================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for chat in conv_manager.get_history():
    role_class = "chat-bubble-ai" if chat['role'] == 'ai' else "chat-bubble-user"
    st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 5. 추천 버튼
# ============================================
if not conv_manager.is_ready_for_conversion():
    st.markdown('<p class="section-title">주요 문의 사항</p>', unsafe_allow_html=True)
    
    buttons = conv_manager.get_recommended_buttons()
    
    # 버튼 레이아웃
    if len(buttons) == 3:
        cols = st.columns(3)
    else:
        cols = st.columns(len(buttons))
    
    for idx, button_text in enumerate(buttons):
        with cols[idx]:
            if st.button(button_text, key=f"quick_{idx}"):
                # 버튼 클릭 처리
                conv_manager.add_message("user", button_text, metadata={"type": "button"})
                
                # AI 응답 생성
                context = conv_manager.get_context()
                history = conv_manager.get_formatted_history(for_llm=True)
                
                with st.spinner("분석 중..."):
                    time.sleep(0.8)
                    ai_response = generate_ai_response(button_text, context, history)
                
                conv_manager.add_message("ai", ai_response)
                st.rerun()

# ============================================
# 6. 채팅 입력창
# ============================================
user_input = st.chat_input("문의 사항을 입력하세요")

if user_input:
    # 사용자 메시지 추가
    conv_manager.add_message("user", user_input, metadata={"type": "text"})
    
    # AI 응답 생성
    context = conv_manager.get_context()
    history = conv_manager.get_formatted_history(for_llm=True)
    
    with st.spinner("분석 중..."):
        time.sleep(1.0)
        ai_response = generate_ai_response(user_input, context, history)
    
    conv_manager.add_message("ai", ai_response)
    st.rerun()

# ============================================
# 7. 리드 전환 폼
# ============================================
if conv_manager.is_ready_for_conversion() and conv_manager.get_context()['stage'] != 'complete':
    st.markdown("---")
    st.markdown('<p class="section-title">AI 아키텍처 설계 제안서 신청</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94A3B8; font-size:14px;'>담당 컨설턴트가 24시간 내 연락드립니다</p>", unsafe_allow_html=True)
    
    with st.form("lead_capture_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("성함 / 직함", placeholder="홍길동 / 대표이사")
        with col2:
            contact = st.text_input("연락처", placeholder="010-1234-5678")
        
        company = st.text_input("기업명 / 병원명", placeholder="예: (주)ABC컴퍼니")
        urgency = st.selectbox("도입 희망 시기", URGENCY_OPTIONS)
        
        submitted = st.form_submit_button("제안서 신청", use_container_width=True)
        
        if submitted:
            if not name or not contact:
                st.error("필수 정보를 입력해주세요.")
            else:
                # 리드 저장
                lead_data = {
                    'user_type': conv_manager.get_context().get('user_type', 'Unknown'),
                    'stage': 'Lead Converted',
                    'name': name,
                    'contact': contact,
                    'company': company,
                    'urgency': urgency,
                    'source': 'IMD_AI_Consultant'
                }
                
                success, message = lead_handler.save_lead(lead_data)
                
                if success:
                    # 완료 메시지
                    completion_msg = f"""
### 신청이 완료되었습니다

**{name}님**, 감사합니다.

담당 컨설턴트가 **24시간 내**로 아래 연락처로 맞춤 분석 리포트와 함께 연락드립니다.

**연락처**: {contact}  
**희망 시기**: {urgency}

---

**다음 단계:**
1. 24시간 내: 1차 전화 상담
2. 48시간 내: 맞춤 AI 설계 제안서 발송
3. 7일 내: 실제 데모 시연 (선택)
"""
                    conv_manager.add_message("ai", completion_msg)
                    conv_manager.update_stage('complete')
                    
                    st.success("신청이 완료되었습니다.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"오류: {message}")

# ============================================
# 8. 완료 후 액션
# ============================================
if conv_manager.get_context()['stage'] == 'complete':
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("새 상담 시작", use_container_width=True):
            conv_manager.reset_conversation()
            st.rerun()
    
    with col2:
        if st.button("대화 요약 보기", use_container_width=True):
            with st.expander("상담 요약", expanded=True):
                st.markdown(conv_manager.get_summary())

# ============================================
# 9. 사이드바 (간소화)
# ============================================
with st.sidebar:
    st.markdown(f"<h3 style='color:{COLOR_PRIMARY};'>IMD</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:12px;'>AI Architecture Group</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 진행도
    trust = conv_manager.get_context()['trust_level']
    st.metric("상담 진행도", f"{trust}%")
    
    # 개발자 모드 (간소화)
    if st.checkbox("시스템 정보"):
        st.json({
            "messages": len(conv_manager.get_history()),
            "stage": conv_manager.get_context()['stage'],
            "user_type": conv_manager.get_context().get('user_type', 'Unknown')
        })

# ============================================
# 10. 푸터
# ============================================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align:center; color:#64748B; font-size:11px; padding: 20px 0;'>
        <b style='color:{COLOR_PRIMARY};'>IMD Architecture Group</b><br>
        Enterprise AI Solutions | Powered by Gemini 2.0<br>
        © 2024 Reset Security. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

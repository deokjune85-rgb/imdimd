"""
IMD Strategic Consulting - AI Sales Bot (B2B)
멀티 페르소나 지원: ?client=gs (안과), ?client=nana (성형), 기본(한의원)
"""

import time
from typing import Any, Dict

import streamlit as st
from PIL import Image

from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler
from config import (
    CFG,
    TONGUE_TYPES,
    COLOR_PRIMARY,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_AI_BUBBLE,
    COLOR_USER_BUBBLE,
    COLOR_BORDER,
)

# ============================================
# 페이지 설정 (CFG에서 가져오기)
# ============================================
st.set_page_config(
    page_title=CFG["APP_TITLE"],
    page_icon=CFG["APP_ICON"],
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================
# CSS
# ============================================
st.markdown(
    f"""
<style>
/* Streamlit 기본 푸터/헤더 숨기기 */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.stDeployButton {{display: none;}}
[data-testid="stToolbar"] {{display: none;}}
[data-testid="stDecoration"] {{display: none;}}
[data-testid="stStatusWidget"] {{display: none;}}
.viewerBadge_container__r5tak {{display: none;}}
.styles_viewerBadge__CvC9N {{display: none;}}

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
    font-size: 30px !important;
    font-weight: 700 !important;
    color: {COLOR_PRIMARY} !important;
    margin: 0 !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
}}

.title-box .sub {{
    font-size: 16px;
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
    font-size: 20px !important;
    line-height: 1.5 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    border: none !important;
    outline: none !important;
    clear: both !important;
}}

.user-msg {{
    background: {COLOR_USER_BUBBLE} !important;
    color: #1F2937 !important;
    padding: 12px 18px !important;
    border-radius: 18px 18px 4px 18px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    display: inline-block !important;
    font-size: 19px !important;
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
        padding: 0 !important;
        max-width: 100% !important;
    }}
    
    .title-box {{
        padding: 8px 8px 8px 8px !important;
    }}
    
    .title-box h1 {{
        font-size: 22px !important;
        line-height: 1.1 !important;
    }}
    
    .chat-area {{
        padding: 8px 8px 4px 8px !important;
    }}
    
    .ai-msg {{
        font-size: 16px !important;
        padding: 10px 12px !important;
    }}
    
    .user-msg {{
        font-size: 15px !important;
    }}
    
    /* 모바일에서 선택지 4개 가로 배열 강제 */
    div[data-testid="stHorizontalBlock"] {{
        gap: 4px !important;
    }}
    
    div[data-testid="column"] {{
        min-width: 0 !important;
        flex: 0 0 23% !important;
        max-width: 25% !important;
        padding: 0 2px !important;
    }}
    
    div[data-testid="column"] > div {{
        padding: 0 !important;
    }}
    
    div[data-testid="column"] img {{
        width: 100% !important;
        height: auto !important;
        margin-bottom: 2px !important;
    }}
    
    div[data-testid="column"] button {{
        font-size: 10px !important;
        padding: 4px 2px !important;
        margin-top: 2px !important;
        white-space: nowrap !important;
    }}
    
    div[data-testid="column"] div[style*="text-align:center"] {{
        font-size: 10px !important;
        margin: 2px 0 !important;
    }}
    
    /* 입력창 여백 제거 */
    .stChatInput {{
        padding: 10px 4px !important;
    }}
    
    .stChatInput > div {{
        max-width: 100% !important;
        margin: 0 4px !important;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# 유틸: [[STAGE:...]] 파싱
# ============================================
ALLOWED_STAGES = {
    "initial",
    "symptom_explore",
    "sleep_check",
    "digestion_check",
    "tongue_select",
    "conversion",
    "complete",
}


def parse_stage_tag(text: str, current_stage: str) -> (str, str):
    marker = "[[STAGE:"
    idx = text.rfind(marker)
    if idx == -1 or not text.strip().endswith("]]"):
        return text, current_stage

    tag_part = text[idx:].strip()
    body = text[:idx].rstrip()

    inside = tag_part[len(marker) : -2].strip().lower()
    if inside in ALLOWED_STAGES:
        return body, inside
    return body, current_stage


def html_escape(s: str) -> str:
    import html
    return html.escape(s).replace("\n", "<br>")


# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
engine_info = get_prompt_engine()
lead_handler = LeadHandler()

if "app_initialized" not in st.session_state:
    # CFG에서 초기 메시지 가져오기
    initial_msg = CFG["INITIAL_MSG"]
    conv_manager.add_message("ai", initial_msg)
    conv_manager.update_stage("initial")
    st.session_state.app_initialized = True
    st.session_state.conversation_count = 0

# ============================================
# 헤더 (CFG에서 가져오기)
# ============================================
st.markdown(
    f"""
<div class="title-box">
    <h1>{CFG["HEADER_TITLE"]}</h1>
    <div class="sub">{CFG["HEADER_SUB"]}</div>
    <div class="sub" style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">
        {CFG["HEADER_SMALL"]}
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================
# 채팅 히스토리 렌더링
# ============================================
with st.container():
    chat_html = '<div class="chat-area">'
    for msg in conv_manager.get_history():
        role = msg.get("role")
        text = msg.get("text", "")
        safe = html_escape(text)
        if role == "ai":
            chat_html += f'<div class="ai-msg">{safe}</div>'
        elif role == "user":
            chat_html += f'<div class="msg-right"><span class="user-msg">{safe}</span></div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

# ============================================
# 컨텍스트
# ============================================
context: Dict[str, Any] = conv_manager.get_context()
chat_history = conv_manager.get_history()
current_stage = context.get("stage", "initial")
selected_tongue = context.get("selected_tongue")

# ============================================
# 선택 UI (tongue_select 단계에서만)
# ============================================
last_ai_text = (
    chat_history[-1]["text"] if chat_history and chat_history[-1]["role"] == "ai" else ""
)

# 트리거 키워드 확장 (안과: 글씨/시력, 성형: 스타일/워너비)
trigger_keywords = ["혀", "거울", "글씨", "시력", "스타일", "워너비", "선택"]
show_tongue_ui = (
    current_stage == "tongue_select"
    and not selected_tongue
    and any(kw in last_ai_text for kw in trigger_keywords)
)

if show_tongue_ui:
    with st.container():
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:20px; margin:4px 0 8px 0;">{CFG["TONGUE_GUIDE"]}</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(4)

        for idx, (tongue_key, tongue_data) in enumerate(TONGUE_TYPES.items()):
            with cols[idx]:
                image_path = tongue_data.get("image", "")
                try:
                    img = Image.open(image_path)
                    st.image(img, use_container_width=True)
                except Exception:
                    st.markdown(
                        f"<div style='text-align:center; font-size:80px; padding:20px 0;'>{tongue_data['emoji']}</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:600; margin:4px 0; color:#1F2937;'>{tongue_data['name']}</div>",
                    unsafe_allow_html=True,
                )

                if st.button("선택", key=f"tongue_{tongue_key}", use_container_width=True):
                    conv_manager.update_context("selected_tongue", tongue_key)

                    diagnosis_msg = f"""{tongue_data['name']} 상태를 선택하셨습니다.

{tongue_data['analysis']}

주요 증상: {tongue_data['symptoms']}

⚠️ 주의: {tongue_data['warning']}

방금 보신 과정이 실제로 AI가 환자에게 자동으로 진행하는 흐름입니다.

이제부터는 이 분석 결과를 바탕으로,
- 환자분께 현재 상태의 '위험 신호'를 이해시키고
- 적절한 치료/시술 플랜이 왜 필요한지
자연스럽게 연결하는 상담 단계로 넘어가게 됩니다.
"""
                    conv_manager.add_message("ai", diagnosis_msg)
                    conv_manager.update_stage("conversion")
                    try:
                        conv_manager.calculate_health_score()
                    except:
                        pass
                    st.rerun()

        st.markdown('<div style="height:150px;"></div>', unsafe_allow_html=True)

# ============================================
# CTA (conversion 단계) - CFG에서 텍스트 가져오기
# ============================================
current_stage = conv_manager.get_context().get("stage", "initial")
selected_tongue = conv_manager.get_context().get("selected_tongue")

show_cta = (current_stage == "conversion") or (
    len(conv_manager.get_history()) > 0 and 
    "도입하시겠습니까" in conv_manager.get_history()[-1].get("text", "")
)

if show_cta and current_stage != "complete":
    with st.container():
        st.markdown("---")
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:18px; margin:20px 0 10px;">{CFG["CTA_TITLE"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align:center; color:#6B7280; font-size:14px; margin-bottom:20px;'>{CFG['CTA_SUB']}</p>",
            unsafe_allow_html=True,
        )

        with st.form("consulting_form"):
            col1, col2 = st.columns(2)
            with col1:
                clinic_name = st.text_input(CFG["FORM_LABEL_1"], placeholder=CFG["FORM_PLACEHOLDER_1"])
            with col2:
                director_name = st.text_input(CFG["FORM_LABEL_2"], placeholder=CFG["FORM_PLACEHOLDER_2"])

            contact = st.text_input("연락처 (직통)", placeholder="010-1234-5678")

            submitted = st.form_submit_button(CFG["FORM_BUTTON"], use_container_width=True)

            if submitted:
                if not clinic_name or not director_name or not contact:
                    st.error("필수 정보를 모두 입력해주세요.")
                else:
                    lead_data = {
                        "name": director_name,
                        "contact": contact,
                        "symptom": f"병원명: {clinic_name}",
                        "preferred_date": "즉시 상담 희망",
                        "chat_summary": conv_manager.get_summary(),
                        "source": CFG["APP_TITLE"],
                        "type": CFG["APP_TITLE"],
                    }

                    success, message = lead_handler.save_lead(lead_data)

                    if success:
                        completion_msg = f"""
견적서 발송이 완료되었습니다.

{director_name}님, 감사합니다.

{clinic_name}에 최적화된 AI 시스템 견적서를
{contact}로 24시간 내 전송해드리겠습니다.

포함 내용:
- 맞춤형 시스템 구축 비용
- 월 운영비 및 유지보수
- 도입 일정 및 세팅 안내
- ROI 예상 시뮬레이션

담당 컨설턴트가 직접 연락드려 상세히 안내해드리겠습니다.
"""
                        conv_manager.add_message("ai", completion_msg)
                        conv_manager.update_stage("complete")
                        st.success("견적서 신청이 완료되었습니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"오류: {message}")

# ============================================
# 입력창 + 제미나이 호출
# ============================================
user_input = st.chat_input("메시지를 입력해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})

    st.session_state.conversation_count = st.session_state.get("conversation_count", 0) + 1

    context = conv_manager.get_context()
    history_for_llm = conv_manager.get_history()

    raw_ai = generate_ai_response(user_input, context, history_for_llm)
    clean_ai, new_stage = parse_stage_tag(raw_ai, context.get("stage", "initial"))

    if new_stage == "conversion":
        from prompt_engine import generate_veritas_story
        
        user_messages = [
            msg.get("text", "") 
            for msg in conv_manager.get_history() 
            if msg.get("role") == "user"
        ]
        
        symptom_messages = [
            m for m in user_messages 
            if len(m) >= 5 and any(ord('가') <= ord(c) <= ord('힣') for c in m)
        ]
        
        if symptom_messages:
            symptom = " ".join(symptom_messages[:2])
        else:
            symptom = "만성 피로와 전신 무력감"
        
        success_story = generate_veritas_story(symptom)
        clean_ai += f"\n\n---\n\n💬 **실제 후기**\n\n\"{success_story}\"\n\n---\n"

    conv_manager.add_message("ai", clean_ai)
    conv_manager.update_stage(new_stage)

    time.sleep(0.2)
    st.rerun()

# ============================================
# 완료 후 버튼
# ============================================
if conv_manager.get_context().get("stage") == "complete":
    col1, col2 = st.columns(2)

    with col1:
        if st.button("새 상담 시작", use_container_width=True):
            conv_manager.reset_conversation()
            conv_manager.update_stage("initial")
            st.session_state.conversation_count = 0
            st.rerun()

    with col2:
        if st.button("상담 내역 보기", use_container_width=True):
            with st.expander("상담 요약", expanded=True):
                st.markdown(html_escape(conv_manager.get_summary()), unsafe_allow_html=True)

# ============================================
# 푸터 (CFG에서 가져오기)
# ============================================
st.markdown(
    f"""
<div class="footer">
    <b>{CFG["FOOTER_TITLE"]}</b><br>
    {CFG["FOOTER_SUB"]}
</div>
""",
    unsafe_allow_html=True,
)

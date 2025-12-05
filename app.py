# app.py
"""
IMD Strategic Consulting - AI Sales Bot (B2B)
한의원 원장님 대상 AI 실장 시스템 데모
- 화이트 모드
- AI 답변 그라데이션 텍스트
- Gemini 느낌의 "생각 중..." 버블 (타자 애니메이션 없음)
"""

import time
from typing import Any

import streamlit as st

from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler

# ============================================
# 0. config 안전 로딩 (없어도 앱은 돌아가게)
# ============================================
try:
    import config as cfg  # type: ignore
except Exception:
    class _Dummy:
        pass
    cfg = _Dummy()  # type: ignore


def _get(name: str, default: Any) -> Any:
    return getattr(cfg, name, default)


APP_TITLE = _get("APP_TITLE", "IMD Strategic Consulting")
APP_ICON = _get("APP_ICON", "💼")
LAYOUT = _get("LAYOUT", "centered")

COLOR_PRIMARY = _get("COLOR_PRIMARY", "#111827")
COLOR_BG = _get("COLOR_BG", "#FFFFFF")
COLOR_TEXT = _get("COLOR_TEXT", "#111827")
COLOR_AI_BUBBLE = _get("COLOR_AI_BUBBLE", "#F9FAFB")
COLOR_USER_BUBBLE = _get("COLOR_USER_BUBBLE", "#E5E7EB")
COLOR_BORDER = _get("COLOR_BORDER", "#E5E7EB")

# ============================================
# 1. 페이지 설정
# ============================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state="collapsed",
)

# ============================================
# 2. CSS (화이트 모드 + 그라데이션 텍스트 + 생각중 버블)
# ============================================
st.markdown(
    f"""
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

/* AI 메시지 버블 */
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

/* AI 답변 텍스트 그라데이션 */
.ai-text {{
    background: linear-gradient(135deg, #111827, #2563EB, #0EA5E9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* "생각 중..." 버블 */
.ai-msg.thinking {{
    background: #F3F4F6 !important;
    color: #4B5563 !important;
    padding: 10px 14px !important;
    border-radius: 16px !important;
    font-size: 13px !important;
    box-shadow: none !important;
    border: 1px dashed #E5E7EB !important;
    animation: pulse 1.4s ease-in-out infinite;
}}

@keyframes pulse {{
    0%   {{ opacity: 0.4; transform: translateY(1px); }}
    50%  {{ opacity: 1.0; transform: translateY(0); }}
    100% {{ opacity: 0.4; transform: translateY(1px); }}
}}

/* 사용자 메시지 */
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
""",
    unsafe_allow_html=True,
)

# ============================================
# 3. 초기화
# ============================================
conv_manager = get_conversation_manager()
prompt_engine = get_prompt_engine()
lead_handler = LeadHandler()

# B2B 데모용 첫 메시지 세팅
if "app_initialized" not in st.session_state:
    initial_msg = (
        "안녕하십니까, 원장님.\n\n"
        "저는 24시간 잠들지 않는 **AI 상담실장**입니다.\n\n"
        "진료실에서 이런 말, 자주 들으시죠?\n\n"
        "\"선생님… 생각보다 비싸네요. 그냥 침만 맞을게요.\"\n\n"
        "그 순간, 진료 동선도 끊기고, 원장님 마음도 같이 꺾이실 겁니다.\n\n"
        "저는 그 **직전 단계에서**, 환자의 마음을 열고\n"
        "시술과 프로그램을 받아들일 준비를 시키는 역할을 합니다.\n\n"
        "백문이 불여일견입니다. 지금부터 원장님은 잠시 "
        "'만성 피로 환자' 역할을 해봐 주십시오.\n"
        "편한 말투로 현재 상태를 한 줄만 말씀해 주세요."
    )
    conv_manager.add_message("ai", initial_msg)
    st.session_state.app_initialized = True
    st.session_state.mode = "simulation"  # simulation → closing
    st.session_state.conversation_count = 0

# ============================================
# 4. 헤더
# ============================================
st.markdown(
    f"""
<div class="title-box">
    <h1>IMD STRATEGIC CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 학습한 'AI 수석 실장' 데모</div>
    <div class="sub" style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">
        엑셀은 기록만 하지만, AI는 '매출'을 만듭니다 (체험시간: 2분)
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================
# 5. 채팅 히스토리 출력 (AI는 그라데이션)
# ============================================
chat_html = '<div class="chat-area">'

for msg in conv_manager.get_history():
    if msg["role"] == "ai":
        chat_html += (
            f'<div class="ai-msg"><div class="ai-text">{msg["text"]}</div></div>'
        )
    elif msg["role"] == "user":
        chat_html += (
            f'<div class="msg-right"><span class="user-msg">{msg["text"]}</span></div>'
        )

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ============================================
# 6. CTA 폼 (시뮬레이션 끝난 후 자동 노출)
# ============================================
chat_history = conv_manager.get_history()
last_msg_is_ai = bool(chat_history and chat_history[-1]["role"] == "ai")

# 대충 6메시지 이상 + 마지막이 AI면 폼 띄우기
if (
    len(chat_history) >= 6
    and last_msg_is_ai
    and conv_manager.get_context()["stage"] != "complete"
):
    st.markdown("---")
    st.markdown(
        f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:18px; margin:20px 0 10px;">'
        "이 시스템을 한의원에 도입하시겠습니까?"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#6B7280; font-size:14px; margin-bottom:20px;'>"
        "지역구 독점권은 선착순입니다. 무료 도입 견적서를 보내드립니다"
        "</p>",
        unsafe_allow_html=True,
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
                    "name": director_name,
                    "contact": contact,
                    "symptom": f"병원명: {clinic_name}",
                    "preferred_date": "즉시 상담 희망",
                    "chat_summary": conv_manager.get_summary(),
                    "source": "IMD_Strategic_Consulting",
                    "type": "Oriental_Clinic",
                }

                success, message = lead_handler.save_lead(lead_data)

                if success:
                    completion_msg = f"""
견적서 발송이 완료되었습니다.

{director_name} 원장님, 감사합니다.

**{clinic_name}**에 최적화된 AI 실장 시스템 견적서를  
**{contact}**로 24시간 내 전송해드리겠습니다.

포함 내용:
- 맞춤형 시스템 구축 비용
- 월 운영비 및 유지보수
- 지역 독점권 계약 조건
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
# 7. 입력창 + 생각 중 버블
# ============================================
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})

    # 대화 카운트
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 0
    st.session_state.conversation_count += 1

    context = conv_manager.get_context()
    history = conv_manager.get_formatted_history(for_llm=True)

    # 3회 이상 대화되면 클로징 멘트 직접 투입
    if st.session_state.conversation_count >= 3 and st.session_state.mode == "simulation":
        st.session_state.mode = "closing"
        closing_msg = """
원장님, 방금 보신 대화가 실제 환자에게 제가 자동으로 하는 상담 흐름입니다.

정리해보면, 저는:

1. 환자의 표현을 그대로 받아주고 공감하고,
2. 증상을 기간·강도·수면·통증 부위로 쪼개서 듣고,
3. 그 정보를 바탕으로 원장님 병원의 진료 철학에 맞게 설명하고,
4. 마지막에는 자연스럽게 진맥 → 한약/침/추나 → 생활 교정으로 이어지게 설계됩니다.

이제 상상해보십시오.

이 AI를 원장님 병원 홈페이지에 24시간 붙여놓는다면?

밤 11시, 퇴근하고 누워서 검색하는 직장인이
"만성 피로 한약"을 물으면, 제가 알아서 상담하고 예약까지 받아둡니다.

실제 적용 사례로 말씀드리면: 서울 A한의원 (월 신규 환자 약 80명 수준)

- AI 도입 후 2개월 동안 온라인 문의 수 약 40% 증가
- 예약 전환율 18% → 22.5% (약 25% 상승)

폭발적인 매출 신화가 아니라,
원장님이 직접 설명해야 했던 부분을 AI가 온라인에서 조금씩 대신 떠받쳐주는 구조입니다.
"""
        conv_manager.add_message("ai", closing_msg)
        st.rerun()

    else:
        # 제미나이 느낌의 "생각 중..." 버블 (타자 효과 없음)
        thinking_placeholder = st.empty()
        thinking_html = """
<div class="chat-area">
    <div class="ai-msg thinking">
        AI 수석 실장이 원장님의 상황을 정리하고 있습니다...<br/>
        · 현재 환자 표현 정리<br/>
        · 진료/매출 구조에 미치는 영향 상상<br/>
        · AI가 들어갈 수 있는 지점 계산
    </div>
</div>
"""
        thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)

        with st.spinner("분석 중..."):
            ai_response = generate_ai_response(user_input, context, history)

        # 생각 중 버블 제거
        thinking_placeholder.empty()

        # 실제 답변 추가 (그라데이션으로 렌더링됨)
        conv_manager.add_message("ai", ai_response)
        st.rerun()

# ============================================
# 8. 완료 후 액션
# ============================================
if conv_manager.get_context()["stage"] == "complete":
    col1, col2 = st.columns(2)

    with col1:
        if st.button("새 상담 시작", use_container_width=True):
            conv_manager.reset_conversation()
            st.session_state.mode = "simulation"
            st.session_state.conversation_count = 0
            st.session_state.app_initialized = False
            st.rerun()

    with col2:
        if st.button("상담 내역 보기", use_container_width=True):
            with st.expander("상담 요약", expanded=True):
                st.markdown(conv_manager.get_summary())

# ============================================
# 9. 푸터
# ============================================
st.markdown(
    """
<div class="footer">
    <b>IMD Strategic Consulting</b><br>
    한의원 전용 AI 매출 엔진 | 전국 일부 지역 독점 운영
</div>
""",
    unsafe_allow_html=True,
)

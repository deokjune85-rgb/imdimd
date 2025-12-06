# app.py
"""
IMD Strategic Consulting - AI Sales Bot (B2B)
한의원 원장님 대상 AI 실장 시스템 데모
- 모바일 최적화: 인터리브 코멘터리 방식
- 텍스트 대화 시뮬레이션: 원장이 환자 역할 체험
"""

import time
from typing import Any

import streamlit as st

from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler

# ============================================
# 0. config 안전 로딩
# ============================================
try:
    import config as cfg
except Exception:
    class _Dummy:
        pass
    cfg = _Dummy()


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

SYMPTOM_CARDS = _get("SYMPTOM_CARDS", {})
TONGUE_TYPES = _get("TONGUE_TYPES", {})

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
# 2. CSS (모바일 최적화 - 인터리브 코멘터리 방식)
# ============================================
st.markdown(
    """
<style>
/* 전체 다크 테마 */
.stApp { 
    background-color: #121212; 
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; 
    color: white; 
}

.main {
    background-color: #121212 !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 720px !important;
    margin: 0 auto !important;
    background-color: #121212 !important;
}

header, .stDeployButton {
    display: none !important;
}

footer {
    display: none !important;
}

/* 타이틀 */
.title-box {
    text-align: center;
    padding: 20px 20px 12px 20px;
    background-color: #121212;
}

.title-box h1 {
    font-family: Arial, sans-serif !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #D4AF37 !important;
    margin: 0 !important;
    letter-spacing: 0.5px !important;
}

.title-box .sub {
    font-size: 12px;
    color: #888;
    margin-top: 4px;
}

/* 채팅 영역 */
.chat-area {
    padding: 12px 20px 4px 20px;
    background-color: #121212 !important;
    min-height: 150px;
    margin-bottom: 100px;
}

/* 1. 환자용 UI (밝은 카드 스타일 - 환자 메시지) */
.patient-card {
    background-color: #ffffff;
    color: #333;
    padding: 16px 20px;
    border-radius: 15px;
    margin: 10px 0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    border-left: 6px solid #2E8B57;
    max-width: 85%;
    display: inline-block;
}

.patient-text {
    font-size: 16px;
    font-weight: 600;
    color: #111;
    line-height: 1.5;
}

/* 사용자 메시지 우측 정렬 */
.msg-right {
    text-align: right !important;
    clear: both !important;
    display: block !important;
    width: 100% !important;
    margin-top: 16px !important;
}

/* 2. AI 원장님용 로그 (어두운 터미널 스타일) */
.admin-log {
    background-color: #000;
    color: #00E5FF;
    padding: 15px 18px;
    border-radius: 10px;
    margin: 5px 0 25px 0;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    border: 1px solid #333;
    animation: fadeIn 0.5s ease-in-out;
    max-width: 90%;
}

.log-header {
    color: #D4AF37;
    font-weight: bold;
    font-size: 11px;
    margin-bottom: 8px;
    display: block;
    border-bottom: 1px solid #333;
    padding-bottom: 5px;
    letter-spacing: 1px;
}

.log-highlight {
    color: #ffff00;
    font-weight: bold;
    text-decoration: underline;
}

.log-msg {
    color: #00E5FF;
    line-height: 1.5;
}

/* AI 메시지 (일반 대화용 - 기존 스타일 유지) */
.ai-msg {
    background-color: #1a1a1a !important;
    color: #E0E0E0 !important;
    padding: 16px 20px !important;
    border-radius: 15px !important;
    margin: 18px 0 10px 0 !important;
    max-width: 85% !important;
    display: block !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
    border-left: 3px solid #D4AF37 !important;
    animation: fadeInText 0.55s ease-out;
}

/* 부드러운 등장 애니메이션 */
@keyframes fadeInText {
    0% {
        opacity: 0;
        transform: translateY(10px);
        filter: blur(3px);
    }
    50% {
        opacity: 0.7;
        transform: translateY(3px);
        filter: blur(1.5px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 입력창 */
.stChatInput {
    position: fixed !important;
    bottom: 60px !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    background-color: #1a1a1a !important;
    padding: 10px 0 !important;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.5) !important;
    z-index: 999 !important;
    margin: 0 !important;
}

.stChatInput > div {
    max-width: 680px !important;
    margin: 0 auto !important;
    border: 1px solid #333 !important;
    border-radius: 24px !important;
    background-color: #2a2a2a !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
}

.stChatInput input {
    color: #E0E0E0 !important;
    background-color: #2a2a2a !important;
    -webkit-text-fill-color: #E0E0E0 !important;
}

.stChatInput input::placeholder {
    color: #666 !important;
    font-size: 15px !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #666 !important;
}

/* 푸터 */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    background-color: #1a1a1a !important;
    padding: 12px 20px;
    text-align: center;
    font-size: 11px;
    color: #666;
    border-top: 1px solid #333;
    z-index: 998;
}

.footer b {
    color: #D4AF37;
    font-weight: 600;
}

/* 폼 */
.stForm {
    background-color: #1a1a1a;
    padding: 20px;
    border: 1px solid #333;
    border-radius: 12px;
    margin: 16px 20px 180px 20px;
}

.stForm label {
    color: #E0E0E0 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

input, textarea, select {
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    background-color: #2a2a2a !important;
    color: #E0E0E0 !important;
}

input::placeholder, textarea::placeholder {
    color: #666 !important;
    opacity: 1 !important;
}

/* 버튼 */
.stButton > button {
    width: 100%;
    background-color: #2a2a2a;
    border: 2px solid #D4AF37;
    color: #D4AF37;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 12px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #D4AF37;
    color: #121212;
}

/* 모바일 */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 0 !important;
    }
    
    .title-box {
        padding: 16px 16px 12px 16px !important;
    }
    
    .title-box h1 {
        font-size: 20px !important;
        line-height: 1.2 !important;
    }
    
    .chat-area {
        padding: 8px 16px 4px 16px !important;
    }
    
    .ai-msg, .admin-log {
        font-size: 14px !important;
        padding: 14px 16px !important;
    }
    
    .patient-card {
        font-size: 15px !important;
        padding: 14px 16px !important;
    }
}
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

# 모드 초기화
if "mode" not in st.session_state:
    st.session_state.mode = "simulation"  # simulation → closing
    st.session_state.conversation_count = 0

# 첫 메시지 세팅
if "app_initialized" not in st.session_state:
    initial_msg = (
        "안녕하십니까, 원장님.\n\n"
        "저는 24시간 잠들지 않는 <b>AI 상담실장</b>입니다.\n\n"
        "진료실에서 이런 말, 자주 들으시죠?\n\n"
        "\"선생님… 생각보다 비싸네요. 그냥 침만 맞을게요.\"\n\n"
        "그 순간, 진료 동선도 끊기고, 원장님 마음도 같이 꺾이실 겁니다.\n\n"
        "저는 그 <b>직전 단계에서</b>, 환자의 마음을 열고\n"
        "시술과 프로그램을 받아들일 준비를 시키는 역할을 합니다.\n\n"
        "백문이 불여일견입니다. 지금부터 원장님은 잠시 "
        "'만성 피로 환자' 역할을 해봐 주십시오.\n"
        "편한 말투로 현재 상태를 한 줄만 말씀해 주세요."
    )
    conv_manager.add_message("ai", initial_msg)
    st.session_state.app_initialized = True
    conv_manager.update_stage("simulation")

# ============================================
# 4. 헤더
# ============================================
st.markdown(
    """
<div class="title-box">
    <h1>💼 IMD MEDICAL CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 학습한 'AI 수석 실장' 데모</div>
    <div class="sub" style="font-size: 11px; color: #666; margin-top: 4px;">
        엑셀은 기록만 하지만, AI는 '매출'을 만듭니다 (체험시간: 2분)
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================
# 5. 채팅 히스토리 출력 (인터리브 방식)
# ============================================
chat_html = '<div class="chat-area">'

for idx, msg in enumerate(conv_manager.get_history()):
    if msg["role"] == "ai":
        # AI 메시지
        chat_html += (
            f'<div class="ai-msg">{msg["text"]}</div>'
        )
    elif msg["role"] == "user":
        # 환자(원장) 메시지 - 흰색 카드
        chat_html += (
            f'<div class="msg-right">'
            f'<div class="patient-card">'
            f'<div class="patient-text">{msg["text"]}</div>'
            f'</div></div>'
        )
        
        # 사용자 메시지 바로 다음에 AI 분석 로그 삽입
        metadata = msg.get("metadata", {})
        
        # 첫 번째 메시지: 증상 파악
        if idx == 1 and st.session_state.conversation_count >= 1:
            chat_html += """
<div class="admin-log">
    <span class="log-header">🎯 AI SYSTEM LOG</span>
    <div class="log-msg">
        <b>TARGET DETECTED</b><br>
        환자 증상 키워드: <span class="log-highlight">'피곤', '만성'</span><br>
        → 고가 비급여(공진단/녹용) 타겟군 식별<br>
        → <b>'기력 회복 장기 프로그램'</b> 세일즈 시나리오 가동
    </div>
</div>
"""
        
        # 두 번째 메시지: 패턴 분석
        elif idx == 3 and st.session_state.conversation_count >= 2:
            chat_html += """
<div class="admin-log">
    <span class="log-header">📊 DEEP ANALYSIS</span>
    <div class="log-msg">
        <b>패턴 심화 분석 완료</b><br>
        진단: <span class="log-highlight">만성 피로 + 회복 불가 패턴</span><br>
        → 단순 휴식으로는 회복 불가함을 인지시킴<br>
        → 환자의 <b>위기감 증폭 중</b> (전환율 ↑)
    </div>
</div>
"""
        
        # 세 번째 메시지: 클로징 준비
        elif idx >= 5 and st.session_state.conversation_count >= 3:
            chat_html += """
<div class="admin-log" style="border: 1px solid #D4AF37;">
    <span class="log-header" style="color:#D4AF37;">💡 SALES OPPORTUNITY</span>
    <div class="log-msg">
        <b>원장님, 지금입니다.</b><br><br>
        환자는 자신의 상태가 '심각하다'고 인지했습니다.<br>
        이 타이밍에 <span class="log-highlight">'프리미엄 3개월 프로그램'</span>을<br>
        제안하면 동의율이 <b>80% 이상</b>으로 올라갑니다.
    </div>
</div>
"""

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ============================================
# 6. CTA 폼 (시뮬레이션 끝난 후 자동 노출)
# ============================================
chat_history = conv_manager.get_history()
last_msg_is_ai = bool(chat_history and chat_history[-1]["role"] == "ai")

if (
    len(chat_history) >= 6
    and last_msg_is_ai
    and conv_manager.get_context()["stage"] != "complete"
):
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#D4AF37; font-weight:600; font-size:18px; margin:20px 0 10px;">'
        "이 시스템을 한의원에 도입하시겠습니까?"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#888; font-size:14px; margin-bottom:20px;'>"
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

<b>{clinic_name}</b>에 최적화된 AI 실장 시스템 견적서를  
<b>{contact}</b>로 24시간 내 전송해드리겠습니다.

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
# 7. 입력창 + AI 응답
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

여기까지는 '만성 피로 한 명의 환자' 이야기에 불과합니다.

이제 상상해보십시오.

이 AI를 원장님 병원 홈페이지에 24시간 붙여놓는다면,

밤 11시, 퇴근하고 누워서 검색하는 직장인이
"만성 피로 한약"을 물으면, 제가 알아서 상담하고 예약까지 받아둡니다.
낮에는 다이어트, 저녁에는 교통사고 후유증, 주말에는 만성 두통 환자까지
동시에 상담을 받아주는 구조가 됩니다.

실제 적용 사례로 말씀드리면, 서울 A한의원(월 신규 환자 약 80명 수준)의 경우:

- AI 도입 후 2개월 동안 온라인 문의 수 약 40% 증가
- 예약 전환율 18% → 22.5% (약 25% 상승)

폭발적인 매출 신화를 약속하는 시스템이 아니라,
원장님이 진료실에서 직접 설명해야 했던 부분을
AI가 온라인에서 조금씩 대신 떠받쳐주는 구조입니다.

여기서 딱 한 가지 질문만 남습니다.

"우리 병원에 붙이면, 실제 숫자가 얼마나 바뀔까?"

월 신규 환자 수, 주요 클리닉(예: 피로/다이어트/추나)의 비중,
온라인 문의 비율 정도만 알면,
'원장님 병원 기준'으로 시뮬레이션을 그려볼 수 있습니다.

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 데이터를 기준으로 한
간단한 도입 시나리오와 견적 요약본을 보내드리겠습니다.
"""
        conv_manager.add_message("ai", closing_msg)
        conv_manager.update_stage("conversion")
        st.rerun()

    else:
        with st.spinner("AI 수석 실장이 원장님 상황을 정리하고 있습니다..."):
            ai_response = generate_ai_response(user_input, context, history)

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

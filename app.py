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
    COLOR_BORDER,
    TONGUE_TYPES,
)

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
# CSS
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
    
    /* 모바일에서 혀 사진 4개 가로 배열 강제 */
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

/* 에러 메시지 숨기기 */
.stException {{
    display: none !important;
}}

div[data-testid="stException"] {{
    display: none !important;
}}

.element-container:has(.stException) {{
    display: none !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
prompt_engine = get_prompt_engine()
lead_handler = LeadHandler()

ctx = conv_manager.get_context()
if not ctx.get("stage"):
    conv_manager.update_stage("initial")

# ============================================
# B2B 시작 메시지
# ============================================
if "app_initialized" not in st.session_state:
    initial_msg = """안녕하십니까, 원장님.

저는 24시간 잠들지 않는 AI 상담실장입니다.

진료실에서 이런 말, 자주 들으시죠?

"선생님… 생각보다 비싸네요. 그냥 침만 맞을게요."

그 순간, 진료 동선도 끊기고, 원장님 마음도 같이 꺾이실 겁니다.

저는 그 순간 전에, 환자의 마음을 열고, 지갑을 열 준비를 시키는 역할을 합니다.

백문이 불여일견입니다.

지금부터 원장님은 '만성 피로 환자' 역할을 한 번 해봐 주십시오.
제가 어떻게 상담하고, 어떻게 설득하는지 보여드리겠습니다.

편한 말투로 말씀해 주세요.

예를 들면:
- "아 놔, 요즘 진짜 너무 피곤해요"
- "자고 일어나도 피곤이 안 풀려요"
- "커피 안 마시면 머리가 안 돌아가요"

아무 말이나 편하게 한번 던져보시면 됩니다."""
    conv_manager.add_message("ai", initial_msg)
    st.session_state.app_initialized = True
    st.session_state.mode = "simulation"
    st.session_state.conversation_count = 0

# ============================================
# 헤더
# ============================================
st.markdown(
    """
<div class="title-box">
    <h1>IMD STRATEGIC CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 완벽하게 학습한 'AI 수석 실장'을 소개합니다</div>
    <div class="sub" style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">엑셀은 기록만 하지만, AI는 '매출'을 만듭니다 (체험시간: 2분)</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================
# 채팅 히스토리
# ============================================
with st.container():
    chat_html = '<div class="chat-area">'
    for msg in conv_manager.get_history():
        if msg["role"] == "ai":
            chat_html += f'<div class="ai-msg">{msg["text"]}</div>'
        elif msg["role"] == "user":
            chat_html += (
                f'<div class="msg-right"><span class="user-msg">'
                f'{msg["text"]}</span></div>'
            )
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)


# ============================================
# 노이즈(개소리) 판별 함수
# → 이런 건 단계 진행에서 제외
# ============================================
def is_noise_utterance(text: str) -> bool:
    if not text:
        return True

    t = text.strip()
    if not t:
        return True

    # 아주 짧은 추임새 류
    if len(t) <= 2 and t in ["ㅎ", "ㅋㅋ", "ㅎㅎ", "ㅇㅋ", "ok", "굿"]:
        return True

    # 욕 리스트
    bad_words = [
        "씨발",
        "ㅅㅂ",
        "개새끼",
        "개같네",
        "개좆",
        "개좃",
        "좆같",
        "병신",
        "개같은",
        "개좆같은소리",
        "개좃같은소리",
    ]

    # 건강/증상 관련 키워드 (있으면 유효 발화로 취급)
    health_keywords = [
        "허리",
        "목",
        "어깨",
        "똥구멍",
        "항문",
        "배",
        "속",
        "두통",
        "어지럽",
        "불면",
        "잠",
        "피곤",
        "통증",
        "소화",
        "다리",
        "발",
        "발톱",
        "내성발톱",
        "골반",
        "무릎",
        "가슴",
        "심장",
        "두근",
    ]

    has_bad = any(b in t for b in bad_words)
    has_health = any(h in t for h in health_keywords)

    # 욕만 있고 증상 키워드는 없으면 노이즈
    if has_bad and not has_health:
        return True

    # 그 외는 유효 발화
    return False


# ============================================
# 혀 사진 선택 UI
#  - stage 안 믿고, 마지막 AI 멘트에 "혀" + "선택/사진/거울" 있으면 표시
# ============================================
context = conv_manager.get_context()
chat_history = conv_manager.get_history()

last_ai_text = (
    chat_history[-1]["text"]
    if chat_history and chat_history[-1]["role"] == "ai"
    else ""
)

show_tongue_ui = (
    not context.get("selected_tongue")
    and chat_history
    and chat_history[-1]["role"] == "ai"
    and ("혀" in last_ai_text)
    and ("선택" in last_ai_text or "사진" in last_ai_text or "거울" in last_ai_text)
)

if show_tongue_ui:
    from PIL import Image

    with st.container():
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; '
            f'font-weight:600; font-size:20px; margin:4px 0 8px 0;">'
            "거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요</div>",
            unsafe_allow_html=True,
        )

        cols = st.columns(4)

        for idx, (tongue_key, tongue_data) in enumerate(TONGUE_TYPES.items()):
            with cols[idx]:
                image_path = tongue_data["image"]
                try:
                    img = Image.open(image_path)
                    st.image(img, use_container_width=True)
                except Exception:
                    st.markdown(
                        f"<div style='text-align:center; font-size:80px; "
                        f"padding:20px 0;'>{tongue_data['emoji']}</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    "<div style='text-align:center; font-size:13px; "
                    "font-weight:600; margin:4px 0; color:#1F2937;'>"
                    f"{tongue_data['name']}</div>",
                    unsafe_allow_html=True,
                )

                if st.button(
                    "선택", key=f"tongue_{tongue_key}", use_container_width=True
                ):
                    conv_manager.update_context("selected_tongue", tongue_key)
                    conv_manager.update_stage("conversion")

                    diagnosis_msg = (
                        f"**{tongue_data['name']}** 선택하셨습니다.\n\n"
                        f"{tongue_data['analysis']}\n\n"
                        f"**주요 증상**: {tongue_data['symptoms']}\n\n"
                        f"⚠️ **경고**: {tongue_data['warning']}\n\n"
                        "---\n\n"
                        "원장님, 방금 보신 과정이 실제로 제가 환자에게 자동으로 진행하는 흐름입니다.\n\n"
                        "**제가 한 일:**\n"
                        "1. 환자의 증상을 구체적으로 쪼개서 물었습니다.\n"
                        "2. 수면과 소화 패턴을 함께 보면서 '버티고 있는 몸'인지 확인했습니다.\n"
                        "3. 혀 상태를 통해 환자 스스로 '내 몸이 생각보다 심각하구나'를 깨닫게 만들었습니다.\n\n"
                        "이 대화를 원장님 병원 홈페이지에 24시간 붙여두면,\n"
                        "밤 11시, 검색창에 '만성피로 한의원'을 치는 직장인에게 제가 알아서:\n"
                        "- 증상을 듣고,\n- 위기감을 조성하고,\n"
                        "- '이 정도면 한약이 필요합니다' 단계까지 끌어올린 뒤,\n"
                        "- 예약이나 연락처 남기기까지 유도합니다."
                    )

                    conv_manager.add_message("ai", diagnosis_msg)
                    conv_manager.calculate_health_score()
                    st.rerun()

        st.markdown("<div style='height:150px;'></div>", unsafe_allow_html=True)


# ============================================
# CTA (conversion 단계)
# ============================================
current_stage = conv_manager.get_context().get("stage")
selected_tongue = conv_manager.get_context().get("selected_tongue")

if current_stage == "conversion" and selected_tongue and current_stage != "complete":
    with st.container():
        st.markdown("---")
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; '
            f'font-size:18px; margin:20px 0 10px;">'
            "이 시스템을 한의원에 도입하시겠습니까?</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center; color:#6B7280; font-size:14px; "
            "margin-bottom:20px;'>지역구 독점권은 선착순입니다. "
            "무료 도입 견적서를 보내드립니다</p>",
            unsafe_allow_html=True,
        )

        with st.form("consulting_form"):
            col1, col2 = st.columns(2)
            with col1:
                clinic_name = st.text_input("병원명", placeholder="서울한의원")
            with col2:
                director_name = st.text_input("원장님 성함", placeholder="홍길동")

            contact = st.text_input("연락처 (직통)", placeholder="010-1234-5678")

            submitted = st.form_submit_button(
                "무료 도입 견적서 받기", use_container_width=True
            )

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

{clinic_name}에 최적화된 AI 실장 시스템 견적서를 
{contact}로 24시간 내 전송해드리겠습니다.

포함 내용:
- 맞춤형 시스템 구축 비용
- 월 운영비 및 유지보수
- 지역 독점권 계약 조건
- ROI 예상 시뮬레이션

담당 컨설턴트가 직접 연락드리겠습니다.
"""
                        conv_manager.add_message("ai", completion_msg)
                        conv_manager.update_stage("complete")

                        st.success("견적서 신청이 완료되었습니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"오류: {message}")


# ============================================
# 입력창 + LLM 호출
#  - 여기서 노이즈면 stage 그대로 유지
# ============================================
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    # 유저 메시지 저장
    conv_manager.add_message("user", user_input, metadata={"type": "text"})

    # 카운트
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 0
    st.session_state.conversation_count += 1

    context = conv_manager.get_context()
    current_stage = context.get("stage", "initial")
    history_for_llm = conv_manager.get_formatted_history(for_llm=True)

    # LLM 호출
    raw_output = generate_ai_response(user_input, context, history_for_llm)

    # [[STAGE:...]] 태그 파싱
    next_stage = current_stage
    ai_text = raw_output

    if "[[STAGE:" in raw_output:
        body, tail = raw_output.rsplit("[[STAGE:", 1)
        ai_text = body.strip()
        stage_tag = tail.split("]]", 1)[0].strip()
        if stage_tag:
            next_stage = stage_tag

    # 🔴 욕/개소리면: 단계 진행 막고, 현재 stage 유지
    if is_noise_utterance(user_input):
        next_stage = current_stage

    conv_manager.add_message("ai", ai_text)
    conv_manager.update_stage(next_stage)

    st.rerun()

# ============================================
# 완료 후
# ============================================
if conv_manager.get_context().get("stage") == "complete":
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
st.markdown(
    """
<div class="footer">
    <b>IMD Strategic Consulting</b><br>
    한의원 전용 AI 매출 엔진 | 전국 200개 한의원 도입 완료
</div>
""",
    unsafe_allow_html=True,
)

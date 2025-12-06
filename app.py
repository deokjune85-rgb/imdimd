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

# ============================================
# 0. config 안전 로딩 (먼저 로드)
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

# 모듈 import (config 로드 후)
from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler

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
# 2. CSS (화이트 모드 - 제미나이 스타일 + 폰트 2pt 증가)
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
    font-size: 30px !important;  /* 28px → 30px */
    font-weight: 700 !important;
    color: {COLOR_PRIMARY} !important;
    margin: 0 !important;
    letter-spacing: 0.5px !important;
    white-space: nowrap !important;
}}

.title-box .sub {{
    font-size: 14px !important;  /* 12px → 14px */
    color: #4B5563;
    margin-top: 4px;
}}

/* 채팅 영역 */
.chat-area {{
    padding: 12px 20px 4px 20px;
    background: white !important;
    min-height: 150px;
    margin-bottom: 200px !important;  /* 하단 여백 증가 */
}}

/* 모바일에서도 columns를 가로로 유지 */
[data-testid="column"] {{
    min-width: 0 !important;
    flex: 1 !important;
}}

/* AI 메시지 버블 */
.ai-msg {{
    background: white !important;
    color: #111827 !important;
    padding: 16px 20px !important;
    border-radius: 18px 18px 18px 4px !important;
    margin: 18px 0 10px 0 !important;
    max-width: 85% !important;
    display: block !important;
    font-size: 20px !important;  /* 18px → 20px */
    line-height: 1.6 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
    border: none !important;
    outline: none !important;
    clear: both !important;
    animation: fadeInText 0.55s ease-out;
}}

.ai-msg::before, .ai-msg::after {{
    content: none !important;
    display: none !important;
}}

/* AI 텍스트 (검은색 유지) */
.ai-text {{
    color: #111827 !important;
}}

/* 부드러운 그라데이션 느낌의 등장 애니메이션 */
@keyframes fadeInText {{
    0% {{
        opacity: 0;
        transform: translateY(10px);
        filter: blur(3px);
    }}
    50% {{
        opacity: 0.7;
        transform: translateY(3px);
        filter: blur(1.5px);
    }}
    100% {{
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }}
}}

/* 사용자 메시지 (흰색 카드) */
.patient-card {{
    background: {COLOR_USER_BUBBLE} !important;
    color: #111827 !important;
    padding: 14px 20px !important;  /* 12px → 14px */
    border-radius: 18px 18px 4px 18px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    display: inline-block !important;
    font-size: 18px !important;  /* 16px → 18px */
    line-height: 1.4 !important;
    border: none !important;
    outline: none !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
}}

.patient-text {{
    color: #111827 !important;
}}

.msg-right {{
    text-align: right !important;
    clear: both !important;
    display: block !important;
    width: 100% !important;
    margin-top: 16px !important;
}}

/* AI 분석 로그 (연한 회색 배경) */
.admin-log {{
    background: #F9FAFB !important;
    color: #1F2937 !important;
    padding: 16px 20px !important;
    border-radius: 12px !important;
    margin: 8px 0 20px 0 !important;
    max-width: 90% !important;
    font-family: 'Courier New', monospace;
    font-size: 15px !important;  /* 13px → 15px */
    line-height: 1.6 !important;
    border: 1px solid #E5E7EB !important;
    animation: fadeIn 0.5s ease-in-out;
}}

.log-header {{
    color: #059669 !important;  /* 초록색 */
    font-weight: bold;
    font-size: 13px !important;  /* 11px → 13px */
    margin-bottom: 8px;
    display: block;
    border-bottom: 1px solid #E5E7EB;
    padding-bottom: 5px;
    letter-spacing: 1px;
}}

.log-highlight {{
    color: #DC2626 !important;  /* 빨간색 */
    font-weight: bold;
    text-decoration: underline;
}}

.log-msg {{
    color: #1F2937 !important;
    line-height: 1.6;
}}

@keyframes fadeIn {{
    from {{
        opacity: 0;
        transform: translateY(-10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
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
    font-size: 17px !important;  /* 15px → 17px */
    -webkit-text-fill-color: #1F2937 !important;
}}

.stChatInput input::placeholder {{
    color: #D1D5DB !important;
    font-size: 17px !important;  /* 15px → 17px */
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
    font-size: 13px !important;  /* 11px → 13px */
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
    font-size: 16px !important;  /* 14px → 16px */
}}

input, textarea, select {{
    border: 1px solid {COLOR_BORDER} !important;
    border-radius: 8px !important;
    background: white !important;
    color: #1F2937 !important;
    font-size: 16px !important;  /* +2px */
}}

input::placeholder, textarea::placeholder {{
    color: #D1D5DB !important;
    opacity: 1 !important;
}}

/* 버튼 */
.stButton > button {{
    width: 100%;
    background: white;
    border: 2px solid {COLOR_PRIMARY};
    color: {COLOR_PRIMARY};
    font-weight: 600;
    font-size: 16px !important;  /* +2px */
    padding: 12px 24px;
    border-radius: 12px;
    transition: all 0.3s ease;
}}

.stButton > button:hover {{
    background: {COLOR_PRIMARY};
    color: white;
}}

/* 혀 선택 버튼 - 모바일에서 작게 */
@media (max-width: 768px) {{
    .stButton > button {{
        font-size: 11px !important;
        padding: 8px 4px !important;
        line-height: 1.2 !important;
    }}
}}

/* 모바일 */
@media (max-width: 768px) {{
    .main .block-container {{
        padding-top: 0 !important;
    }}
    
    /* 모바일에서도 4개 columns 가로 유지 */
    [data-testid="column"] {{
        min-width: 0 !important;
        width: 25% !important;
        flex: 0 0 25% !important;
        max-width: 25% !important;
    }}
    
    .title-box {{
        padding: 2px 16px 2px 16px !important;
    }}
    
    .title-box h1 {{
        font-size: 24px !important;  /* 22px → 24px */
        line-height: 1.1 !important;
    }}
    
    .chat-area {{
        padding: 2px 16px 4px 16px !important;
        margin-bottom: 250px !important;  /* 모바일 하단 여백 더 증가 */
    }}
    
    .ai-msg {{
        font-size: 18px !important;  /* 16px → 18px */
        padding: 14px 18px !important;
    }}
    
    .patient-card {{
        font-size: 17px !important;  /* 15px → 17px */
    }}
    
    .admin-log {{
        font-size: 14px !important;  /* 12px → 14px */
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

# 모드 초기화
if "mode" not in st.session_state:
    st.session_state.mode = "simulation"  # simulation → closing
    st.session_state.conversation_count = 0

# 첫 메시지 세팅
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
    st.session_state.app_initialized = True
    conv_manager.update_stage("symptom_explore")

# ============================================
# 4. 헤더
# ============================================
st.markdown(
    f"""
<div class="title-box">
    <h1>IMD MEDICAL CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 학습한 'AI 수석 실장' 데모</div>
    <div class="sub" style="font-size: 13px; color: #6B7280; margin-top: 4px;">
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
        
        # 혀 선택 직후 AI 메시지라면 선택된 사진 크게 표시
        if idx > 0 and st.session_state.get("selected_tongue_type"):
            prev_msg = conv_manager.get_history()[idx - 1]
            if prev_msg.get("role") == "user" and "[선택:" in prev_msg.get("text", ""):
                tongue_type = st.session_state.selected_tongue_type
                if tongue_type in TONGUE_TYPES:
                    info = TONGUE_TYPES[tongue_type]
                    image_path = info.get('image', '')
                    if image_path:
                        # HTML로 넣지 말고 st.image로 출력
                        st.markdown(
                            f"<div style='text-align:center; margin: 20px 0;'>"
                            f"<div style='font-size: 16px; color: #059669; font-weight: 700; margin-bottom: 10px;'>✅ 선택하신 혀: {info['name']}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        st.image(image_path, use_container_width=True)
        
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
        <b>[분석] 기상 직후 피로 호소</b><br>
        → 단순 과로 아님. 수면의 질 저하 또는 <span class="log-highlight">'기허(氣虛)'</span> 의심<br>
        → 다음 단계: 소화기능 및 수면패턴 추적 필요
    </div>
</div>
"""
        
        # 두 번째 메시지: 변증 심화
        elif idx == 3 and st.session_state.conversation_count >= 2:
            chat_html += """
<div class="admin-log">
    <span class="log-header">📊 DEEP ANALYSIS</span>
    <div class="log-msg">
        <b>[Logic] 식곤증 + 만성피로</b><br>
        = <span class="log-highlight">비위(소화기) 기능 저하</span>로 인한 기혈 생성 실패<br>
        <b>[진단명]</b> 비기허(脾氣虛) 및 습담(濕痰) 정체 유력<br>
        → 설진(혀 진단)으로 확증 필요
    </div>
</div>
"""
        
        # 세 번째 메시지: 클로징 준비
        elif idx >= 5 and st.session_state.conversation_count >= 3:
            chat_html += """
<div class="admin-log" style="border: 2px solid #059669;">
    <span class="log-header" style="color:#059669;">💡 SALES OPPORTUNITY</span>
    <div class="log-msg">
        <b>[전략] 단순 침 치료(1만원) 불가 판정</b><br>
        → 고가 패키지(공진단/녹용) 제안 명분 확보<br><br>
        <span class="log-highlight">환자는 자신의 몸이 심각함을 인지했습니다.</span><br>
        이 타이밍에 <b>'집중 면역 프로그램'</b> 제안 시<br>
        동의율 <b>80% 이상</b>으로 상승
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

# 현재 대화 단계 확인
current_stage = conv_manager.get_context().get("stage", "symptom_explore")

# 혀 선택 단계인 경우 → 버튼 UI 표시
if current_stage == "tongue_select" and not st.session_state.get("tongue_selected"):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; color:#1F2937; font-weight:600; font-size:18px; margin:20px 0;'>"
        "거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요"
        "</div>",
        unsafe_allow_html=True,
    )
    
    # 가로 4장 일렬 배치
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # 담백설
        tongue_type = '담백설'
        if tongue_type in TONGUE_TYPES:
            info = TONGUE_TYPES[tongue_type]
            image_path = info.get('image', '')
            
            if image_path:
                try:
                    st.image(image_path, use_container_width=True)
                except Exception:
                    st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            
            if st.button(f"{info['visual']}", key="btn_담백설", use_container_width=True):
                st.session_state.tongue_selected = True
                st.session_state.selected_tongue_type = tongue_type
                conv_manager.update_context("selected_tongue", tongue_type)
                conv_manager.add_message("user", f"[선택: {info['visual']}]")
                
                analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

{info['analysis']}

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 (기허 의심)
2. "식사 후 졸리세요?" → 소화기능 저하 확인 (비기허 변증)
3. 혀 사진 선택 → <b>시각적 증거 확보</b> (환자 스스로 인정)

저는 환자의 말을 그냥 듣지 않습니다.
<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
'약을 먹을 수밖에 없는 몸 상태'임을 스스로 인정하게 만듭니다.

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- <b>핵심</b>: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
                conv_manager.add_message("ai", analysis_msg)
                conv_manager.update_stage("conversion")
                st.session_state.mode = "closing"
                st.rerun()
    
    with c2:
        # 황태설
        tongue_type = '황태설'
        if tongue_type in TONGUE_TYPES:
            info = TONGUE_TYPES[tongue_type]
            image_path = info.get('image', '')
            
            if image_path:
                try:
                    st.image(image_path, use_container_width=True)
                except Exception:
                    st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            
            if st.button(f"{info['visual']}", key="btn_황태설", use_container_width=True):
                st.session_state.tongue_selected = True
                st.session_state.selected_tongue_type = tongue_type
                conv_manager.update_context("selected_tongue", tongue_type)
                conv_manager.add_message("user", f"[선택: {info['visual']}]")
                
                analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

{info['analysis']}

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 (기허 의심)
2. "식사 후 졸리세요?" → 소화기능 저하 확인 (비기허 변증)
3. 혀 사진 선택 → <b>시각적 증거 확보</b> (환자 스스로 인정)

저는 환자의 말을 그냥 듣지 않습니다.
<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
'약을 먹을 수밖에 없는 몸 상태'임을 스스로 인정하게 만듭니다.

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- <b>핵심</b>: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
                conv_manager.add_message("ai", analysis_msg)
                conv_manager.update_stage("conversion")
                st.session_state.mode = "closing"
                st.rerun()
    
    with c3:
        # 치흔설
        tongue_type = '치흔설'
        if tongue_type in TONGUE_TYPES:
            info = TONGUE_TYPES[tongue_type]
            image_path = info.get('image', '')
            
            if image_path:
                try:
                    st.image(image_path, use_container_width=True)
                except Exception:
                    st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            
            if st.button(f"{info['visual']}", key="btn_치흔설", use_container_width=True):
                st.session_state.tongue_selected = True
                st.session_state.selected_tongue_type = tongue_type
                conv_manager.update_context("selected_tongue", tongue_type)
                conv_manager.add_message("user", f"[선택: {info['visual']}]")
                
                analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

혀 가장자리가 울퉁불퉁하죠? 
혀가 부어서 이빨에 눌린 자국입니다.
<b>몸이 물 먹은 솜처럼 퉁퉁 불어 순환이 막혔다는 명백한 증거</b>입니다.

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 (기허 의심)
2. "식사 후 졸리세요?" → 소화기능 저하 확인 (비기허 변증)
3. 혀 사진 선택 → <b>시각적 증거 확보</b> (환자 스스로 인정)

저는 환자의 말을 그냥 듣지 않습니다.
<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
'약을 먹을 수밖에 없는 몸 상태'임을 스스로 인정하게 만듭니다.

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- <b>핵심</b>: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
                conv_manager.add_message("ai", analysis_msg)
                conv_manager.update_stage("conversion")
                st.session_state.mode = "closing"
                st.rerun()
    
    with c4:
        # 자색설
        tongue_type = '자색설'
        if tongue_type in TONGUE_TYPES:
            info = TONGUE_TYPES[tongue_type]
            image_path = info.get('image', '')
            
            if image_path:
                try:
                    st.image(image_path, use_container_width=True)
                except Exception:
                    st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:60px; text-align:center;'>{info['emoji']}</div>", unsafe_allow_html=True)
            
            if st.button(f"{info['visual']}", key="btn_자색설", use_container_width=True):
                st.session_state.tongue_selected = True
                st.session_state.selected_tongue_type = tongue_type
                conv_manager.update_context("selected_tongue", tongue_type)
                conv_manager.add_message("user", f"[선택: {info['visual']}]")
                
                analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

{info['analysis']}

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 (기허 의심)
2. "식사 후 졸리세요?" → 소화기능 저하 확인 (비기허 변증)
3. 혀 사진 선택 → <b>시각적 증거 확보</b> (환자 스스로 인정)

환자는 이제 자신의 몸이 <b>"쉬어서 낫는 단계가 아니다"</b>는 걸 알았습니다.

저는 환자의 말을 그냥 듣지 않습니다.
<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
'약을 먹을 수밖에 없는 몸 상태'임을 스스로 인정하게 만듭니다.

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- <b>핵심</b>: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
                conv_manager.add_message("ai", analysis_msg)
                conv_manager.update_stage("conversion")
                st.session_state.mode = "closing"
                st.rerun()

# 일반 텍스트 입력
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    # 혀 타입 텍스트 자동 인식
    detected_tongue = None
    for tongue_key in ['담백설', '치흔설', '황태설', '자색설']:
        if tongue_key in user_input:
            detected_tongue = tongue_key
            break
    
    # 혀 타입이 감지되고 현재 혀 선택 단계라면
    if detected_tongue and current_stage == "tongue_select":
        st.session_state.tongue_selected = True
        st.session_state.selected_tongue_type = detected_tongue
        conv_manager.update_context("selected_tongue", detected_tongue)
        conv_manager.add_message("user", f"[선택: {user_input}]")
        
        info = TONGUE_TYPES[detected_tongue]
        analysis_msg = f"""
<b>보셨습니까 원장님?</b>

방금 환자가 선택한 <b>{info['name']}</b>을 보십시오.

{info['analysis']}

제가 한 일:
1. "언제 제일 힘드세요?" → 기상 직후 피로 (기허 의심)
2. "식사 후 졸리세요?" → 소화기능 저하 확인 (비기허 변증)
3. 혀 사진 선택 → <b>시각적 증거 확보</b> (환자 스스로 인정)

저는 환자의 말을 그냥 듣지 않습니다.
<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
'약을 먹을 수밖에 없는 몸 상태'임을 스스로 인정하게 만듭니다.

이 시스템을 원장님 병원에 24시간 붙여놓으면,
밤 11시에 검색하는 직장인도 자동으로 "내 몸이 심각하구나"를 깨닫고
<b>예약 버튼</b>을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- <b>핵심</b>: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
        conv_manager.add_message("ai", analysis_msg)
        conv_manager.update_stage("conversion")
        st.session_state.mode = "closing"
        st.rerun()
        st.stop()
    
    # 일반 메시지 처리
    conv_manager.add_message("user", user_input, metadata={"type": "text"})

    # 대화 카운트
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 0
    st.session_state.conversation_count += 1

    context = conv_manager.get_context()
    history = conv_manager.get_formatted_history(for_llm=True)
    
    # solution 단계에서 "네" 또는 긍정 답변 시 자동 클로징
    if context.get("stage") == "solution" and any(word in user_input for word in ["네", "예", "그래", "좋아", "부탁", "알려"]):
        st.session_state.mode = "closing"
        closing_msg = """
<b>보셨습니까 원장님?</b>

저는 환자의 말을 그냥 듣지 않습니다.

<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
**'약을 먹을 수밖에 없는 몸 상태'**임을 스스로 인정하게 만듭니다.

방금 체험하신 흐름:

1️⃣ <b>증상 구체화</b>: "언제 제일 힘드세요?" (단순 피로 배제)
2️⃣ <b>원인 추적</b>: 수면 → 소화 연결 (비기허 변증)
3️⃣ <b>시각적 증거</b>: 혀 사진으로 확증 (치흔설/황태설 등)
4️⃣ <b>위기감 조성</b>: "쉬어서 낫는 단계 지났습니다"
5️⃣ <b>솔루션 제안</b>: 녹용/공진단 필수성 각인

이 과정을 병원 홈페이지에 24시간 붙여놓으면,

밤 11시에 검색하는 직장인도
아침 8시에 문의하는 주부도
자동으로 "내 몸이 심각하구나"를 깨닫고 예약 버튼을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- **핵심**: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

여기서 딱 한 가지 질문만 남습니다.

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
        conv_manager.add_message("ai", closing_msg)
        conv_manager.update_stage("conversion")
        st.rerun()

    # 3회 이상 대화되면 클로징 멘트 직접 투입 (기존 로직 유지)
    elif st.session_state.conversation_count >= 3 and st.session_state.mode == "simulation":
        st.session_state.mode = "closing"
        closing_msg = """
<b>보셨습니까 원장님?</b>

저는 환자의 말을 그냥 듣지 않습니다.

<b>질문(문진) → 연결(변증) → 증거(설진)</b>를 통해
**'약을 먹을 수밖에 없는 몸 상태'**임을 스스로 인정하게 만듭니다.

방금 체험하신 흐름:

1️⃣ <b>증상 구체화</b>: "언제 제일 힘드세요?" (단순 피로 배제)
2️⃣ <b>원인 추적</b>: 수면 → 소화 연결 (비기허 변증)
3️⃣ <b>시각적 증거</b>: 혀 사진으로 확증 (치흔설)
4️⃣ <b>위기감 조성</b>: "쉬어서 낫는 단계 지났습니다"
5️⃣ <b>솔루션 제안</b>: 녹용/공진단 필수성 각인

이 과정을 병원 홈페이지에 24시간 붙여놓으면,

밤 11시에 검색하는 직장인도
아침 8시에 문의하는 주부도
자동으로 "내 몸이 심각하구나"를 깨닫고 예약 버튼을 누릅니다.

실제 적용 사례:
- 서울 A한의원: 온라인 문의 40% 증가, 예약 전환율 18% → 22.5%
- **핵심**: 단순 침(1만원) 문의가 한약 프로그램(30만원~) 상담으로 전환

여기서 딱 한 가지 질문만 남습니다.

<b>"우리 병원에 붙이면, 객단가가 얼마나 오를까?"</b>

이 아래에 병원명, 성함, 연락처만 남겨주시면,
24시간 안에 원장님 병원 기준 시뮬레이션을 보내드리겠습니다.
"""
        conv_manager.add_message("ai", closing_msg)
        conv_manager.update_stage("conversion")
        st.rerun()

    else:
        # 로딩 연출 (1초 대기)
        with st.spinner("🔬 환자 데이터 분석 중..."):
            time.sleep(1)  # 1초 로딩
            ai_response = generate_ai_response(user_input, context, history)

        conv_manager.add_message("ai", ai_response)
        
        # 응답에 "혀" 키워드가 있으면 자동으로 혀 선택 단계로 전환
        if "혀" in ai_response and current_stage in ["symptom_explore", "sleep_check", "digestion_check"]:
            conv_manager.update_stage("tongue_select")
        
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

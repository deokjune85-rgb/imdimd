"""
IMD Architecture Group - AI Sales Bot
멀티 페르소나 지원:
- ?client= (없거나 root) → IMD 회사 소개 AI 아키텍트
- ?client=hanbang → 한의원 데모
- ?client=gs → 안과 데모
- ?client=nana → 성형외과 데모
"""

import time
import re
from typing import Any, Dict

import streamlit as st
from PIL import Image

from conversation_manager import get_conversation_manager
from prompt_engine import get_prompt_engine, generate_ai_response
from lead_handler import LeadHandler


# ============================================
# AI 진단 로직 함수 (lift용)
# ============================================
def get_lift_recommendation(age_group, worry, history):
    """고민 부위 + 연령대 + 시술 경험에 따른 맞춤 추천"""
    
    treatment_name = ""
    description = ""
    urgency_msg = ""
    
    # 로직 1: 고민 부위에 따른 시술 추천 (가장 중요)
    if "턱" in worry or "이중턱" in worry:
        treatment_name = "윤곽 조각 리프팅 (지방분해 + 탄력 고정)"
        description = "지방층이 두꺼운 부위입니다. 불필요한 지방은 줄이고 근막(SMAS)층을 당겨주는 고주파 복합 시술이 필요합니다."
    elif "팔자" in worry:
        treatment_name = "심부볼 리프팅 & 볼륨 채움"
        description = "단순히 당기는 것만으로는 부족합니다. 꺼진 부위는 채우고, 처진 유지인대를 강화하는 시술이 병행되어야 합니다."
    elif "볼패임" in worry or "땅콩" in worry:
        treatment_name = "타이트닝 & 볼륨 리프팅"
        description = "가장 주의가 필요한 타입입니다. 강한 시술은 오히려 더 늙어 보일 수 있습니다. 피부 밀도를 높이는 고주파 계열이 안전합니다."
    else:  # 전반적 탄력 저하
        treatment_name = "올인원 풀페이스 타이트닝"
        description = "피부 전층(표피-진피-근막)을 동시에 자극하여 콜라겐 생성을 극대화하는 레이저 리프팅이 적합합니다."
    
    # 로직 2: 연령대에 따른 긴급도 멘트
    if "20대" in age_group:
        urgency_msg = "아직 노화가 본격화되기 전입니다. 지금 관리하면 10년 후가 달라집니다."
    elif "30대" in age_group:
        urgency_msg = "아직 깊은 주름이 자리 잡기 전입니다. 지금 관리하면 '가성비'가 가장 좋습니다."
    elif "40대" in age_group:
        urgency_msg = "피부 회복력이 떨어지기 시작하는 시기입니다. 1년 늦어질수록 비용이 증가합니다."
    else:  # 50대 이상
        urgency_msg = "피부 회복력이 급격히 떨어지는 시기입니다. 지금이 비수술로 해결할 수 있는 마지막 기회일 수 있습니다."
    
    # 로직 3: 시술 경험에 따른 추가 멘트
    history_msg = ""
    if "없음" in history or "처음" in history:
        history_msg = "첫 시술이시므로 부작용 위험이 낮은 조합부터 시작하는 것이 좋습니다."
    elif "1년" in history:
        history_msg = "유지 시술 타이밍입니다. 기존 효과가 남아있을 때 추가하면 시너지가 납니다."
    elif "3년 이내" in history:
        history_msg = "기존 시술 효과가 거의 소멸된 시점입니다. 리터치 시술이 시급합니다."
    else:  # 3년 이상
        history_msg = "처음 시술하시는 분과 동일하게 기초부터 다시 시작해야 합니다."
    
    return treatment_name, description, urgency_msg, history_msg


from config import (
    get_client_id_from_query,
    get_config,
    COLOR_PRIMARY,
    COLOR_BG,
    COLOR_TEXT,
    COLOR_AI_BUBBLE,
    COLOR_USER_BUBBLE,
    COLOR_BORDER,
)

# ============================================
# CLIENT_ID와 설정 로드
# ============================================
CLIENT_ID = get_client_id_from_query()
CFG = get_config(CLIENT_ID)
TONGUE_TYPES = CFG.get("TONGUE_TYPES", {})
IS_ROOT = CFG.get("IS_ROOT", False)

# ============================================
# 페이지 설정
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
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.stDeployButton {{display: none;}}
[data-testid="stToolbar"] {{display: none;}}
[data-testid="stDecoration"] {{display: none;}}
[data-testid="stStatusWidget"] {{display: none;}}

.stApp {{
    background: white !important;
}}

.main .block-container {{
    padding: 0 !important;
    max-width: 720px !important;
    margin: 0 auto !important;
    background: white !important;
}}

.title-box {{
    text-align: center;
    padding: 20px 20px 12px 20px;
    background: white;
}}

.title-box h1 {{
    font-size: 28px !important;
    font-weight: 700 !important;
    color: {COLOR_PRIMARY} !important;
    margin: 0 !important;
}}

.title-box .sub {{
    font-size: 16px;
    color: #4B5563;
    margin-top: 4px;
}}

.hero-section {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    padding: 30px 20px;
    text-align: center;
    border-radius: 0 0 16px 16px;
    margin-bottom: 10px;
}}

.hero-title {{
    font-size: 24px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 1px;
}}

.hero-sub {{
    font-size: 14px;
    color: #94A3B8;
    margin-top: 6px;
}}

.chat-area {{
    padding: 12px 20px 4px 20px;
    background: white !important;
    min-height: 150px;
    margin-bottom: 100px;
}}

.ai-msg {{
    background: #F9FAFB !important;
    color: #1F2937 !important;
    padding: 14px 18px !important;
    border-radius: 18px 18px 18px 4px !important;
    margin: 12px 0 8px 0 !important;
    max-width: 85% !important;
    font-size: 17px !important;
    line-height: 1.5 !important;
    border: 1px solid #E5E7EB !important;
}}

.user-msg {{
    background: {COLOR_USER_BUBBLE} !important;
    color: #1F2937 !important;
    padding: 12px 18px !important;
    border-radius: 18px 18px 4px 18px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    display: inline-block !important;
    font-size: 16px !important;
    line-height: 1.4 !important;
}}

.msg-right {{
    text-align: right !important;
    clear: both !important;
    display: block !important;
    width: 100% !important;
    margin-top: 12px !important;
}}

.stChatInput {{
    position: fixed !important;
    bottom: 50px !important;
    left: 0 !important;
    right: 0 !important;
    background: white !important;
    padding: 10px 0 !important;
    box-shadow: 0 -2px 6px rgba(0,0,0,0.08) !important;
    z-index: 999 !important;
}}

.stChatInput > div {{
    max-width: 680px !important;
    margin: 0 auto !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 24px !important;
}}

.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white !important;
    padding: 10px 20px;
    text-align: center;
    font-size: 11px;
    color: #9CA3AF;
    border-top: 1px solid {COLOR_BORDER};
    z-index: 998;
}}

.stForm {{
    background: white;
    padding: 20px;
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
    margin: 16px 20px 180px 20px;
}}

@media (max-width: 768px) {{
    .main .block-container {{
        max-width: 100% !important;
    }}
    .title-box h1 {{
        font-size: 20px !important;
    }}
    .ai-msg {{
        font-size: 15px !important;
        padding: 10px 12px !important;
    }}
    .user-msg {{
        font-size: 14px !important;
    }}
    div[data-testid="column"] {{
        min-width: 0 !important;
        flex: 0 0 23% !important;
        max-width: 25% !important;
    }}
}}

/* st.metric 글자색 + 크기 강제 지정 */
[data-testid="stMetric"] {{
    background: #F8FAFC !important;
    padding: 12px !important;
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
}}

[data-testid="stMetricLabel"] {{
    color: #64748B !important;
    font-size: 13px !important;
}}

[data-testid="stMetricValue"] {{
    color: #1E293B !important;
    font-weight: 700 !important;
    font-size: 18px !important;
}}

[data-testid="stMetricDelta"] {{
    color: #059669 !important;
    font-size: 12px !important;
}}

/* st.status 글자색 - 모든 요소 강제 */
[data-testid="stStatus"] {{
    color: #1F2937 !important;
}}

[data-testid="stStatus"] * {{
    color: #1F2937 !important;
}}

[data-testid="stStatusWidget"] {{
    color: #1F2937 !important;
}}

[data-testid="stExpander"] summary span {{
    color: #1F2937 !important;
}}

div[data-testid="stStatus"] label {{
    color: #1F2937 !important;
}}

div[data-testid="stStatus"] p {{
    color: #1F2937 !important;
}}

/* stStatus 내부 완료 메시지 */
.stStatus span, .stStatus p, .stStatus label {{
    color: #1F2937 !important;
}}

/* st.info, st.warning, st.error, st.success 글자색 */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
.stAlert p,
.stAlert span {{
    color: #1F2937 !important;
}}

/* st.divider */
[data-testid="stDivider"] {{
    border-color: #E5E7EB !important;
}}

/* 마크다운 h3 */
.stMarkdown h3 {{
    color: #1E293B !important;
}}

/* Streamlit 버튼 스타일 - 옅은 회색 배경 + 검은 글자 */
.stButton > button {{
    background-color: #F3F4F6 !important;
    color: #1F2937 !important;
    border: 1px solid #E5E7EB !important;
    font-weight: 500 !important;
}}

.stButton > button:hover {{
    background-color: #E5E7EB !important;
    border-color: #D1D5DB !important;
}}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================
# 유틸 함수
# ============================================
ALLOWED_STAGES = {"initial", "symptom_explore", "sleep_check", "digestion_check", "tongue_select", "conversion", "complete"}
ROUTE_MAP = {"hanbang": "hanbang", "gs": "gs", "nana": "nana", "law": "law", "math": "math", "lift": "lift"}


def parse_response_tags(text: str, current_stage: str):
    """[[STAGE:...]] 와 [[ROUTE:...]] 태그 파싱"""
    body = text
    new_stage = current_stage
    route_to = None
    
    stage_match = re.search(r'\[\[STAGE:(\w+)\]\]', text)
    if stage_match:
        stage_val = stage_match.group(1).lower()
        if stage_val in ALLOWED_STAGES:
            new_stage = stage_val
        body = re.sub(r'\[\[STAGE:\w+\]\]', '', body)
    
    route_match = re.search(r'\[\[ROUTE:(\w+)\]\]', text)
    if route_match:
        route_val = route_match.group(1).lower()
        if route_val in ROUTE_MAP:
            route_to = ROUTE_MAP[route_val]
        body = re.sub(r'\[\[ROUTE:\w+\]\]', '', body)
    
    return body.strip(), new_stage, route_to


def html_escape(s: str) -> str:
    import html
    return html.escape(s).replace("\n", "<br>")


# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
engine_info = get_prompt_engine()
lead_handler = LeadHandler()

if "app_initialized" not in st.session_state or st.session_state.get("current_client") != CLIENT_ID:
    conv_manager.reset_conversation()
    conv_manager.add_message("ai", CFG["INITIAL_MSG"])
    conv_manager.update_stage("initial")
    st.session_state.app_initialized = True
    st.session_state.current_client = CLIENT_ID
    st.session_state.conversation_count = 0
    st.session_state.pending_route = None
    st.session_state.analysis_shown = False
    st.session_state.math_case_study = None
    st.session_state.lift_step = 1

conv_manager.update_context("client_id", CLIENT_ID)


# ============================================
# 헤더
# ============================================
if IS_ROOT:
    st.markdown(
        """
<div class="hero-section">
    <div class="hero-title">🏛️ IMD ARCHITECTURE GROUP</div>
    <div class="hero-sub">매출을 설계하는 비즈니스 아키텍처 그룹</div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
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
context = conv_manager.get_context()
chat_history = conv_manager.get_history()
current_stage = context.get("stage", "initial")
selected_tongue = context.get("selected_tongue")


# ============================================
# Root 모드: 추천 질문 칩 + 데모 라우팅 버튼
# ============================================
if IS_ROOT:
    # 추천 질문 칩 (첫 메시지 후에만)
    if len(chat_history) <= 2:
        st.markdown("---")
        cols = st.columns(3)
        chips = [
            ("🏢 IMD는 뭐하는 곳?", "IMD는 뭐하는 회사야?"),
            ("💰 진짜 매출이 올라?", "진짜 매출이 올라?"),
            ("🏥 병원 원장입니다", "저는 병원 원장입니다"),
        ]
        for i, (label, query) in enumerate(chips):
            with cols[i]:
                if st.button(label, key=f"chip_{i}", use_container_width=True):
                    conv_manager.add_message("user", query)
                    raw_ai = generate_ai_response(query, conv_manager.get_context(), conv_manager.get_history())
                    clean_ai, new_stage, route_to = parse_response_tags(raw_ai, current_stage)
                    conv_manager.add_message("ai", clean_ai)
                    conv_manager.update_stage(new_stage)
                    if route_to:
                        st.session_state.pending_route = route_to
                    st.rerun()
    
    # 라우팅 버튼 (pending_route가 있거나 대화 중 업종 감지 시)
    pending = st.session_state.get("pending_route")
    if pending:
        st.markdown("---")
        demo_labels = {
            "hanbang": ("🏥 한의원 AI 실장 체험하기", "원장님 대신 환자를 설득하는 AI"),
            "gs": ("👁️ 안과 AI 검안 시스템 체험하기", "가격 문의를 검안 예약으로 전환"),
            "nana": ("✨ 성형외과 AI 컨설턴트 체험하기", "환자의 워너비 스타일 파악"),
            "law": ("⚖️ 법률 AI 사건 접수 체험하기", "의뢰인의 증거와 상황 파악"),
            "math": ("📐 수학학원 AI 상담 체험하기", "학부모의 고민과 연락처 확보"),
            "lift": ("💎 피부과 AI 리프팅 진단 체험하기", "가격 문의를 시술 예약으로 전환"),
        }
        label, desc = demo_labels.get(pending, ("데모 보기", ""))
        st.markdown(f"<p style='text-align:center; color:#6B7280; font-size:13px;'>{desc}</p>", unsafe_allow_html=True)
        if st.button(label, key="route_btn", use_container_width=True):
            st.query_params["client"] = pending
            st.session_state.pending_route = None
            st.rerun()

    # 데모 목록 (하단에 항상 표시)
    with st.expander("📋 업종별 데모 바로가기", expanded=False):
        demo_cols = st.columns(6)
        demos = [
            ("hanbang", "🏥 한의원", "AI 수석 실장"),
            ("gs", "👁️ 안과", "AI 검안 시스템"),
            ("nana", "✨ 성형외과", "AI 뷰티 컨설턴트"),
            ("law", "⚖️ 법률", "AI 사건 접수"),
            ("math", "📐 수학학원", "AI 입시 진단"),
            ("lift", "💎 피부과", "AI 리프팅 진단"),
        ]
        for i, (cid, name, desc) in enumerate(demos):
            with demo_cols[i]:
                if st.button(f"{name}", key=f"demo_{cid}", use_container_width=True):
                    st.query_params["client"] = cid
                    st.rerun()
                st.caption(desc)


# ============================================
# Lift 모드: 단계별 버튼 UI (B2C 고객 직접 타겟)
# ============================================
if CLIENT_ID == "lift" and current_stage != "conversion" and current_stage != "complete":
    last_ai_text = chat_history[-1]["text"] if chat_history and chat_history[-1]["role"] == "ai" else ""
    
    # AI 대사 키워드로 현재 단계 및 버튼 결정
    buttons = []
    if "연령대" in last_ai_text:
        buttons = ["20대", "30대", "40대", "50대 이상"]
    elif "신경 쓰이는 부위" in last_ai_text:
        buttons = ["무너진 턱라인(이중턱)", "깊어지는 팔자주름", "볼패임/땅콩형 얼굴", "전반적인 탄력 저하"]
    elif "시술 경험" in last_ai_text:
        buttons = ["없음(처음)", "1년 이내", "3년 이내", "3년 이상"]
    
    # 버튼 표시
    if buttons:
        with st.container():
            st.markdown(
                '<div style="text-align:center; color:#9CA3AF; font-size:12px; margin:8px 0;">버튼을 선택하거나, 직접 입력하셔도 됩니다</div>',
                unsafe_allow_html=True,
            )
            # 4개 버튼일 때 2x2 또는 4열
            if len(buttons) == 4:
                cols = st.columns(2)
                for idx, btn_label in enumerate(buttons):
                    with cols[idx % 2]:
                        if st.button(btn_label, key=f"lift_btn_{idx}_{btn_label}", use_container_width=True):
                            # 선택한 값 저장 (나이 매칭용)
                            if "대" in btn_label:
                                st.session_state.lift_age = btn_label
                            elif "턱" in btn_label or "팔자" in btn_label or "볼패임" in btn_label or "탄력" in btn_label:
                                st.session_state.lift_concern = btn_label
                            else:
                                st.session_state.lift_history = btn_label
                            
                            conv_manager.add_message("user", btn_label)
                            raw_ai = generate_ai_response(btn_label, conv_manager.get_context(), conv_manager.get_history())
                            clean_ai, new_stage, route_to = parse_response_tags(raw_ai, current_stage)
                            conv_manager.add_message("ai", clean_ai)
                            conv_manager.update_stage(new_stage)
                            st.rerun()
            else:
                cols = st.columns(len(buttons))
                for idx, btn_label in enumerate(buttons):
                    with cols[idx]:
                        if st.button(btn_label, key=f"lift_btn_{idx}_{btn_label}", use_container_width=True):
                            conv_manager.add_message("user", btn_label)
                            raw_ai = generate_ai_response(btn_label, conv_manager.get_context(), conv_manager.get_history())
                            clean_ai, new_stage, route_to = parse_response_tags(raw_ai, current_stage)
                            conv_manager.add_message("ai", clean_ai)
                            conv_manager.update_stage(new_stage)
                            st.rerun()


# ============================================
# 데모 모드: 선택 UI (tongue_select 단계)
# ============================================
if not IS_ROOT and TONGUE_TYPES:
    last_ai_text = chat_history[-1]["text"] if chat_history and chat_history[-1]["role"] == "ai" else ""
    trigger_keywords = ["혀", "거울", "글씨", "시력", "스타일", "워너비", "선택", "증거", "상황", "문제", "등급", "성적", "학년", "부위", "팔자", "턱선", "눈가", "처짐", "주름"]
    show_tongue_ui = (
        current_stage == "tongue_select"
        and not selected_tongue
        and any(kw in last_ai_text for kw in trigger_keywords)
    )
    
    if show_tongue_ui:
        with st.container():
            st.markdown(
                f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:18px; margin:4px 0 8px 0;">{CFG["TONGUE_GUIDE"]}</div>',
                unsafe_allow_html=True,
            )
            cols = st.columns(4)
            for idx, (tongue_key, tongue_data) in enumerate(TONGUE_TYPES.items()):
                with cols[idx]:
                    image_path = tongue_data.get("image", "")
                    try:
                        img = Image.open(image_path)
                        st.image(img, use_container_width=True)
                    except:
                        st.markdown(
                            f"<div style='text-align:center; font-size:60px; padding:15px 0;'>{tongue_data['emoji']}</div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown(
                        f"<div style='text-align:center; font-size:12px; font-weight:600; color:#1F2937;'>{tongue_data['name']}</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("선택", key=f"tongue_{tongue_key}", use_container_width=True):
                        conv_manager.update_context("selected_tongue", tongue_key)
                        diagnosis_msg = f"""{tongue_data['name']} 상태를 선택하셨습니다.

{tongue_data['analysis']}

주요 증상: {tongue_data['symptoms']}

⚠️ 주의: {tongue_data['warning']}

방금 보신 과정이 실제로 AI가 환자에게 자동으로 진행하는 흐름입니다.

이제부터는 이 분석 결과를 바탕으로 자연스럽게 상담 단계로 넘어갑니다."""
                        conv_manager.add_message("ai", diagnosis_msg)
                        conv_manager.update_stage("conversion")
                        st.rerun()
            st.markdown('<div style="height:120px;"></div>', unsafe_allow_html=True)


# ============================================
# AI 정밀 분석 결과 카드 (전 업종 공통)
# ============================================
if not IS_ROOT and current_stage == "conversion" and not st.session_state.get("analysis_shown"):
    
    # 1. 로딩 애니메이션 (st.status)
    if CLIENT_ID == "hanbang":
        with st.status("🧬 AI 한의학 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 환자 증상 데이터 수신 및 키워드 추출...")
            time.sleep(1.0)
            st.write("🔍 전국 유사 체질 사례 8,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 원장님 진료 철학 기반 맞춤 처방 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 진단서가 생성되었습니다.", state="complete", expanded=False)
        
        # 2. 결과 카드 (st.metric)
        st.divider()
        st.markdown("### 🏥 [AI 한의학 정밀 진단서]")
        c1, c2, c3 = st.columns(3)
        c1.metric("체질 적합도", "87점", "양호")
        c2.metric("예상 치료 기간", "8주", "±2주")
        c3.metric("호전 확률", "91%", "매우 높음")
        st.warning("⚠️ **주의:** 현재 **기혈 순환 저하** 징후가 감지되었습니다. 2주 내 초진 미진행 시 만성화 위험이 있습니다.")
    
    elif CLIENT_ID == "gs":
        with st.status("👁️ AI 안과 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 환자 시력 데이터 수신 및 패턴 분석...")
            time.sleep(1.0)
            st.write("🔍 강남구 유사 수술 사례 15,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 최적 수술법 및 예상 결과 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 검안 리포트가 생성되었습니다.", state="complete", expanded=False)
        
        st.divider()
        st.markdown("### 👁️ [AI 정밀 검안 리포트]")
        c1, c2, c3 = st.columns(3)
        c1.metric("수술 적합도", "94점", "매우 높음")
        c2.metric("예상 교정 시력", "1.2", "+1.0")
        c3.metric("부작용 위험도", "3%", "매우 낮음")
        st.error("⚠️ **긴급:** 현재 **각막 두께**가 평균 이하입니다. 일반 라식 불가, 스마일라식 프로 권장됩니다.")
    
    elif CLIENT_ID == "nana":
        with st.status("✨ AI 뷰티 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 환자 얼굴형 데이터 수신 및 황금비율 분석...")
            time.sleep(1.0)
            st.write("🔍 강남구 유사 성형 사례 12,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 원장님 수술 철학 기반 견적 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 제안서가 생성되었습니다.", state="complete", expanded=False)
        
        st.divider()
        st.markdown("### ✨ [AI 뷰티 컨설팅 리포트]")
        c1, c2, c3 = st.columns(3)
        c1.metric("스타일 매칭도", "96점", "완벽")
        c2.metric("자연스러움 지수", "92점", "매우 높음")
        c3.metric("회복 예상 기간", "2주", "빠름")
        st.success("✅ **Good News:** 고객님의 얼굴형은 **자연유착**과 **비개방 코성형**에 최적화되어 있습니다.")
    
    elif CLIENT_ID == "law":
        with st.status("⚖️ AI 법률 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 의뢰인 사건 데이터 수신 및 쟁점 추출...")
            time.sleep(1.0)
            st.write("🔍 유사 판례 50,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 승소 확률 및 예상 결과 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 법률 진단서가 생성되었습니다.", state="complete", expanded=False)
        
        st.divider()
        st.markdown("### ⚖️ [AI 법률 정밀 진단서]")
        c1, c2, c3 = st.columns(3)
        c1.metric("승소 유력 지수", "92점", "매우 높음")
        c2.metric("예상 위자료", "3,500만 원", "±500")
        c3.metric("증거 확보율", "85%", "양호")
        st.error("⚠️ **긴급 경고:** 상대방의 **재산 은닉** 징후가 포착되었습니다. 12시간 내 가압류 미진행 시 회수 불능 위험이 있습니다.")
    
    elif CLIENT_ID == "math":
        with st.status("📐 AI 입시 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 학생 성적 패턴 수신 및 취약점 추출...")
            time.sleep(1.0)
            st.write("🔍 대치동/목동 유사 성적 향상 사례 8,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 '역산 학습법' 적용 시 예상 등급 시뮬레이션...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 진단 리포트가 생성되었습니다.", state="complete", expanded=False)
        
        st.divider()
        st.markdown("### 📐 [AI 입시 정밀 진단서]")
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 학습 효율", "38%", "위험")
        c2.metric("수포자 확률", "93%", "매우 높음")
        c3.metric("골든타임", "D-90", "이번 방학")
        st.error("⚠️ **긴급 경고:** 현재 **'관람객 공부법'** 패턴이 감지되었습니다. 즉시 교정하지 않으면 고3에서 회복 불가능합니다.")
        
        # 솔루션 블러 처리 (인질극)
        st.divider()
        st.markdown("### 📂 [유사 사례: 4등급 → 1등급 달성]")
        st.info("""
**목동고 김OO 학생** (고2, 수학 4등급 → 1등급)

✅ 3개월 만에 **전교 15등** 달성
✅ 비결: **'??? 학습법'** 적용

🔒 **상세 로드맵은 [맞춤형 리포트]에서만 공개됩니다.**
        """)
        st.warning("💡 이 학생이 사용한 **'역산 학습법'**과 **주차별 커리큘럼**을 받아보시겠습니까?")
    
    elif CLIENT_ID == "lift":
        with st.status("🔄 강남 40,000건의 데이터와 대조 중입니다...", expanded=True) as status:
            st.write("📡 고객님의 피부 데이터 수신 중...")
            time.sleep(1.0)
            st.write("🔍 연령대별 유사 사례 매칭 중...")
            time.sleep(1.2)
            st.write("📊 최적 시술 조합 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 고객님만을 위한 리프팅 설계도가 나왔습니다.", state="complete", expanded=False)
        
        # 세션에서 선택값 가져오기
        lift_age = st.session_state.get("lift_age", "30대")
        lift_concern = st.session_state.get("lift_concern", "팔자주름")
        lift_history = st.session_state.get("lift_history", "없음")
        
        # 로직 함수 호출
        rec_name, rec_desc, urgency_msg, history_msg = get_lift_recommendation(lift_age, lift_concern, lift_history)
        
        # 연령대별 피부 나이 및 사례 나이 계산 (고객 연령대 + 3~6살)
        if "20대" in lift_age:
            skin_age = "26세"
            case_age = "28세"
            case_name = "이OO"
        elif "30대" in lift_age:
            skin_age = "34세"
            case_age = "36세"
            case_name = "박OO"
        elif "40대" in lift_age:
            skin_age = "45세"
            case_age = "47세"
            case_name = "김OO"
        else:
            skin_age = "54세"
            case_age = "56세"
            case_name = "최OO"
        
        # 고민 부위 간략화
        if "턱" in lift_concern:
            concern_short = "턱라인"
        elif "팔자" in lift_concern:
            concern_short = "팔자주름"
        elif "볼패임" in lift_concern or "땅콩" in lift_concern:
            concern_short = "볼패임"
        else:
            concern_short = "탄력 저하"
        
        st.divider()
        st.markdown("### 💎 [AI 리프팅 정밀 진단서]")
        c1, c2, c3 = st.columns(3)
        c1.metric("피부 탄력 나이", skin_age, "실제 나이보다 높음 ⚠️")
        c2.metric("탄력 위험도", "47점", "주의 단계")
        c3.metric("비수술 골든타임", "D-180일", "6개월")
        
        # 추천 시술 표시
        st.divider()
        st.markdown("### 🎯 [AI 추천 시술]")
        st.success(f"**{rec_name}**")
        st.info(f"**[분석 코멘트]** {rec_desc}")
        st.warning(f"**[긴급도]** {urgency_msg}")
        if history_msg:
            st.caption(f"💡 {history_msg}")
        
        # 유사 성공 사례 (나이 매칭)
        st.divider()
        st.markdown("### 📂 [유사 성공 사례 매칭]")
        st.info(f"""
**강남 {case_name} 고객 ({case_age}, {concern_short} 고민)**

✅ 고객님과 **98% 유사**한 피부 두께 및 처짐 패턴
✅ 시술 3주 후 눈에 띄는 개선 확인
✅ 적용 시술: **{rec_name}**

🔒 **상세 시술 구성과 예상 견적은 리포트에서 확인하세요.**
        """)
    
    # 분석 결과 표시 완료 플래그
    st.session_state.analysis_shown = True


# ============================================
# CTA (conversion 단계)
# ============================================
current_stage = conv_manager.get_context().get("stage", "initial")
show_cta = (current_stage == "conversion") or (
    len(chat_history) > 0 and "도입하시겠습니까" in chat_history[-1].get("text", "")
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
            # lift는 B2C이므로 성함/연락처만 받음
            if CLIENT_ID == "lift":
                customer_name = st.text_input(CFG["FORM_LABEL_1"], placeholder=CFG["FORM_PLACEHOLDER_1"])
                contact = st.text_input(CFG["FORM_LABEL_2"], placeholder=CFG["FORM_PLACEHOLDER_2"])
                # 안심 문구
                cta_note = CFG.get("CTA_NOTE", "")
                if cta_note:
                    st.caption(f"*{cta_note}*")
                submitted = st.form_submit_button(CFG["FORM_BUTTON"], use_container_width=True)
                
                if submitted:
                    if not customer_name or not contact:
                        st.error("필수 정보를 모두 입력해주세요.")
                    else:
                        # lift용 리드 데이터
                        lead_data = {
                            "name": customer_name,
                            "contact": contact,
                            "symptom": f"연령대: {st.session_state.get('lift_age', '미입력')} / 고민: {st.session_state.get('lift_concern', '미입력')} / 시술경험: {st.session_state.get('lift_history', '미입력')}",
                            "preferred_date": "즉시 상담 희망",
                            "chat_summary": conv_manager.get_summary(),
                            "source": CFG["APP_TITLE"],
                            "type": "피부과 리프팅",
                        }
                        success = save_lead(lead_data)
                        if success:
                            conv_manager.update_stage("complete")
                            conv_manager.add_message("ai", "신청이 완료되었습니다. 전문 분석가가 곧 연락드리겠습니다. 감사합니다.")
                            st.success("✅ 신청되었습니다! 전문 분석가가 곧 연락드립니다.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("저장 중 오류가 발생했습니다. 다시 시도해주세요.")
            else:
                # 기존 B2B 폼 (병원명/원장명/연락처)
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
                            "symptom": f"회사/병원명: {clinic_name}",
                            "preferred_date": "즉시 상담 희망",
                            "chat_summary": conv_manager.get_summary(),
                            "source": CFG["APP_TITLE"],
                            "type": CFG["APP_TITLE"],
                    }
                    success, message = lead_handler.save_lead(lead_data)
                    if success:
                        completion_msg = f"""견적서 발송이 완료되었습니다.

{director_name}님, 감사합니다.

{clinic_name}에 최적화된 AI 시스템 견적서를 {contact}로 24시간 내 전송해드리겠습니다.

담당 컨설턴트가 직접 연락드려 상세히 안내해드리겠습니다."""
                        conv_manager.add_message("ai", completion_msg)
                        conv_manager.update_stage("complete")
                        st.success("견적서 신청이 완료되었습니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"오류: {message}")


# ============================================
# 입력창 + AI 응답
# ============================================
user_input = st.chat_input("메시지를 입력해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})
    st.session_state.conversation_count = st.session_state.get("conversation_count", 0) + 1
    
    context = conv_manager.get_context()
    history_for_llm = conv_manager.get_history()
    
    raw_ai = generate_ai_response(user_input, context, history_for_llm)
    clean_ai, new_stage, route_to = parse_response_tags(raw_ai, context.get("stage", "initial"))
    
    # 데모 모드에서 conversion일 때 후기 추가
    if not IS_ROOT and new_stage == "conversion":
        from prompt_engine import generate_veritas_story
        user_messages = [msg.get("text", "") for msg in conv_manager.get_history() if msg.get("role") == "user"]
        symptom_messages = [m for m in user_messages if len(m) >= 5 and any(ord('가') <= ord(c) <= ord('힣') for c in m)]
        symptom = " ".join(symptom_messages[:2]) if symptom_messages else "만성 피로"
        success_story = generate_veritas_story(symptom, client_id=CLIENT_ID)
        
        # 학원(math)은 '유사 사례 분석' 형태로 저장 (st.info로 별도 표시)
        if CLIENT_ID == "math":
            st.session_state.math_case_study = success_story
            clean_ai += "\n\n잠시만요, 어머님 자녀분과 비슷한 케이스를 데이터베이스에서 찾아보겠습니다..."
        else:
            # 기존 방식 (병원/법률 등)
            clean_ai += f"\n\n---\n\n💬 **실제 후기**\n\n\"{success_story}\"\n\n---\n"
    
    conv_manager.add_message("ai", clean_ai)
    conv_manager.update_stage(new_stage)
    
    # Root 모드에서 라우팅 감지
    if IS_ROOT and route_to:
        st.session_state.pending_route = route_to
    
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
# 푸터 - 하단 조그만 회색 글자 (클릭 시 제작사 홈페이지 이동)
# ============================================
footer_url = CFG.get("FOOTER_URL", "https://www.converdream.co.kr")
st.markdown(
    f"""
<div style="
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 10px 20px;
    text-align: center;
    font-size: 11px;
    color: #9CA3AF;
    border-top: 1px solid #E5E7EB;
    z-index: 998;">
    <a href="{footer_url}" target="_blank" style="text-decoration: none; color: #9CA3AF;">
        <b>{CFG["FOOTER_TITLE"]}</b> | {CFG["FOOTER_SUB"]}
    </a>
</div>
""",
    unsafe_allow_html=True,
)

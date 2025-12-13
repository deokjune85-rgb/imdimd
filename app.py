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

/* st.metric 글자색 강제 지정 */
[data-testid="stMetric"] {{
    background: #F8FAFC !important;
    padding: 16px !important;
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
}}

[data-testid="stMetricLabel"] {{
    color: #64748B !important;
}}

[data-testid="stMetricValue"] {{
    color: #1E293B !important;
    font-weight: 700 !important;
}}

[data-testid="stMetricDelta"] {{
    color: #059669 !important;
}}

/* st.status 글자색 */
[data-testid="stStatusWidget"] {{
    color: #1F2937 !important;
}}

[data-testid="stStatus"] p, 
[data-testid="stStatus"] span {{
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
</style>
""",
    unsafe_allow_html=True,
)


# ============================================
# 유틸 함수
# ============================================
ALLOWED_STAGES = {"initial", "symptom_explore", "sleep_check", "digestion_check", "tongue_select", "conversion", "complete"}
ROUTE_MAP = {"hanbang": "hanbang", "gs": "gs", "nana": "nana", "law": "law", "math": "math"}


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
        }
        label, desc = demo_labels.get(pending, ("데모 보기", ""))
        st.markdown(f"<p style='text-align:center; color:#6B7280; font-size:13px;'>{desc}</p>", unsafe_allow_html=True)
        if st.button(label, key="route_btn", use_container_width=True):
            st.query_params["client"] = pending
            st.session_state.pending_route = None
            st.rerun()

    # 데모 목록 (하단에 항상 표시)
    with st.expander("📋 업종별 데모 바로가기", expanded=False):
        demo_cols = st.columns(5)
        demos = [
            ("hanbang", "🏥 한의원", "AI 수석 실장"),
            ("gs", "👁️ 안과", "AI 검안 시스템"),
            ("nana", "✨ 성형외과", "AI 뷰티 컨설턴트"),
            ("law", "⚖️ 법률", "AI 사건 접수"),
            ("math", "📐 수학학원", "AI 학습 상담"),
        ]
        for i, (cid, name, desc) in enumerate(demos):
            with demo_cols[i]:
                if st.button(f"{name}", key=f"demo_{cid}", use_container_width=True):
                    st.query_params["client"] = cid
                    st.rerun()
                st.caption(desc)


# ============================================
# 데모 모드: 선택 UI (tongue_select 단계)
# ============================================
if not IS_ROOT and TONGUE_TYPES:
    last_ai_text = chat_history[-1]["text"] if chat_history and chat_history[-1]["role"] == "ai" else ""
    trigger_keywords = ["혀", "거울", "글씨", "시력", "스타일", "워너비", "선택", "증거", "상황", "문제", "등급", "성적", "학년"]
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
        with st.status("📐 AI 학습 데이터 정밀 분석 중...", expanded=True) as status:
            st.write("📡 학생 성적 데이터 수신 및 취약점 추출...")
            time.sleep(1.0)
            st.write("🔍 목동/강남 유사 성적 향상 사례 5,000건 대조 중...")
            time.sleep(1.2)
            st.write("📊 맞춤형 커리큘럼 및 예상 등급 산출 중...")
            time.sleep(1.0)
            status.update(label="✅ 분석 완료! 맞춤형 학습 진단서가 생성되었습니다.", state="complete", expanded=False)
        
        st.divider()
        st.markdown("### 📐 [AI 학습 정밀 진단서]")
        c1, c2, c3 = st.columns(3)
        c1.metric("개념 이해도", "62점", "보통")
        c2.metric("예상 등급 변화", "3등급 → 1등급", "+2등급")
        c3.metric("필요 기간", "3개월", "집중반")
        st.error("⚠️ **긴급 경고:** 현재 **개념 결손**이 심각합니다. 이번 방학 내 재건축 미진행 시 고2에서 5등급 이하 추락 위험이 있습니다.")
        
        # 유사 사례 카드 (math 전용)
        if st.session_state.get("math_case_study"):
            case_study = st.session_state.math_case_study
            st.info(f"""
**[📂 유사 사례 분석 결과]**

{case_study}
            """)
            st.session_state.math_case_study = None
    
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
# 푸터
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

import streamlit as st
import time
from conversation_manager import ConversationManager
from config import TONGUE_TYPES, COLOR_PRIMARY

# 페이지 설정
st.set_page_config(page_title="IMD Medical Consulting", page_icon="💼", layout="centered")

# 초기화
if 'conv_manager' not in st.session_state:
    st.session_state.conv_manager = ConversationManager()
    st.session_state.conv_manager.add_message("ai", """
원장님, 환자가 '비싸요'라고 하는 진짜 이유는 돈이 없어서가 아닙니다.
내 몸이 그만큼 심각하다는 걸 모르기 때문입니다.

제가 질문 몇 개로 환자의 '숨겨진 병리'를 찾아내고, 스스로 지갑을 열게 만드는 과정을 보여드리겠습니다.

지금부터 원장님은 잠시 '만성 피로 환자' 역할을 해봐 주십시오. 편한 말투로 현재 상태를 한 줄만 말씀해 주세요.
""")
    st.session_state.count = 0

conv_manager = st.session_state.conv_manager

# CSS
st.markdown(f"""
<style>
.stApp {{
    background: white;
}}
.title {{
    text-align: center;
    color: {COLOR_PRIMARY};
    font-size: 24px;
    font-weight: 700;
    padding: 20px;
}}
</style>
""", unsafe_allow_html=True)

# 타이틀
st.markdown('<div class="title">IMD MEDICAL CONSULTING</div>', unsafe_allow_html=True)

# 채팅 표시
for msg in conv_manager.get_history():
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"], unsafe_allow_html=True)

# 현재 단계
current_stage = conv_manager.get_context().get("stage", "symptom_explore")

# 혀 선택 버튼
if current_stage == "tongue_select":
    st.markdown("---")
    st.markdown("**거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⚪ 담백설"):
            conv_manager.add_message("user", "[선택: 담백설]")
            info = TONGUE_TYPES['담백설']
            conv_manager.add_message("ai", f"""
**{info['name']}** 선택하셨습니다.

{info['analysis']}

이 시스템을 원장님 병원에 붙이면, 환자가 스스로 "내 몸이 심각하구나"를 깨닫고 예약합니다.

아래에 병원명, 성함, 연락처만 남겨주시면 24시간 안에 견적서를 보내드립니다.
""")
            conv_manager.update_stage("conversion")
            st.rerun()
    
    with col2:
        if st.button("🦷 치흔설"):
            conv_manager.add_message("user", "[선택: 치흔설]")
            info = TONGUE_TYPES['치흔설']
            conv_manager.add_message("ai", f"""
**{info['name']}** 선택하셨습니다.

{info['analysis']}

이 시스템을 원장님 병원에 붙이면, 환자가 스스로 "내 몸이 심각하구나"를 깨닫고 예약합니다.

아래에 병원명, 성함, 연락처만 남겨주시면 24시간 안에 견적서를 보내드립니다.
""")
            conv_manager.update_stage("conversion")
            st.rerun()
    
    with col3:
        if st.button("🟡 황태설"):
            conv_manager.add_message("user", "[선택: 황태설]")
            info = TONGUE_TYPES['황태설']
            conv_manager.add_message("ai", f"""
**{info['name']}** 선택하셨습니다.

{info['analysis']}

이 시스템을 원장님 병원에 붙이면, 환자가 스스로 "내 몸이 심각하구나"를 깨닫고 예약합니다.

아래에 병원명, 성함, 연락처만 남겨주시면 24시간 안에 견적서를 보내드립니다.
""")
            conv_manager.update_stage("conversion")
            st.rerun()
    
    with col4:
        if st.button("🟣 자색설"):
            conv_manager.add_message("user", "[선택: 자색설]")
            info = TONGUE_TYPES['자색설']
            conv_manager.add_message("ai", f"""
**{info['name']}** 선택하셨습니다.

{info['analysis']}

이 시스템을 원장님 병원에 붙이면, 환자가 스스로 "내 몸이 심각하구나"를 깨닫고 예약합니다.

아래에 병원명, 성함, 연락처만 남겨주시면 24시간 안에 견적서를 보내드립니다.
""")
            conv_manager.update_stage("conversion")
            st.rerun()

# CTA 폼
if current_stage == "conversion":
    st.markdown("---")
    with st.form("lead_form"):
        clinic = st.text_input("병원명")
        name = st.text_input("원장님 성함")
        contact = st.text_input("연락처")
        
        if st.form_submit_button("무료 견적서 받기"):
            st.success(f"{name} 원장님, 감사합니다! 24시간 안에 연락드리겠습니다.")

# 입력
user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    conv_manager.add_message("user", user_input)
    st.session_state.count += 1
    
    # 1단계
    if st.session_state.count == 1:
        time.sleep(0.5)
        conv_manager.add_message("ai", "언제 제일 힘드세요? 아침에 눈뜰 때인가요, 아니면 오후 3시쯤인가요?")
        conv_manager.update_stage("sleep_check")
    
    # 2단계
    elif st.session_state.count == 2:
        time.sleep(0.5)
        conv_manager.add_message("ai", "역시 그렇군요. 혹시 식사 후에 유독 졸리거나 속이 더부룩하진 않으신가요?")
        conv_manager.update_stage("digestion_check")
    
    # 3단계
    elif st.session_state.count == 3:
        time.sleep(0.5)
        conv_manager.add_message("ai", """
**분석 완료**

증상을 정리하면:
- 아침 기상 시 피로 (수면 회복력 저하)
- 식후 졸음/더부룩함 (비위 기능 저하)

이는 **비기허 + 습담 정체**의 전형적 패턴입니다.

이제 혀 상태를 확인하여, 환자가 스스로 "내 몸이 망가졌구나"를 깨닫게 만들겠습니다.
""")
        conv_manager.update_stage("tongue_select")
    
    st.rerun()

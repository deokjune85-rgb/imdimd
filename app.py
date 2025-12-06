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
    TONGUE_TYPES
)

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="IMD Strategic Consulting",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS
# ============================================
st.markdown(f"""
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
""", unsafe_allow_html=True)

# ============================================
# 초기화
# ============================================
conv_manager = get_conversation_manager()
prompt_engine = get_prompt_engine()
lead_handler = LeadHandler()

# B2B 모드 시작 메시지
if 'app_initialized' not in st.session_state:
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
    st.session_state.mode = 'simulation'  # simulation -> closing
    st.session_state.conversation_count = 0

# ============================================
# 헤더
# ============================================
st.markdown("""
<div class="title-box">
    <h1>IMD STRATEGIC CONSULTING</h1>
    <div class="sub">원장님의 진료 철학을 완벽하게 학습한 'AI 수석 실장'을 소개합니다</div>
    <div class="sub" style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">엑셀은 기록만 하지만, AI는 '매출'을 만듭니다 (체험시간: 2분)</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# 채팅 히스토리
# ============================================
with st.container():
    chat_html = '<div class="chat-area">'

    for msg in conv_manager.get_history():
        if msg['role'] == 'ai':
            chat_html += f'<div class="ai-msg">{msg["text"]}</div>'
        elif msg['role'] == 'user':
            chat_html += f'<div class="msg-right"><span class="user-msg">{msg["text"]}</span></div>'

    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

# ============================================
# 혀 사진 선택 (digestion_check 단계 후 표시)
# ============================================
context = conv_manager.get_context()
chat_history = conv_manager.get_history()

# digestion_check이고, 혀 미선택이고, 마지막 메시지에 "거울" 또는 "혀" 포함 시에만 UI 표시
show_tongue_ui = (
    context.get('stage') == 'digestion_check' 
    and not context.get('selected_tongue')
    and chat_history 
    and chat_history[-1]['role'] == 'ai'
    and ('거울' in chat_history[-1]['text'] or '혀' in chat_history[-1]['text'])
)

if show_tongue_ui:
    with st.container():
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:20px; margin:4px 0 8px 0;">거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요</div>',
            unsafe_allow_html=True
        )
        
        # 1x4 가로 배열로 혀 사진 표시
        cols = st.columns(4)
        
        from PIL import Image
        
        for idx, (tongue_key, tongue_data) in enumerate(TONGUE_TYPES.items()):
            with cols[idx]:
                # 혀 사진 표시
                image_path = tongue_data['image']
                
                try:
                    img = Image.open(image_path)
                    st.image(img, use_container_width=True)
                except Exception as e:
                    # 이미지 로드 실패시 이모지로 대체
                    st.markdown(
                        f"<div style='text-align:center; font-size:80px; padding:20px 0;'>{tongue_data['emoji']}</div>",
                        unsafe_allow_html=True
                    )
                
                # 이름 표시 - 검은색으로 변경
                st.markdown(
                    f"<div style='text-align:center; font-size:13px; font-weight:600; margin:4px 0; color:#1F2937;'>{tongue_data['name']}</div>",
                    unsafe_allow_html=True
                )
                
                # 선택 버튼
                if st.button(f"선택", key=f"tongue_{tongue_key}", use_container_width=True):
                    conv_manager.update_context('selected_tongue', tongue_key)
                    conv_manager.update_stage('tongue_select')
                    
                    # 혀 진단 메시지 추가
                    diagnosis_msg = f"""**{tongue_data['name']}** 선택하셨습니다.

{tongue_data['analysis']}

**주요 증상**: {tongue_data['symptoms']}

⚠️ **경고**: {tongue_data['warning']}

---

원장님, 방금 보신 과정이 실제로 제가 환자에게 자동으로 진행하는 흐름입니다.

**제가 한 일:**
1. "피곤해요" → "언제부터? 얼마나?" 구체적으로 물었습니다
2. 수면, 소화 패턴을 쪼개서 물어봤습니다
3. 혀 사진으로 "내 몸이 심각하구나"를 스스로 깨닫게 만들었습니다

이 대화를 원장님 병원 홈페이지에 24시간 붙여두면?

**밤 11시에 "만성 피로 한의원" 검색하는 직장인**에게 제가 알아서:
- 증상 듣고
- 위기감 조성하고  
- "이건 한약이 필요하겠네요" 단계까지 끌어올려서
- 예약까지 받아둡니다

실제 사례:
서울 A한의원 (월 신규 80명 수준)
→ AI 도입 후 온라인 문의 40% 증가
→ 예약 전환율 18% → 22.5% (약 25% 상승)

폭발적인 매출 신화가 아닙니다. 
다만 원장님이 직접 설명해야 했던 부분을 AI가 온라인에서 대신 떠받쳐주는 결과입니다."""
                    
                    conv_manager.add_message("ai", diagnosis_msg)
                    
                    # 건강 점수 계산
                    conv_manager.calculate_health_score()
                    conv_manager.update_stage('conversion')  # diagnosis → conversion으로 변경
                    
                    st.rerun()
        
        # 투명 스페이서 버튼 (채팅창 가림 방지용)
        st.markdown('<div style="height:150px;"></div>', unsafe_allow_html=True)

# ============================================
# 자동 CTA (시뮬레이션 완료 후)
# ============================================
chat_history = conv_manager.get_history()
last_msg_is_ai = chat_history and chat_history[-1]['role'] == 'ai'
current_stage = conv_manager.get_context()['stage']
selected_tongue = conv_manager.get_context().get('selected_tongue')

# conversion 단계이고 혀를 선택했을 때만 CTA 표시
if current_stage == 'conversion' and selected_tongue and current_stage != 'complete':
    with st.container():
        st.markdown("---")
        st.markdown(
            f'<div style="text-align:center; color:{COLOR_PRIMARY}; font-weight:600; font-size:18px; margin:20px 0 10px;">이 시스템을 한의원에 도입하시겠습니까?</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:#6B7280; font-size:14px; margin-bottom:20px;'>지역구 독점권은 선착순입니다. 무료 도입 견적서를 보내드립니다</p>",
            unsafe_allow_html=True
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
                        'name': director_name,
                        'contact': contact,
                        'symptom': f"병원명: {clinic_name}",
                        'preferred_date': '즉시 상담 희망',
                        'chat_summary': conv_manager.get_summary(),
                        'source': 'IMD_Strategic_Consulting',
                        'type': 'Oriental_Clinic'
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

담당 컨설턴트가 직접 연락드려 상세히 안내해드리겠습니다.
"""
                        conv_manager.add_message("ai", completion_msg)
                        conv_manager.update_stage('complete')
                        
                        st.success("견적서 신청이 완료되었습니다!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"오류: {message}")

# ============================================
# 입력창
# ============================================
user_input = st.chat_input("원장님의 생각을 말씀해주세요")

if user_input:
    conv_manager.add_message("user", user_input, metadata={"type": "text"})
    
    # 대화 카운트 증가
    if 'conversation_count' not in st.session_state:
        st.session_state.conversation_count = 0
    st.session_state.conversation_count += 1
    
    context = conv_manager.get_context()
    current_stage = context.get('stage', 'initial')
    history = conv_manager.get_formatted_history(for_llm=True)
    user_lower = user_input.lower()
    
    # ========================================
    # 증상별 분기 처리 (initial 단계에서만)
    # ========================================
    if current_stage == 'initial':
        # 1) 다리 쥐 / 저림 / 통증
        if any(word in user_lower for word in ['쥐', '저리', '다리', '통증', '아프', '결림']):
            ai_response = """다리에 쥐가 나신다니, 불편하시겠습니다.

혈액 순환이나 근육의 영양 공급에 문제가 있을 수 있습니다.

**구체적으로 여쭤보겠습니다:**
- 주로 언제 쥐가 나나요? (자다가? 운동 중?)
- 어느 부위인가요? (종아리? 허벅지?)
- 손발이 차갑거나 저린 증상도 있으신가요?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
            
        # 2) 다이어트 / 살 / 체중
        elif any(word in user_lower for word in ['다이어트', '살', '체중', '뚱뚱', '비만', '빠지', '감량']):
            ai_response = """체중 관리에 관심이 있으시군요.

한의학에서는 단순히 칼로리만이 아니라, **몸의 대사 기능**을 중요하게 봅니다.

**몇 가지 여쭤보겠습니다:**
- 식사량은 많지 않은데도 살이 찌시나요?
- 붓기가 심한 편인가요?
- 소화는 잘 되시나요?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
            
        # 3) 불면 / 수면 / 잠
        elif any(word in user_lower for word in ['잠', '수면', '불면', '못자', '새벽', '깨']):
            ai_response = """수면에 문제가 있으시군요. 잠은 건강의 기본입니다.

**좀 더 구체적으로 여쭤보겠습니다:**
- 잠들기가 어려우신가요? 아니면 자다가 자주 깨시나요?
- 새벽 몇 시쯤 깨시나요?
- 머리가 복잡하거나 가슴이 두근거리시나요?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
            
        # 4) 소화 / 속 / 더부룩
        elif any(word in user_lower for word in ['소화', '속', '더부룩', '체', '명치', '배', '복통']):
            ai_response = """소화가 불편하시군요. 비위(소화기) 기능을 점검해봐야 할 것 같습니다.

**증상을 좀 더 구체적으로 알려주세요:**
- 언제 더 불편하신가요? (식후? 공복?)
- 트림이나 명치 답답함이 있으신가요?
- 대변은 규칙적인가요?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
            
        # 5) 두통 / 어지럼
        elif any(word in user_lower for word in ['두통', '머리', '어지럼', '현기증']):
            ai_response = """두통이나 어지럼증은 일상생활에 큰 지장을 주죠.

**패턴을 파악해보겠습니다:**
- 어떤 두통인가요? (지끈지끈? 띠 두른 듯? 욱신욱신?)
- 주로 언제 심해지나요?
- 메스꺼움이나 구토도 동반되나요?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
            
        # 6) 피로 (기본 루트)
        else:
            ai_response = """피곤하시군요. 많은 분들이 비슷한 증상을 호소하십니다.

좀 더 정확히 파악하기 위해 여쭤보겠습니다.

**언제 가장 힘드신가요?**
- 아침에 눈뜰 때?
- 오후 시간대?
- 하루종일 계속?"""
            conv_manager.add_message("ai", ai_response)
            conv_manager.update_stage('symptom_explore')
            st.rerun()
        
    elif current_stage == 'symptom_explore':
        # 시간대 답변 → 수면 질문
        ai_response = """그렇군요. 그 시간대에 특히 힘드시다는 건, 단순 과로가 아닐 수 있습니다.

**수면은 어떠신가요?**
- 잠은 몇 시간 정도 주무세요?
- 자고 일어나도 개운하지 않으신가요?"""
        conv_manager.add_message("ai", ai_response)
        conv_manager.update_stage('sleep_check')
        st.rerun()
        
    elif current_stage == 'sleep_check':
        # 수면 답변 → 소화 질문
        ai_response = """잠을 자도 피로가 안 풀리신다면, 에너지 충전 기능 자체에 문제가 있는 것 같습니다.

**소화는 어떠세요?**
- 식사 후에 더 피곤해지시나요?
- 속이 더부룩하거나 소화가 안 되시나요?"""
        conv_manager.add_message("ai", ai_response)
        conv_manager.update_stage('digestion_check')
        st.rerun()
        
    elif current_stage == 'digestion_check':
        # 소화 답변 → 혀 선택 안내
        ai_response = """소화와 피로가 함께 오시는군요. 이는 **비위(소화기) 기능 저하**로 인해 기혈 생성이 안 되는 상태일 가능성이 높습니다.

이제 정확한 진단을 위해 **혀 상태**를 확인해보겠습니다.

거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요."""
        conv_manager.add_message("ai", ai_response)
        # stage는 그대로 유지 (혀 선택 UI가 나와야 함)
        st.rerun()
        
    else:
        # 기타 단계에서는 AI 응답
        time.sleep(1.0)
        ai_response = generate_ai_response(user_input, context, history)
        conv_manager.add_message("ai", ai_response)
        st.rerun()

# ============================================
# 완료 후
# ============================================
if conv_manager.get_context()['stage'] == 'complete':
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
st.markdown("""
<div class="footer">
    <b>IMD Strategic Consulting</b><br>
    한의원 전용 AI 매출 엔진 | 전국 200개 한의원 도입 완료
</div>
""", unsafe_allow_html=True)

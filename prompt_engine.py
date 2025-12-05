# app.py
# prompt_engine.py
"""
IMD Sales Bot - Main Application
다크 엘레강스 (McKinsey 컨설팅 스타일)
IMD Sales Bot - AI Response Generation
Gemini 전용 + Fallback 방지 강화
"""

import streamlit as st
import google.generativeai as genai
from typing import Dict, Optional
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
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    CASE_STUDIES,
    MAX_RETRY_ATTEMPTS
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
class PromptEngine:
    """AI 응답 생성 엔진 (Fallback 방지 강화)"""

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(12px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    def __init__(self):
        """Gemini API 초기화"""
        self.model = None
        self.retry_count = 0
        self._init_gemini()

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
    def _init_gemini(self):
        """Gemini API 설정"""
        try:
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
                self.model = None
                return
            
            api_key = st.secrets["GEMINI_API_KEY"]
            
            if not api_key:
                st.error("❌ API 키가 비어있습니다.")
                self.model = None
                return
            
            # Gemini 설정
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                generation_config={
                    "temperature": GEMINI_TEMPERATURE,
                    "max_output_tokens": GEMINI_MAX_TOKENS,
                }
            )
            
            # 초기화 성공 표시 (한번만)
            if 'gemini_initialized' not in st.session_state:
                st.success(f"✅ AI 컨설턴트 준비 완료")
                st.session_state.gemini_initialized = True
            
        except Exception as e:
            st.error(f"❌ 시스템 초기화 실패: {str(e)}")
            self.model = None

    /* 섹션 제목 */
    .section-title {{
        color: {COLOR_PRIMARY};
        font-size: 18px;
        font-weight: 600;
        margin: 24px 0 12px 0;
        text-align: center;
    }}
    def generate_response(
        self,
        user_input: str,
        context: Dict,
        conversation_history: str
    ) -> str:
        """
        AI 응답 생성 (재시도 로직 포함)
        """
        if not self.model:
            st.error("⚠️ AI 시스템이 연결되지 않았습니다. 관리자에게 문의하세요.")
            return self._fallback_response(user_input, context)
        
        # 재시도 로직
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # 프롬프트 생성
                full_prompt = self._build_prompt(user_input, context, conversation_history)
                
                # Gemini 호출
                response = self.model.generate_content(full_prompt)
                
                # 응답 검증
                if not response or not response.text:
                    raise ValueError("빈 응답 수신")
                
                # 응답 후처리
                ai_response = self._post_process_response(response.text.strip(), context)
                
                # 성공 시 재시도 카운트 리셋
                self.retry_count = 0
                
                return ai_response
                
            except Exception as e:
                self.retry_count += 1
                error_msg = str(e)
                
                # 마지막 시도에서 실패
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    st.error(f"⚠️ AI 응답 생성 실패 (시도 {attempt + 1}/{MAX_RETRY_ATTEMPTS})")
                    st.error(f"오류: {error_msg}")
                    
                    # 에러 타입별 안내
                    if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                        st.warning("💡 API 사용량 초과. 잠시 후 다시 시도해주세요.")
                    elif "invalid" in error_msg.lower():
                        st.warning("💡 API 키 오류. 관리자에게 문의하세요.")
                    
                    return self._fallback_response(user_input, context)
                else:
                    # 재시도
                    st.warning(f"재시도 중... ({attempt + 1}/{MAX_RETRY_ATTEMPTS})")
                    time.sleep(1)  # 1초 대기 후 재시도
        
        return self._fallback_response(user_input, context)

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
    def _build_prompt(
        self,
        user_input: str,
        context: Dict,
        conversation_history: str
    ) -> str:
        """프롬프트 조립"""
        system_prompt = SYSTEM_PROMPT.format(
            user_type=context.get('user_type') or '미파악',
            pain_point=context.get('pain_point') or '미파악',
            stage=context.get('stage', 'initial'),
            trust_level=context.get('trust_level', 0)
        )
        
        # 반박 사항 대응
        if context.get('objections'):
            objection_guide = self._get_objection_handling(context['objections'])
            system_prompt += f"\n\n## 현재 고객 우려사항\n{objection_guide}"
        
        # 사례 연구 추가
        if context.get('user_type') in CASE_STUDIES:
            case = CASE_STUDIES[context['user_type']]
            system_prompt += f"\n\n## 제시 가능한 실제 사례\n- {case['title']}: {case['result']}\n- 정량 데이터: {case['data']}"
        
        full_prompt = f"""{system_prompt}

# 첫 방문 시 웰컴 메시지
if len(conv_manager.get_history()) == 0:
    initial_msg = prompt_engine.generate_initial_message()
    conv_manager.add_message("ai", initial_msg)
---

# ============================================
# 3. 헤더
# ============================================
st.title("IMD AI 전략 컨설팅")
st.markdown('<p class="subtitle">데이터 기반 비즈니스 성장 솔루션</p>', unsafe_allow_html=True)
## 최근 대화 내역
{conversation_history}

# ============================================
# 4. 채팅 히스토리 렌더링
# ============================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
---

for chat in conv_manager.get_history():
    role_class = "chat-bubble-ai" if chat['role'] == 'ai' else "chat-bubble-user"
    st.markdown(f'<div class="{role_class}">{chat["text"]}</div>', unsafe_allow_html=True)
## 고객의 최신 입력
{user_input}

st.markdown('</div>', unsafe_allow_html=True)
---

# ============================================
# 5. 추천 버튼
# ============================================
if not conv_manager.is_ready_for_conversion():
    st.markdown('<p class="section-title">주요 문의 사항</p>', unsafe_allow_html=True)
**전문 컨설턴트로서 응답하세요. 2-4문장, 데이터 기반, 명확한 제안.**
"""
        return full_prompt

    buttons = conv_manager.get_recommended_buttons()
    def _get_objection_handling(self, objections: list) -> str:
        """반박 사항 대응 전략"""
        strategies = {
            'skeptical': "→ 정량 데이터로 증명. '도입 6개월, 전환율 32% 상승' 같은 구체적 수치 제시",
            'complexity': "→ '초기 셋업 3일, 직원 교육 2시간' 같이 구체적 일정 명시",
            'price_sensitive': "→ ROI 중심. '월 200만원 투자 시 회수 기간 3개월, 연간 2,400만원 추가 매출'"
        }
        
        guide = [strategies[obj] for obj in objections if obj in strategies]
        return "\n".join(guide) if guide else "데이터 기반 해결책 제시"

    # 버튼 레이아웃
    if len(buttons) == 3:
        cols = st.columns(3)
    else:
        cols = st.columns(len(buttons))
    def _post_process_response(self, response: str, context: Dict) -> str:
        """응답 후처리"""
        import re
        
        # 줄바꿈 정리
        response = response.replace('\n\n\n', '\n\n')
        
        # 마크다운 굵기 처리
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        # 길이 제한 (600자)
        if len(response) > 600:
            response = response[:580] + "\n\n추가 정보가 필요하신가요?"
        
        # 금지 단어 필터
        forbidden_words = {
            'LLM': 'AI 시스템',
            'RAG': 'AI 기술',
            'API': '시스템',
            '머신러닝': 'AI',
            '딥러닝': 'AI'
        }
        
        for word, replacement in forbidden_words.items():
            response = response.replace(word, replacement)
        
        # CTA 추가 (적절한 타이밍)
        if context.get('trust_level', 0) >= 50 and '설계' not in response.lower():
            response += "\n\n아래 정보를 남겨주시면 맞춤 분석 리포트를 발송해드립니다."
        
        return response

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
    def _fallback_response(self, user_input: str, context: Dict) -> str:
        """Fallback 응답 (최소한으로만 사용)"""
        user_lower = user_input.lower()
        
        # 가격 문의
        if any(word in user_lower for word in ['가격', '비용', '얼마', '요금']):
            return """투자 금액보다 중요한 것은 투자 회수 기간입니다.

# ============================================
# 6. 채팅 입력창
# ============================================
user_input = st.chat_input("문의 사항을 입력하세요")
현재 월 방문자 수와 전환율을 공유해주시면, 정확한 ROI를 산출해드리겠습니다.

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
아래 간단한 정보만 남겨주시면 맞춤 분석을 제공합니다."""

        company = st.text_input("기업명 / 병원명", placeholder="예: (주)ABC컴퍼니")
        urgency = st.selectbox("도입 희망 시기", URGENCY_OPTIONS)
        # 효과 의심
        elif any(word in user_lower for word in ['효과', '진짜', '정말', '의심']):
            case = CASE_STUDIES.get(context.get('user_type', 'hospital'))
            return f"""데이터로 말씀드리겠습니다.

{case['title']} 도입 사례:
- {case['result']}
- {case['data']}

상세 분석 리포트를 확인하시겠습니까?"""

        submitted = st.form_submit_button("제안서 신청", use_container_width=True)
        # 시간 부족
        elif any(word in user_lower for word in ['시간', '바쁘', '나중']):
            return """이해합니다.

핵심만 말씀드리면, 현재 놓치는 고객의 평균 30%를 AI가 자동 전환합니다.

간단한 연락처만 남겨주시면 분석 리포트를 발송해드립니다."""

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
        # 기본 응답
        else:
            return """현재 사업의 핵심 과제를 파악하고 싶습니다.

**{name}님**, 감사합니다.
다음 중 가장 시급한 문제는 무엇인가요?

담당 컨설턴트가 **24시간 내**로 아래 연락처로 맞춤 분석 리포트와 함께 연락드립니다.
1. 광고 대비 매출 효율
2. 고객 전환율
3. 운영 인력 부족

**연락처**: {contact}  
**희망 시기**: {urgency}
구체적으로 말씀해주시면 맞춤 솔루션을 제안드립니다."""
    
    def generate_initial_message(self) -> str:
        """첫 메시지"""
        return """안녕하십니까. <b>IMD 아키텍처 그룹</b> 수석 컨설턴트입니다.

---
대표님 사업의 핵심 과제를 파악하고 싶습니다.

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
현재 <b>마케팅 투자 대비 효율(ROAS)</b>에 만족하고 계십니까?"""

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
def get_prompt_engine() -> PromptEngine:
    """싱글톤 인스턴스"""
    if 'prompt_engine' not in st.session_state:
        st.session_state.prompt_engine = PromptEngine()
    return st.session_state.prompt_engine

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

def generate_ai_response(user_input: str, context: Dict, history: str) -> str:
    """빠른 호출"""
    engine = get_prompt_engine()
    return engine.generate_response(user_input, context, history)

# prompt_engine.py
"""
IMD Sales Bot - AI Response Generation
Gemini API 전용 (디버깅 강화)
"""

import streamlit as st
import google.generativeai as genai
from typing import Dict, Optional
from config import (
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    CASE_STUDIES
)

class PromptEngine:
    """AI 응답 생성 엔진 (Gemini 전용)"""
    
    def __init__(self):
        """Gemini API 초기화"""
        self.model = None
        self._init_gemini()
    
    def _init_gemini(self):
        """Gemini API 설정"""
        try:
            # Secrets 확인
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("❌ st.secrets에 'GEMINI_API_KEY'가 없습니다!")
                st.info("Streamlit Cloud > Settings > Secrets에 추가하세요.")
                self.model = None
                return
            
            api_key = st.secrets["GEMINI_API_KEY"]
            
            if not api_key or api_key == "":
                st.error("❌ GEMINI_API_KEY가 비어있습니다!")
                self.model = None
                return
            
            # API 키 유효성 표시 (처음 3글자만)
            st.success(f"✅ Gemini API 키 감지됨: {api_key[:8]}...")
            
            # Gemini 설정
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                generation_config={
                    "temperature": GEMINI_TEMPERATURE,
                    "max_output_tokens": GEMINI_MAX_TOKENS,
                }
            )
            
            st.success(f"✅ Gemini 모델 초기화 완료: {GEMINI_MODEL}")
            
        except Exception as e:
            st.error(f"❌ Gemini API 초기화 실패: {str(e)}")
            import traceback
            st.code(traceback.format_exc(), language="python")
            self.model = None
    
    def generate_response(
        self,
        user_input: str,
        context: Dict,
        conversation_history: str
    ) -> str:
        """
        사용자 입력에 대한 AI 응답 생성
        
        Args:
            user_input: 사용자 메시지
            context: 대화 컨텍스트 (user_type, pain_point 등)
            conversation_history: 최근 대화 히스토리
        
        Returns:
            AI 응답 텍스트
        """
        # 디버그 정보
        st.info(f"🔧 DEBUG: 모델 연결 상태 = {'연결됨' if self.model else '미연결'}")
        
        if not self.model:
            st.warning("⚠️ Gemini 미연결 - Fallback 응답 사용")
            return self._fallback_response(user_input, context)
        
        try:
            st.info("🔧 DEBUG: 프롬프트 생성 중...")
            
            # 동적 System Prompt 생성
            full_prompt = self._build_prompt(user_input, context, conversation_history)
            
            st.info(f"🔧 DEBUG: 프롬프트 길이 = {len(full_prompt)} 글자")
            st.info("🔧 DEBUG: Gemini API 호출 시작...")
            
            # Gemini API 호출
            response = self.model.generate_content(full_prompt)
            
            st.success("🔧 DEBUG: Gemini 응답 받음!")
            st.info(f"🔧 DEBUG: 원본 응답 길이 = {len(response.text)} 글자")
            
            # 응답 후처리
            ai_response = self._post_process_response(response.text.strip(), context)
            
            st.success(f"🔧 DEBUG: 최종 응답 길이 = {len(ai_response)} 글자")
            
            # 응답 미리보기 (처음 100자)
            st.code(ai_response[:100] + "...", language="text")
            
            return ai_response
            
        except Exception as e:
            st.error(f"❌ AI 응답 생성 실패: {str(e)}")
            
            # 상세 에러 로그
            import traceback
            error_detail = traceback.format_exc()
            st.code(error_detail, language="python")
            
            # 에러 타입별 안내
            error_str = str(e).lower()
            if "quota" in error_str or "rate" in error_str:
                st.warning("💡 API 할당량 초과! 잠시 후 다시 시도하세요.")
            elif "invalid" in error_str:
                st.warning("💡 API 키가 유효하지 않습니다. Secrets 확인하세요.")
            
            return self._fallback_response(user_input, context)
    
    def _build_prompt(
        self,
        user_input: str,
        context: Dict,
        conversation_history: str
    ) -> str:
        """
        최종 프롬프트 조립
        
        Args:
            user_input: 사용자 메시지
            context: 컨텍스트
            conversation_history: 대화 히스토리
        
        Returns:
            완성된 프롬프트
        """
        # System Prompt에 컨텍스트 주입
        system_prompt = SYSTEM_PROMPT.format(
            user_type=context.get('user_type') or '미파악',
            pain_point=context.get('pain_point') or '미파악',
            stage=context.get('stage', 'initial'),
            trust_level=context.get('trust_level', 0)
        )
        
        # 반박 사항 대응 전략 추가
        if context.get('objections'):
            objection_guide = self._get_objection_handling(context['objections'])
            system_prompt += f"\n\n## 현재 고객 우려사항\n{objection_guide}"
        
        # 사례 연구 추가 (업종별)
        if context.get('user_type') in CASE_STUDIES:
            case = CASE_STUDIES[context['user_type']]
            system_prompt += f"\n\n## 제시할 수 있는 실제 사례\n- {case['title']}: {case['result']}\n- 고객 후기: \"{case['quote']}\""
        
        # 최종 프롬프트 조립
        full_prompt = f"""{system_prompt}

---

## 최근 대화 내역
{conversation_history}

---

## 고객의 최신 입력
고객: {user_input}

---

**위 맥락을 고려하여, 지금 즉시 응답하세요.**
응답은 3-5문장 이내로 간결하게 작성하세요.
핵심 메시지 하나에 집중하세요.
"""
        return full_prompt
    
    def _get_objection_handling(self, objections: list) -> str:
        """
        반박 사항별 대응 전략
        
        Args:
            objections: 우려 사항 리스트
        
        Returns:
            대응 가이드
        """
        strategies = {
            'skeptical': "→ 실제 사례와 구체적 수치로 증명하세요. '지금 저와 대화하는 것처럼...' 프레임 사용",
            'complexity': "→ '설치 3일, 교육 1시간이면 끝' 같이 구체적 일정 제시",
            'price_sensitive': "→ 가격이 아닌 ROI로 전환. '월 200만원 투자로 월 1000만원 추가 매출' 식으로 제시"
        }
        
        guide = []
        for obj in objections:
            if obj in strategies:
                guide.append(strategies[obj])
        
        return "\n".join(guide) if guide else "고객의 우려를 공감하고 구체적 해결책 제시"
    
    def _post_process_response(self, response: str, context: Dict) -> str:
        """
        AI 응답 후처리 (포맷팅, 안전장치)
        
        Args:
            response: 원본 응답
            context: 컨텍스트
        
        Returns:
            처리된 응답
        """
        # 1. 과도한 줄바꿈 제거
        response = response.replace('\n\n\n', '\n\n')
        
        # 2. 마크다운 굵기 처리 (** → <b>)
        import re
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
        
        # 3. 너무 길면 자르기 (500자 제한)
        if len(response) > 500:
            response = response[:480] + "...\n\n계속 들어보시겠어요?"
        
        # 4. 금지 단어 필터링
        forbidden = ['LLM', 'RAG', 'API', '머신러닝', '딥러닝']
        for word in forbidden:
            if word in response:
                response = response.replace(word, 'AI 기술')
        
        # 5. CTA 자동 추가 (전환 타이밍)
        if context.get('trust_level', 0) >= 60 and '무료' not in response:
            response += "\n\n💡 지금 무료 설계도라도 받아보시는 건 어떨까요?"
        
        return response
    
    def _fallback_response(self, user_input: str, context: Dict) -> str:
        """
        API 실패 시 폴백 응답 (규칙 기반)
        
        Args:
            user_input: 사용자 입력
            context: 컨텍스트
        
        Returns:
            폴백 응답
        """
        user_lower = user_input.lower()
        
        # 키워드 기반 단순 응답
        if any(word in user_lower for word in ['가격', '비용', '얼마']):
            return """대표님, 솔직히 말씀드리면 '가격'보다 중요한 게 있습니다.
            
지금 홈페이지 방문자 100명 중 몇 명이 구매/예약하시나요?
만약 2%라면, AI로 3%만 올려도 월매출이 50% 늘어납니다.

투자 대비 수익(ROI)을 먼저 계산해보시겠어요?"""
        
        elif any(word in user_lower for word in ['효과', '진짜', '정말']):
            case = CASE_STUDIES.get(context.get('user_type', 'hospital'))
            return f"""당연히 의심스러우실 겁니다. 근데 대표님, 지금 저와 대화하시면서 느끼셨나요?

제가 사람처럼 대답한다는 걸?

실제로 <b>{case['title']}</b>는 도입 후 <b>{case['result']}</b> 달성했습니다.

"{case['quote']}"

실제 사례를 더 보시겠어요?"""
        
        elif any(word in user_lower for word in ['시간', '바쁘', '나중']):
            return """대표님, 딱 2분만 투자하세요.
            
지금 경쟁사들은 AI로 야간/주말 고객까지 잡고 있습니다.
대표님이 '나중에'를 고민하는 사이, 고객은 다른 곳으로 갑니다.

무료 설계도는 받아두시고 검토하셔도 됩니다. 손해 볼 게 없잖아요?"""
        
        else:
            return """말씀 감사합니다. 더 자세히 듣고 싶은데요,

지금 가장 답답한 부분이 뭔가요?
1️⃣ 광고비 대비 매출이 안 나와서?
2️⃣ 고객이 문의만 하고 구매/예약 안 해서?
3️⃣ 직원들이 야근해도 대응이 안 돼서?

편하게 말씀해주세요."""
    
    def generate_initial_message(self) -> str:
        """
        첫 인사 메시지 생성 (고정)
        
        Returns:
            첫 메시지
        """
        return """반갑습니다. <b>IMD 수석 아키텍트 AI</b>입니다.

대표님, 솔직히 말씀드리죠.

지금 <b>마케팅 비용 대비 효율(ROAS)</b>, 만족하시나요?"""


# ============================================
# 편의 함수
# ============================================
def get_prompt_engine() -> PromptEngine:
    """PromptEngine 싱글톤 인스턴스 반환"""
    if 'prompt_engine' not in st.session_state:
        st.session_state.prompt_engine = PromptEngine()
    return st.session_state.prompt_engine


def generate_ai_response(user_input: str, context: Dict, history: str) -> str:
    """
    빠른 AI 응답 생성 (앱에서 바로 호출용)
    
    Args:
        user_input: 사용자 메시지
        context: 컨텍스트
        history: 대화 히스토리
    
    Returns:
        AI 응답
    """
    engine = get_prompt_engine()
    return engine.generate_response(user_input, context, history)

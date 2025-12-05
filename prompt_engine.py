# prompt_engine.py
"""
IMD Sales Bot - AI Response Generation
Multi-LLM 지원 (Gemini, Groq, OpenRouter)
"""

import streamlit as st
from typing import Dict, Optional
from config import (
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    CASE_STUDIES
)

# LLM 선택에 따른 import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

try:
    import requests
    OPENROUTER_AVAILABLE = True
except:
    OPENROUTER_AVAILABLE = False

class PromptEngine:
    """AI 응답 생성 엔진 (Gemini, Groq, OpenRouter 지원)"""
    
    def __init__(self):
        """LLM API 초기화"""
        self.model = None
        self.llm_type = None  # 'gemini', 'groq', 'openrouter'
        self._init_llm()
    
    def _init_llm(self):
        """사용 가능한 LLM 자동 감지 및 초기화"""
        
        # 0순위: OpenRouter (가장 유연함, 여러 모델)
        if "OPENROUTER_API_KEY" in st.secrets and OPENROUTER_AVAILABLE:
            try:
                self.api_key = st.secrets["OPENROUTER_API_KEY"]
                # 모델 선택 (Secrets에서 지정 가능)
                self.model_name = st.secrets.get(
                    "OPENROUTER_MODEL", 
                    "google/gemini-2.0-flash-exp:free"  # 기본값: Gemini 무료
                )
                self.model = "openrouter"  # 플래그
                self.llm_type = "openrouter"
                st.success(f"✅ OpenRouter 연결 완료 (모델: {self.model_name})")
                return
            except Exception as e:
                st.warning(f"OpenRouter 초기화 실패: {e}")
        
        # 1순위: Groq (가장 빠르고 무료)
        if "GROQ_API_KEY" in st.secrets and GROQ_AVAILABLE:
            try:
                api_key = st.secrets["GROQ_API_KEY"]
                self.model = Groq(api_key=api_key)
                self.llm_type = "groq"
                st.success(f"✅ Groq API 연결 완료 (초고속 모드)")
                return
            except Exception as e:
                st.warning(f"Groq 초기화 실패: {e}")
        
        # 2순위: Gemini
        if "GEMINI_API_KEY" in st.secrets and GEMINI_AVAILABLE:
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    generation_config={
                        "temperature": GEMINI_TEMPERATURE,
                        "max_output_tokens": GEMINI_MAX_TOKENS,
                    }
                )
                self.llm_type = "gemini"
                st.success(f"✅ Gemini API 연결 완료")
                return
            except Exception as e:
                st.warning(f"Gemini 초기화 실패: {e}")
        
        # 모두 실패
        st.error("❌ 사용 가능한 LLM API가 없습니다!")
        st.info("""
        **Secrets에 다음 중 하나를 추가하세요:**
        
        1. OpenRouter (추천, 다양한 모델):
           ```
           OPENROUTER_API_KEY = "sk-or-v1-..."
           OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free"
           ```
           발급: https://openrouter.ai/keys
        
        2. Groq (빠름, 무료):
           ```
           GROQ_API_KEY = "gsk_..."
           ```
           발급: https://console.groq.com/keys
        
        3. Gemini:
           ```
           GEMINI_API_KEY = "AIza..."
           ```
           발급: https://aistudio.google.com/apikey
        """)
        self.model = None
        self.llm_type = None
    
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
        if not self.model:
            st.warning("⚠️ LLM 미연결 - Fallback 응답 사용")
            return self._fallback_response(user_input, context)
        
        try:
            # 디버그: LLM 타입 확인
            st.info(f"🔧 DEBUG: LLM 타입 = {self.llm_type}")
            
            # 동적 System Prompt 생성
            full_prompt = self._build_prompt(user_input, context, conversation_history)
            st.info(f"🔧 DEBUG: 프롬프트 길이 = {len(full_prompt)} 글자")
            
            # LLM별 호출 방식
            if self.llm_type == "openrouter":
                st.info("🔧 DEBUG: OpenRouter 호출 중...")
                response = self._call_openrouter(full_prompt)
            elif self.llm_type == "groq":
                st.info("🔧 DEBUG: Groq 호출 중...")
                response = self._call_groq(full_prompt)
            elif self.llm_type == "gemini":
                st.info("🔧 DEBUG: Gemini 호출 중...")
                response = self._call_gemini(full_prompt)
            else:
                st.error(f"🔧 DEBUG: 알 수 없는 LLM 타입: {self.llm_type}")
                return self._fallback_response(user_input, context)
            
            st.success(f"🔧 DEBUG: AI 응답 받음 (길이: {len(response)} 글자)")
            
            # 응답 후처리
            ai_response = self._post_process_response(response, context)
            st.success(f"🔧 DEBUG: 후처리 완료 (최종 길이: {len(ai_response)} 글자)")
            
            return ai_response
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            st.error(f"⚠️ AI 응답 생성 실패: {str(e)}")
            st.code(error_detail, language="python")
            return self._fallback_response(user_input, context)
    
    def _call_openrouter(self, prompt: str) -> str:
        """OpenRouter API 호출"""
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://imd-sales-bot.streamlit.app",  # 선택사항
                "X-Title": "IMD Sales Bot",  # 선택사항
            },
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.85,
                "max_tokens": 1000,
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API 오류: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_groq(self, prompt: str) -> str:
        """Groq API 호출"""
        chat_completion = self.model.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-70b-versatile",  # 가장 성능 좋은 무료 모델
            temperature=0.85,
            max_tokens=1000,
        )
        return chat_completion.choices[0].message.content
    
    def _call_gemini(self, prompt: str) -> str:
        """Gemini API 호출"""
        response = self.model.generate_content(prompt)
        return response.text
    
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
        response = response.replace('**', '<b>', 1).replace('**', '</b>', 1)
        
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

# prompt_engine.py
"""
IMD Sales Bot - AI Response Generation
Gemini 전용 + Fallback 방지 강화
"""

import streamlit as st
import google.generativeai as genai
from typing import Dict, Optional
import time
from config import (
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    CASE_STUDIES,
    MAX_RETRY_ATTEMPTS
)

class PromptEngine:
    """AI 응답 생성 엔진 (Fallback 방지 강화)"""
    
    def __init__(self):
        """Gemini API 초기화"""
        self.model = None
        self.retry_count = 0
        self._init_gemini()
    
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

---

## 최근 대화 내역
{conversation_history}

---

## 고객의 최신 입력
{user_input}

---

**전문 컨설턴트로서 응답하세요. 2-4문장, 데이터 기반, 명확한 제안.**
"""
        return full_prompt
    
    def _get_objection_handling(self, objections: list) -> str:
        """반박 사항 대응 전략"""
        strategies = {
            'skeptical': "→ 정량 데이터로 증명. '도입 6개월, 전환율 32% 상승' 같은 구체적 수치 제시",
            'complexity': "→ '초기 셋업 3일, 직원 교육 2시간' 같이 구체적 일정 명시",
            'price_sensitive': "→ ROI 중심. '월 200만원 투자 시 회수 기간 3개월, 연간 2,400만원 추가 매출'"
        }
        
        guide = [strategies[obj] for obj in objections if obj in strategies]
        return "\n".join(guide) if guide else "데이터 기반 해결책 제시"
    
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
    
    def _fallback_response(self, user_input: str, context: Dict) -> str:
        """Fallback 응답 (최소한으로만 사용)"""
        user_lower = user_input.lower()
        
        # 가격 문의
        if any(word in user_lower for word in ['가격', '비용', '얼마', '요금']):
            return """투자 금액보다 중요한 것은 투자 회수 기간입니다.

현재 월 방문자 수와 전환율을 공유해주시면, 정확한 ROI를 산출해드리겠습니다.

아래 간단한 정보만 남겨주시면 맞춤 분석을 제공합니다."""
        
        # 효과 의심
        elif any(word in user_lower for word in ['효과', '진짜', '정말', '의심']):
            case = CASE_STUDIES.get(context.get('user_type', 'hospital'))
            return f"""데이터로 말씀드리겠습니다.

{case['title']} 도입 사례:
- {case['result']}
- {case['data']}

상세 분석 리포트를 확인하시겠습니까?"""
        
        # 시간 부족
        elif any(word in user_lower for word in ['시간', '바쁘', '나중']):
            return """이해합니다.

핵심만 말씀드리면, 현재 놓치는 고객의 평균 30%를 AI가 자동 전환합니다.

간단한 연락처만 남겨주시면 분석 리포트를 발송해드립니다."""
        
        # 기본 응답
        else:
            return """현재 사업의 핵심 과제를 파악하고 싶습니다.

다음 중 가장 시급한 문제는 무엇인가요?

1. 광고 대비 매출 효율
2. 고객 전환율
3. 운영 인력 부족

구체적으로 말씀해주시면 맞춤 솔루션을 제안드립니다."""
    
    def generate_initial_message(self) -> str:
        """첫 메시지"""
        return """안녕하십니까. <b>IMD 아키텍처 그룹</b> 수석 컨설턴트입니다.

대표님 사업의 핵심 과제를 파악하고 싶습니다.

현재 <b>마케팅 투자 대비 효율(ROAS)</b>에 만족하고 계십니까?"""


def get_prompt_engine() -> PromptEngine:
    """싱글톤 인스턴스"""
    if 'prompt_engine' not in st.session_state:
        st.session_state.prompt_engine = PromptEngine()
    return st.session_state.prompt_engine


def generate_ai_response(user_input: str, context: Dict, history: str) -> str:
    """빠른 호출"""
    engine = get_prompt_engine()
    return engine.generate_response(user_input, context, history)

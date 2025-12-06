import time
from typing import Dict

import streamlit as st
import google.generativeai as genai

# ------------------------------------------------------
# config.py 의 값이 있으면 가져오고, 없으면 기본값 사용
# ------------------------------------------------------
try:
    from config import SYSTEM_PROMPT as CONFIG_SYSTEM_PROMPT
    from config import CASE_STUDIES as CONFIG_CASE_STUDIES
    from config import MAX_RETRY_ATTEMPTS as CONFIG_MAX_RETRY_ATTEMPTS
    from config import GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS
    from config import TONGUE_TYPES
except Exception:
    CONFIG_SYSTEM_PROMPT = None
    CONFIG_CASE_STUDIES = None
    CONFIG_MAX_RETRY_ATTEMPTS = None
    GEMINI_MODEL = "gemini-2.0-flash"
    GEMINI_TEMPERATURE = 0.6
    GEMINI_MAX_TOKENS = 1024
    TONGUE_TYPES = {}


# 기본 SYSTEM_PROMPT (config에 있으면 그걸 우선 사용)
DEFAULT_SYSTEM_PROMPT = """
[IMD Strategic Consulting - B2B Sales Bot Core System Prompt]

당신의 역할:
- 당신은 'IMD 아키텍처 그룹(IMD Architecture Group)'의 수석 컨설턴트이자 AI 아키텍트입니다.
- 당신의 목표는, 한의원/병원 원장에게 'AI 상담 실장 시스템'의 가치를 이해시키고, 도입을 자연스럽게 제안하는 것입니다.

현재 컨텍스트:
- 선택한 증상: {selected_symptom}
- 선택한 혀 타입: {selected_tongue}
- 건강 점수: {health_score}/100
- 현재 단계(stage): {stage}

단계별 행동 지침:

1) symptom_select 단계:
- 공감 멘트 1~2문장 + "이제 혀 상태를 확인해보겠습니다" 안내

2) tongue_select 단계:
- 선택한 혀 타입에 대한 분석 결과를 **경고 톤**으로 전달
- 구조: "혀 상태 관찰 → 한의학적 해석 → 위기감 조성"

3) result_view 단계:
- 종합 건강 점수 언급 + 솔루션 제안

4) conversion 단계 (클로징):
- "이 흐름이 AI가 자동으로 하는 일"이라고 설명

응답 스타일:
- 존댓말, 담백한 컨설팅 톤
- 2~6문장 분량
- 기술 용어 금지
"""

SYSTEM_PROMPT = CONFIG_SYSTEM_PROMPT or DEFAULT_SYSTEM_PROMPT

# 적용 사례 기본값
DEFAULT_CASE_STUDIES = {
    "hospital": {
        "title": "서울 A한의원 만성피로·다이어트 클리닉",
        "result": "야간 온라인 문의 응답률 100% 확보, 예약 전환율 약 20~25% 구간 상승",
        "data": "온라인 문의 40% 증가, 예약 전환율 18% → 22.5%",
    }
}
CASE_STUDIES = CONFIG_CASE_STUDIES or DEFAULT_CASE_STUDIES

# 재시도 횟수
MAX_RETRY_ATTEMPTS = CONFIG_MAX_RETRY_ATTEMPTS or 2


class PromptEngine:
    """IMD Sales Bot용 Gemini 응답 엔진 (B2B 세일즈 전용)"""

    def __init__(self):
        self.model = None
        self._init_gemini()

    def _init_gemini(self) -> None:
        """Gemini API 초기화"""
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

        if not api_key:
            try:
                st.error("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            except Exception:
                pass
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                generation_config={
                    "temperature": GEMINI_TEMPERATURE,
                    "max_output_tokens": GEMINI_MAX_TOKENS,
                },
            )
            if "gemini_initialized" not in st.session_state:
                st.session_state["gemini_initialized"] = True
        except Exception as e:
            try:
                st.error(f"❌ Gemini 초기화 실패: {e}")
            except Exception:
                pass
            self.model = None

    # --------------------------------------------------
    # 1) 첫 인사
    # --------------------------------------------------
    def generate_initial_message(self) -> str:
        """첫 인사 메시지 (원장 대상 B2B 세일즈 오프닝)"""
        return (
            "안녕하십니까, 원장님.\n\n"
            "저는 24시간 잠들지 않는 <b>AI 상담실장</b>입니다.\n\n"
            "진료실에서 이런 말, 자주 들으시죠?\n\n"
            "\"선생님… 생각보다 비싸네요. 그냥 침만 맞을게요.\"\n\n"
            "그 순간, 진료 동선도 끊기고, 원장님 마음도 같이 꺾이실 겁니다.\n\n"
            "저는 그 <b>직전 단계에서</b>, 환자의 마음을 열고\n"
            "시술과 프로그램을 받아들일 준비를 시키는 역할을 합니다.\n\n"
            "백문이 불여일견입니다. 지금부터 원장님은 잠시 "
            "'만성 피로 환자' 역할을 해봐 주십시오.\n\n"
            "<b>먼저, 오늘 원장님을 찾아온 가장 큰 이유가 무엇인지\n"
            "아래 4가지 중 하나를 선택해주세요.</b>"
        )

    # --------------------------------------------------
    # 2) 프롬프트 조립
    # --------------------------------------------------
    def _build_prompt(
        self,
        user_input: str,
        context: Dict,
        conversation_history: str,
    ) -> str:
        """SYSTEM_PROMPT + 컨텍스트 + 대화내역을 합쳐 LLM 프롬프트 생성"""
        selected_symptom = context.get("selected_symptom") or "미선택"
        selected_tongue = context.get("selected_tongue") or "미선택"
        health_score = context.get("health_score", 0)
        stage = context.get("stage", "initial")

        system = SYSTEM_PROMPT.format(
            selected_symptom=selected_symptom,
            selected_tongue=selected_tongue,
            health_score=health_score,
            stage=stage,
        )

        # 혀 타입 상세 정보 추가
        if selected_tongue != "미선택" and selected_tongue in TONGUE_TYPES:
            tongue_info = TONGUE_TYPES[selected_tongue]
            system += "\n\n## 선택한 혀 타입 상세 정보\n"
            system += f"- 이름: {tongue_info['name']}\n"
            system += f"- 분석: {tongue_info['analysis']}\n"
            system += f"- 증상: {tongue_info['symptoms']}\n"
            system += f"- 경고: {tongue_info['warning']}\n"

        # 반박/우려 사항
        objections = context.get("objections") or []
        if objections:
            system += "\n\n## 현재 고객(원장)의 우려사항\n"
            for obj in objections:
                if obj == "skeptical":
                    system += "- 효과를 의심하고 있으므로, **데이터/사례 위주로** 짧게 설명하세요.\n"
                elif obj == "complexity":
                    system += "- 도입이 복잡할까 걱정하므로, **셋업 기간/절차를 단순하게** 설명하세요.\n"

        # 사례 추가
        case = CASE_STUDIES.get("hospital")
        if case and stage == "conversion":
            system += (
                "\n\n## 제시 가능한 실제 적용 사례\n"
                f"- {case['title']}: {case['result']}\n"
                f"- 정량 데이터: {case['data']}\n"
            )

        full_prompt = (
            f"{system}\n\n"
            "## 최근 대화 요약\n"
            f"{conversation_history}\n\n"
            "## 고객(원장)의 최신 발언\n"
            f"{user_input}\n\n"
            "### 지시사항\n"
            "- 2~6문장 안에서 **존댓말**로, 깔끔하고 직설적으로 답변하세요.\n"
            "- 기술 용어(LLM, 프롬프트, API 등)는 쓰지 말고, 비즈니스/진료 관점으로 설명하세요.\n"
            "- 과장된 표현보다, 현실적인 효과와 숫자를 사용하세요.\n"
        )
        return full_prompt

    # --------------------------------------------------
    # 3) 응답 후처리
    # --------------------------------------------------
    def _post_process_response(self, response: str, context: Dict) -> str:
        """응답 후처리: 길이/금지어/CTA 정리"""
        import re

        text = response.strip()

        # 줄바꿈 정리
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        # 길이 제한
        max_len = 800
        if len(text) > max_len:
            text = text[: max_len - 40].rstrip() + "\n\n(더 자세한 내용은 상담 시 안내드립니다.)"

        # 기술 용어 치환
        forbidden = {
            "LLM": "AI 시스템",
            "llm": "AI 시스템",
            "프롬프트": "질문 템플릿",
            "RAG": "AI 검색 기술",
            "API": "시스템 연동",
            "딥러닝": "AI 기술",
            "머신러닝": "AI 기술",
        }
        for k, v in forbidden.items():
            text = text.replace(k, v)

        return text

    # --------------------------------------------------
    # 4) Fallback 응답
    # --------------------------------------------------
    def _fallback_response(self, user_input: str, context: Dict) -> str:
        """Gemini 장애 시 사용하는 최소한의 안전 응답"""
        stage = context.get("stage", "initial")
        
        if stage == "symptom_select":
            return (
                "증상을 선택해주셔서 감사합니다.\n\n"
                "한의학에서는 혀를 보면 오장육부의 상태가 보입니다.\n"
                "거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해주세요."
            )
        
        elif stage == "tongue_select":
            return (
                "혀 상태를 확인했습니다.\n\n"
                "현재 몸 상태를 분석 중입니다. 잠시만 기다려주세요."
            )
        
        elif stage == "result_view":
            return (
                "건강 분석이 완료되었습니다.\n\n"
                "현재 상태를 개선하기 위해서는 전문적인 치료가 필요합니다.\n"
                "원장님께서 이 분석표를 미리 보시면 훨씬 정확한 처방이 가능합니다."
            )
        
        else:
            return (
                "시스템 응답 중 오류가 발생했습니다.\n"
                "계속 진행하시려면 다시 선택해주세요."
            )

    # --------------------------------------------------
    # 5) 외부에서 호출하는 메인 함수
    # --------------------------------------------------
    def generate_response(self, user_input: str, context: Dict, conversation_history: str) -> str:
        """Gemini 호출 + 재시도 + 후처리"""
        if not self.model:
            return self._fallback_response(user_input, context)

        last_error = None
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                prompt = self._build_prompt(user_input, context, conversation_history)
                response = self.model.generate_content(prompt)
                text = getattr(response, "text", "") or ""
                if not text.strip():
                    raise ValueError("빈 응답 수신")

                return self._post_process_response(text, context)
            except Exception as e:
                last_error = e
                try:
                    st.warning(f"AI 응답 재시도 중... ({attempt + 1}/{MAX_RETRY_ATTEMPTS})")
                except Exception:
                    pass
                time.sleep(1)

        # 모든 시도 실패 시
        try:
            st.error(f"⚠️ AI 응답 생성 실패: {last_error}")
        except Exception:
            pass
        return self._fallback_response(user_input, context)


# ==================================================
# 외부에서 쓰는 헬퍼
# ==================================================
def get_prompt_engine() -> PromptEngine:
    """세션 단위 싱글톤 엔진"""
    if "prompt_engine" not in st.session_state:
        st.session_state["prompt_engine"] = PromptEngine()
    return st.session_state["prompt_engine"]


def generate_ai_response(user_input: str, context: Dict, history: str) -> str:
    """app에서 바로 호출하는 헬퍼 함수"""
    engine = get_prompt_engine()
    return engine.generate_response(user_input, context, history)

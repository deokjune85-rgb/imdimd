import time
from typing import Dict

import streamlit as st
import google.generativeai as genai

from config import (
    SYSTEM_PROMPT,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
    CASE_STUDIES,
    MAX_RETRY_ATTEMPTS,
)


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
            # 스트림릿에서만 에러 표시, 모델은 None으로 둠
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
            "저는 24시간 잠들지 않는 **IMD AI 수석 실장**입니다.\n\n"
            "진료실에서 이런 말, 자주 들으시죠?\n\n"
            "> \"생각보다 비싸네요… 그냥 침만 맞을게요.\"\n\n"
            "그 순간, 진료 동선도 끊기고, 원장님 마음도 같이 꺾이실 겁니다.\n\n"
            "저는 그 **직전 단계에서**, 환자의 마음을 열고\n"
            "시술과 프로그램을 받아들일 준비를 시키는 역할을 합니다.\n\n"
            "백문이 불여일견입니다.\n"
            "지금부터 원장님은 잠시 **'만성 피로 환자' 역할**을 해봐 주십시오.\n"
            "편한 말투로 현재 상태를 한 줄만 말씀해 주세요."
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
        user_type = context.get("user_type") or "병원"
        pain_point = context.get("pain_point") or "conversion"
        stage = context.get("stage", "initial")
        trust_level = int(context.get("trust_level", 0) or 0)

        system = SYSTEM_PROMPT.format(
            user_type=user_type,
            pain_point=pain_point,
            stage=stage,
            trust_level=trust_level,
        )

        # 반박/우려 사항
        objections = context.get("objections") or []
        if objections:
            system += "\n\n## 현재 고객(원장)의 우려사항\n"
            for obj in objections:
                if obj == "skeptical":
                    system += "- 효과를 의심하고 있으므로, **데이터/사례 위주로** 짧게 설명하세요.\n"
                elif obj == "complexity":
                    system += "- 도입이 복잡할까 걱정하므로, **셋업 기간/절차를 단순하게** 설명하세요.\n"

        # 업종별 사례 추가 (병원 기본)
        case_key = user_type if user_type in CASE_STUDIES else "hospital"
        case = CASE_STUDIES.get(case_key)
        if case:
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
            "- 당신은 IMD 아키텍처 그룹의 수석 컨설턴트입니다.\n"
            "- 상대는 한의원/병원 원장입니다.\n"
            "- 2~6문장 안에서 **존댓말**로, 깔끔하고 직설적으로 답변하세요.\n"
            "- 기술 용어(LLM, 프롬프트, API 등)는 쓰지 말고, 비즈니스/진료 관점으로 설명하세요.\n"
            "- 과장된 표현보다, 현실적인 효과와 숫자를 사용하세요.\n"
            "- 한 번에 너무 많은 메뉴를 나열하지 말고, 다음에 무엇을 하면 좋을지 한 가지만 제안하세요.\n"
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

        # 신뢰도가 어느 정도 쌓였으면 자연스러운 CTA 한 줄 추가
        trust_level = int(context.get("trust_level", 0) or 0)
        stage = context.get("stage", "initial")
        if trust_level >= 40 and stage != "complete":
            if "연락처" not in text and "제안서" not in text:
                text += "\n\n원하시면, 간단한 병원 정보와 연락처를 남겨주시면 맞춤 설계안을 드리겠습니다."

        return text

    # --------------------------------------------------
    # 4) Fallback 응답
    # --------------------------------------------------
    def _fallback_response(self, user_input: str, context: Dict) -> str:
        """Gemini 장애 시 사용하는 최소한의 안전 응답"""
        lower = user_input.lower()

        # 가격/비용 관련
        if any(w in lower for w in ["가격", "비용", "얼마", "요금"]):
            return (
                "투자 금액보다 중요한 것은 **투자 회수 기간**입니다.\n\n"
                "현재 월 방문자 수와 상담/예약 전환율을 알려주시면,\n"
                "대략적인 투자 회수 기간과 기대 매출 증가 폭을 계산해 드릴 수 있습니다."
            )

        # 효과 의심
        if any(w in lower for w in ["효과", "진짜", "정말", "의심", "검증"]):
            case = CASE_STUDIES.get("hospital") or {}
            line1 = case.get("title", "서울 A한의원 도입 사례")
            line2 = case.get("result", "야간 문의 응답률 및 예약 전환율이 동시 상승")
            line3 = case.get("data", "온라인 문의 40% 증가, 예약 전환율 18% → 22.5%")
            return (
                "의심은 당연합니다. 그래서 저희도 **데이터로만** 말씀드립니다.\n\n"
                f"- {line1}\n- 결과: {line2}\n- 정량 데이터: {line3}\n\n"
                "원하시면, 원장님 병원 규모에 맞춘 예상 수치를 따로 뽑아 드리겠습니다."
            )

        # 시간 부족
        if any(w in lower for w in ["시간", "바쁘", "나중", "정리되면"]):
            return (
                "원장님 일정이 바쁘신 거 잘 알고 있습니다.\n\n"
                "핵심만 말씀드리면, 현재 놓치고 있는 온라인/전화 문의의 일부를\n"
                "AI가 대신 받아주면서, 원장님은 진료에만 집중하실 수 있게 만드는 구조입니다.\n\n"
                "잠깐 시간 되실 때 병원명과 연락처만 남겨주시면,\n"
                "요약된 자료만 먼저 보내드리겠습니다."
            )

        # 기본 응답
        return (
            "사업의 상황과 목표를 조금만 더 구체적으로 알고 싶습니다.\n\n"
            "예를 들어,\n"
            "- 현재 월 평균 신규 환자 수\n"
            "- 온라인/전화 문의 대비 실제 내원 비율\n"
            "- 가장 답답하게 느끼시는 지점 1가지\n\n"
            "이 세 가지만 알려주시면, 그 기준으로 구조를 잡아 드리겠습니다."
        )

    # --------------------------------------------------
    # 5) 외부에서 호출하는 메인 함수
    # --------------------------------------------------
    def generate_response(self, user_input: str, context: Dict, conversation_history: str) -> str:
        """Gemini 호출 + 재시도 + 후처리"""
        if not self.model:
            # 모델이 없는 경우 바로 Fallback
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

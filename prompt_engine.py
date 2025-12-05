import time
from typing import Dict

import streamlit as st
import google.generativeai as genai

# ------------------------------------------------------
# config.py 의 값이 있으면 가져오고, 없으면 기본값 사용
# ------------------------------------------------------
try:
    from config import SYSTEM_PROMPT as CONFIG_SYSTEM_PROMPT  # type: ignore
except Exception:
    CONFIG_SYSTEM_PROMPT = None

try:
    from config import CASE_STUDIES as CONFIG_CASE_STUDIES  # type: ignore
except Exception:
    CONFIG_CASE_STUDIES = None

try:
    from config import MAX_RETRY_ATTEMPTS as CONFIG_MAX_RETRY_ATTEMPTS  # type: ignore
except Exception:
    CONFIG_MAX_RETRY_ATTEMPTS = None


# 기본 SYSTEM_PROMPT (config에 있으면 그걸 우선 사용)
DEFAULT_SYSTEM_PROMPT = """
[IMD Strategic Consulting - B2B Sales Bot Core System Prompt]

당신의 역할:
- 당신은 'IMD 아키텍처 그룹(IMD Architecture Group)'의 수석 컨설턴트이자 AI 아키텍트입니다.
- 당신의 목표는, 한의원/병원 원장에게 'AI 상담 실장 시스템'의 가치를 이해시키고, 도입을 자연스럽게 제안하는 것입니다.
- 당신은 기술자가 아니라 '전략 컨설턴트'입니다. 대화의 중심은 기술 설명이 아니라, 비즈니스 구조·진료 흐름·매출 구조입니다.

대화 상대:
- 상대는 {user_type} 업종의 대표 또는 원장입니다. (예: 한의원, 의원, 병원, 클리닉 등)
- 온라인 마케팅이나 AI에 대해 잘 모를 수 있지만, 진료와 매출 구조에 대해서는 누구보다 잘 알고 있습니다.
- 본 대화의 궁극적인 목적은, 상대가 "이 AI를 우리 병원에 꼭 한 번 붙여봐야겠다"라고 생각하도록 만드는 것입니다.

핵심 배경 정보:
- 현재 고객(원장)의 주요 고민(pain point): {pain_point}
- 현재 상담 단계(stage): {stage}
- 현재 신뢰도(trust_level): {trust_level}/100

단계별 행동 지침:

1) 시뮬레이션 단계 (초기: 'initial', 'engaged')
- 이 단계에서 상대는 '원장님'이지만, 당신은 상대에게 **'만성 피로 환자 역할'**을 부탁하고 있습니다.
- 겉으로는 상대를 '환자분'으로 대하고, 실제 한의원 수석 실장/한의사처럼 상담해야 합니다.
- 절대 이 단계에서는 다음을 말하지 마세요:
  - "저희 AI", "챗봇", "홈페이지에 설치", "시스템", "IMD" 등
- 오직 다음에만 집중하세요:
  - 언제부터, 얼마나 자주, 어느 부위가, 어떤 패턴으로 힘든지 묻기
  - 수면 시간, 회복 여부, 업무 강도, 스트레스 등 '패턴 파악'
  - 공감 + 추가 질문 → 실제 진료실에서 쓰는 자연스러운 멘트

예시 톤:
- "요즘 계속 그렇게 피곤하시면 많이 힘드셨겠습니다."
- "언제부터 이런 피로감이 계속되셨는지 기억나세요?"
- "잠은 대략 몇 시간 정도 주무시나요? 자고 일어나도 개운한 느낌이 잘 안 드시나요?"

반드시 지킬 것:
- AI/시스템/설치/IMD/자동 상담 등은 완전히 입 밖에 꺼내지 않습니다.
- 답변은 3~6문장 정도, 마지막에 1~2개의 질문을 붙여서 대화를 이어갑니다.
- 이 단계에서는 '진짜 환자 상담'처럼 행동하는 것이 목적입니다.

2) 클로징 / 제안 단계 (stage가 'conversion'인 경우)
- 이제 역할극은 끝났고, 상대가 다시 '원장님 본인'이라는 전제로 전환합니다.
- 방금까지의 상담 흐름을 "이 AI가 실제 환자에게 대신 해줄 수 있는 일"로 풀어 설명합니다.
- 설명의 구조:
  1. 방금 상담에서 당신이 한 일을 요약 (패턴 파악 → 설명 → 제안 구조)
  2. 이 과정을, 병원 홈페이지·카카오채널·랜딩페이지에서 **24시간 자동으로 돌릴 수 있다**는 점을 설명
  3. 대표적인 지표(문의 수, 예약 전환율, 상담 부담 감소 등)를 구체적인 숫자로 예시
  4. "이 시스템을 병원에 붙였을 때"의 그림을 1~2가지 시나리오로 보여주기

- 표현 예시:
  - "방금 보신 상담 흐름이, 밤 11시에 홈페이지를 찾은 직장인에게 그대로 자동으로 실행된다고 보시면 됩니다."
  - "원장님은 진료에만 집중하시고, 이 AI 실장이 온라인에서 환자의 마음을 미리 열어두는 구조입니다."
  - "서울 A한의원 사례 기준으로, 온라인 문의 약 40% 증가, 예약 전환율 약 20~25% 상승 구간이 관측되었습니다."

- 이 단계에서 CTA(행동 유도)는 이렇게 정리합니다:
  - "병원명과 연락처만 남겨 주시면, 원장님 병원 규모에 맞는 예상 수치를 넣은 간단한 설계안을 보내드리겠습니다."
  - "도입 비용보다 '투자 회수 기간'이 중요하니, 현재 월 신규 환자·온라인 문의 수를 기준으로 시뮬레이션을 보여드리겠습니다."

3) 완료 단계 (stage가 'complete'인 경우)
- 견적/도입 문의 폼이 이미 제출된 상태입니다.
- 이 단계에서는 강한 세일즈 멘트를 줄이고, 다음에 할 일을 명확하게 정리합니다.
- 예시:
  - "요청해주신 정보는 접수되었고, 24시간 내에 담당 컨설턴트가 연락을 드릴 예정입니다."
  - "그 전에, 혹시 꼭 짚고 싶으신 조건(예: 지역 독점, 초기 비용 상한선)이 있다면 한 줄로만 더 남겨주셔도 좋습니다."
- 추가 CTA는 최대 한 줄만, 부드럽게 제안합니다.

응답 스타일 가이드 (항상 공통):

1. 톤 & 매너
- 존댓말, 담백한 컨설팅 톤
- 과장된 광고 멘트 금지 ("폭발적인", "압도적인", "무조건" 등 자제)
- 대신, "구조", "숫자", "예상 시뮬레이션" 같은 단어를 선호합니다.
- 원장의 시간을 존중하는 태도: 군더더기 없이 핵심만 말합니다.

2. 분량
- 기본: 2~6문장
- 시뮬레이션 단계에서는 질문 1~2개를 반드시 포함합니다.
- 클로징 단계에서는 구조 요약 + 숫자 예시 + 다음 액션(CTA)까지 담되, 너무 장황하지 않게 씁니다.

3. 금지/주의 표현
- 아래 용어는 사용하지 않거나, 간단한 말로 바꾸세요:
  - "LLM", "프롬프트", "RAG", "API", "딥러닝", "머신러닝"
- 대신 다음처럼 표현합니다:
  - "AI 시스템", "질문 템플릿", "AI 검색 기술", "시스템 연동", "AI 기술"

4. 대화의 방향성
- 항상 "이게 왜 원장님 병원에 의미 있는 구조인지"로 연결합니다.
- '채널(홈페이지/카카오)'보다 '구조(상담 흐름, 전환율, 회수 기간)'에 더 많은 비중을 둡니다.
- '도입 여부'를 강요하지 않고, '데이터 기반으로 같이 판단해보자'는 프레임을 유지합니다.

요약:
- stage가 'initial' 또는 'engaged'라면 → 철저히 "환자 상담 모드"
- stage가 'conversion'이면 → "방금 상담 흐름 = AI 실장이 대신 하는 일"을 설명하고, 도입을 제안
- stage가 'complete'이면 → 다음 절차 안내와 가벼운 마무리

이 지침을 절대적으로 우선하여, 현재 입력과 대화 내역을 바탕으로 가장 알맞은 한 번의 답변을 생성하세요.
"""

SYSTEM_PROMPT = CONFIG_SYSTEM_PROMPT or DEFAULT_SYSTEM_PROMPT

# 적용 사례 기본값 (config에 있으면 그걸 우선 사용)
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

# Gemini 모델 기본값
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TEMPERATURE = 0.6
GEMINI_MAX_TOKENS = 1024


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
            line2 = case.get("result", "야간 문의 응답률 및 예약 전환율 동시 상승")
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

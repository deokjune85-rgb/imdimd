"""
prompt_engine.py
IMD Strategic Consulting - AI Sales Bot (B2B)

- 상담 흐름용 LLM 엔진 (Advanced Logic)
- 한의학적 변증(Pattern Identification) 및 세일즈 빌드업 로직 탑재
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# Streamlit 및 Google GenAI 라이브러리 로드 (안전 처리)
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore


# ============================================
# 0. Gemini 설정 & API 키 로드
# ============================================
def _load_api_key() -> Optional[str]:
    key = None
    # 1) streamlit secrets
    if st is not None:
        try:
            key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            key = None
    # 2) 환경변수
    if not key:
        key = os.getenv("GEMINI_API_KEY")
    return key


GEMINI_API_KEY: Optional[str] = _load_api_key()
MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # 속도와 가성비 최적화

LLM_ENABLED: bool = GEMINI_API_KEY is not None and genai is not None
_MODEL: Optional["genai.GenerativeModel"] = None


def _init_model() -> Optional["genai.GenerativeModel"]:
    """Gemini 모델 Lazy 초기화"""
    global _MODEL
    if not LLM_ENABLED:
        return None
    if _MODEL is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(MODEL_NAME)
    return _MODEL


# ============================================
# 1. 고도화된 페르소나 및 상담 로직 정의
# ============================================

# 기본 페르소나: 15년 경력의 베테랑 상담 수석 실장 + 한의학적 지식
PERSONA_PROMPT = """
[Role]: 당신은 대한민국 상위 1% 한의원의 '수석 상담 실장'입니다.
[Target]: 당신의 대화 상대는 '원장님'이지만, 지금 이 순간만큼은 원장님이 '환자 역할'을 하고 있습니다.
[Goal]: 환자(원장)의 증상을 깊이 파고들어, 단순 침 치료가 아닌 '고가 비급여 프로그램(녹용/공진단/장기치료)'의 필요성을 스스로 느끼게 만드세요.

[Tone & Manner]:
1. **전문적 인과관계(Why) 설명**: 질문을 던질 때 반드시 '의학적 이유'를 붙이세요.
   - (X) "잠은 잘 주무세요?"
   - (O) "근육과 신경은 밤에 잘 때 회복됩니다. 특히 밤 11시~3시는 '간'이 피를 해독하는 시간인데, 이때 푹 주무시나요?"
2. **극도의 공감**: "아프시군요" (X) -> "저런, 아침마다 몸을 일으키기가 천근만근이셨겠어요." (O)
3. **확신에 찬 어조**: "~일 수도 있어요" 보다는 "~로 보입니다", "~한 상태가 의심됩니다" 사용.
"""

# 단계별 시나리오 지침 (Context-Aware Logic)
STAGE_INSTRUCTIONS = {
    # 1단계: 증상 탐색 (단순 피로 vs 병리적 피로 구분)
    "symptom_explore": """
    [현재 단계: 증상 구체화]
    - 환자가 호소하는 증상(피로/통증/쥐남 등)을 듣고, 그것이 '일시적인 것'이 아님을 확인하세요.
    - 질문 예시: "그 증상이 나타난 지 얼마나 되셨습니까?" 또는 "하루 중 언제가 가장 힘드십니까?"
    - 목적: 단순 휴식으로는 낫지 않는 '오래된 병'이라는 점을 환자 입으로 말하게 하세요.
    """,

    # 2단계: 수면/스트레스 (기허 vs 간울 확인)
    "sleep_check": """
    [현재 단계: 원인 추적 - 수면/회복력]
    - 앞서 환자가 말한 증상을 '수면 부족(충전 실패)'과 연결하세요.
    - 논리: "증상이 계속된다는 건, 밤새 우리 몸을 고쳐주는 '자가 치유력'이 떨어진 겁니다."
    - 질문: "주무시고 일어나면 개운하신가요? 아니면 자도 자도 배터리가 방전된 느낌이신가요?"
    """,

    # 3단계: 소화/식습관 (비위 기능 - 습담 확인)
    "digestion_check": """
    [현재 단계: 원인 추적 - 비위/소화기]
    - 한의학에서 비위(소화기)는 에너지를 만드는 공장(Factory)입니다.
    - 논리: "잠을 잘 자도 힘들다면, 에너지를 만드는 '위장'이 고장 난 것입니다. 먹은 게 피와 살이 안 되고 노폐물(습담)만 쌓이는 거죠."
    - 질문: "식사는 어떠세요? 입맛이 없거나, 먹고 나면 몸이 축 처지는 '식곤증'이 심하지 않으세요?"
    - **(중요)** 이 질문 후에는 반드시 **"말로만 들어서는 한계가 있습니다. 몸 내부를 눈으로 확인해봐야겠습니다. 거울을 보시고 혀 사진을 골라주시겠습니까?"**라고 유도하며 마무리하세요.
    """,
    
    # 4단계: 설진 후 분석 (UI에서 혀 선택 후 진입)
    "conversion": """
    [현재 단계: 위기감 조성 및 솔루션 제안]
    - 환자가 선택한 혀 상태와 앞선 증상들을 종합하여 '심각성'을 경고하세요.
    - 논리: "소화기가 약해서(원인) 에너지 생성이 안 되고(증상), 몸에 노폐물(습담)이 꼈습니다(혀 증거)."
    - 결론: "이건 쉬어서 낫는 단계가 아닙니다. 엔진 오일을 채워주는 '녹용'이나 순환을 돕는 '약침' 치료가 시급합니다."
    - 마지막 멘트: "원장님께 이 리포트를 보내고 우선 진료를 잡아드릴까요?"
    """
}


# ============================================
# 2. 프롬프트 조립 엔진
# ============================================

def _build_prompt(
    context: Dict[str, Any],
    history: List[Dict[str, Any]],
    user_input: str,
) -> str:
    """
    대화 맥락과 현재 단계에 맞춰 최적의 프롬프트를 조립합니다.
    """
    stage = context.get("stage", "symptom_explore")
    specific_instruction = STAGE_INSTRUCTIONS.get(stage, STAGE_INSTRUCTIONS["symptom_explore"])

    # 대화 기록 포맷팅 (최근 6턴만 참조)
    formatted_history = ""
    for msg in history[-6:]:
        role = "환자(원장)" if msg.get("role") == "user" else "AI상담실장"
        text = msg.get("content") or msg.get("text") or ""
        formatted_history += f"{role}: {text}\n"

    # 최종 프롬프트 합성
    full_prompt = f"""
{PERSONA_PROMPT}

[Current Situation]:
현재 상담 단계는 **{stage}** 입니다.
아래 지침에 따라 답변을 생성하세요:
{specific_instruction}

[Conversation History]:
{formatted_history}

[Patient's Last Input]:
"{user_input}"

[Instruction]:
1. 환자의 말에 **반드시 공감**하거나, 그 증상의 **의학적 의미를 해석**해주세요.
2. 질문은 한 번에 **하나만** 하세요. (취조하듯 하지 말 것)
3. 말투는 정중하면서도, 전문가로서의 권위가 느껴지게 하세요. (~하셨군요, ~로 보입니다)
4. 답변 길이는 모바일 가독성을 위해 **3~4문장**으로 작성하세요.
5. **(중요)** 답변 마지막에는 자연스럽게 다음 진단 질문을 던지세요.

AI 상담실장:
"""
    return full_prompt


# ============================================
# 3. Gemini 호출 함수
# ============================================

def _call_llm(
    context: Dict[str, Any],
    history: List[Dict[str, Any]],
    user_input: str,
) -> str:
    """Gemini API 호출 및 에러 핸들링"""
    if not LLM_ENABLED:
        # API 키 없을 때의 Fallback 시나리오 (데모용)
        stage = context.get("stage")
        if stage == "symptom_explore":
            return "저런, 많이 힘드셨겠습니다. 혹시 그 증상이 아침에 눈뜰 때 가장 심한가요, 아니면 오후 늦게 방전되듯 오나요?"
        elif stage == "sleep_check":
            return "그렇군요. 충전이 안 되는 느낌이시네요. 혹시 주무시는 건 어떠세요? 자다가 깨거나 꿈을 많이 꾸진 않으신가요?"
        elif stage == "digestion_check":
            return "잠도 문제지만, 에너지를 만드는 위장 기능도 의심됩니다. 식사 후에 속이 더부룩하거나 급격히 졸리진 않으세요? 이 질문 후 혀 상태를 확인해보겠습니다."
        else:
            return "상담이 완료되었습니다. 원장님께 리포트를 전송하겠습니다."

    model = _init_model()
    if model is None:
        return "시스템 오류: AI 모델 초기화 실패. 관리자에게 문의하세요."

    prompt = _build_prompt(context, history, user_input)

    try:
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6, # 조금 더 차분하고 일관성 있게
                "top_p": 0.9,
                "max_output_tokens": 500,
            }
        )
        
        if hasattr(resp, 'text'):
            return resp.text.strip()
        else:
            return "죄송합니다. 잠시 통신 상태가 좋지 않습니다. 다시 말씀해 주시겠습니까?"

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "네, 말씀하신 증상은 잘 기록했습니다. 다음으로, 평소 식사는 규칙적으로 하시는 편인가요?"


# ============================================
# 4. 외부 호출용 메인 함수 (자동 스테이지 전환)
# ============================================

def generate_ai_response(
    user_input: str,
    context: Dict[str, Any],
    history_for_llm: List[Dict[str, Any]],
) -> str:
    """
    app.py 에서 호출하는 단일 진입점
    """
    # 1. 혀 선택 등 특수 입력 처리 (프롬프트 오염 방지)
    if "[선택:" in user_input:
        user_input = f"(환자가 {user_input} 이미지를 선택했습니다. 이에 대한 분석 결과를 말해주세요.)"

    # 2. LLM 호출
    response = _call_llm(context, history_for_llm, user_input)
    
    # 3. 응답 후 자동 단계 전환 로직 (Workflow Engine)
    # AI가 답변을 했다는 것은 해당 단계의 질문을 던졌다는 의미이므로, 
    # 다음 턴을 위해 단계를 미리 넘겨둡니다. (Ping-Pong 유지)
    current_stage = context.get("stage", "symptom_explore")
    
    if current_stage == "symptom_explore":
        context["stage"] = "sleep_check"
    elif current_stage == "sleep_check":
        context["stage"] = "digestion_check"
    elif current_stage == "digestion_check":
        context["stage"] = "tongue_select" # 다음 턴엔 무조건 혀 사진 보자고 함

    return response


# ============================================
# 5. 유틸리티 (필요 시)
# ============================================
def get_prompt_engine() -> Dict[str, Any]:
    return {
        "llm_enabled": LLM_ENABLED,
        "model_name": MODEL_NAME
    }

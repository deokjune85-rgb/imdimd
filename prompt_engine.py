"""
prompt_engine.py
한의원 AI 실장 데모용 프롬프트 엔진

역할:
- app.py에서 넘겨준 context['stage']에 따라
  어떤 톤/내용으로 말할지 LLM에게 지시한다.
- 단계 진행은 여기서 "한 단계씩"만 진행한다.
  initial → symptom_explore → sleep_check → digestion_check → tongue_select → conversion → complete

중요 규칙:
- tongue_select 단계 이전에는 "혀", "설진", "혀 사진", "혀 상태" 같은 말 절대 금지.
- 욕/개소리는 app.py에서 stage를 막기 때문에,
  여기서는 그냥 부드럽게 받되, 단계는 한 칸씩만 전진한다고 생각하면 된다.
"""

from typing import Any, Dict, List
import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# ----------------------------------------
# 모델 설정
# ----------------------------------------
MODEL_NAME = "gemini-1.5-flash-latest"

_api_key = os.getenv("GOOGLE_API_KEY")
_model = None
if genai is not None and _api_key:
    try:
        genai.configure(api_key=_api_key)
        _model = genai.GenerativeModel(MODEL_NAME)
    except Exception:
        _model = None


def get_prompt_engine() -> Dict[str, Any]:
    """app.py에서 형식상 호출하는 함수 (확장 여지용)."""
    return {"model": _model, "name": MODEL_NAME}


# ----------------------------------------
# 스테이지별 시스템 인스트럭션
# ----------------------------------------
def _build_system_instruction(stage: str) -> str:
    """
    stage에 따라 LLM에게 역할과 금지사항을 명확히 전달한다.
    - tongue_select 이전에는 혀/사진/설진 언급 절대 금지.
    """
    base = """
당신은 '한의원 AI 수석 실장' 역할을 체험시키는 데모 봇입니다.
대화 상대는 실제 환자가 아니라 '한의원 원장님'이며, 원장님이 환자 역할을 연기하고 있습니다.

공통 규칙:
- 항상 존댓말.
- "원장님"이라고 부르며 예의를 갖춘 말투.
- 답변은 3~8줄 정도의 한국어 문단으로, 너무 짧지도 길지도 않게.
- 한 번에 한 단계의 질문만 진행한다. 여러 단계를 한 번에 몰아서 묻지 않는다.
- 마케팅/설명은 자연스럽게 섞되, 핵심은 "환자 공감 + 다음 질문"이다.
- 아래에 명시된 금지사항은 반드시 지킨다.
"""

    if stage == "initial":
        specific = """
[현재 단계: initial]

목표:
- 원장님이 던진 첫 증상/불편감을 공감해 주고,
- "어떤 점이 가장 힘든지", "언제 특히 힘든지" 정도를 한 번 더 물어본다.

지금 단계에서는:
- 혀, 설진, 사진, 이미지는 언급하지 않는다.
- 소화, 수면, 통증, 생활패턴 등 어떤 방향으로도 확장 가능하지만,
  지금은 "증상 스케치" 수준에서만 묻는다.
- 만성 피로/통증과 연관 있을 법한 질문 1~2개만 던진다.
"""

    elif stage == "symptom_explore":
        specific = """
[현재 단계: symptom_explore]

목표:
- 증상의 '양상'과 '패턴'을 조금 더 구체화한다.
  (언제부터, 어느 부위, 어떤 느낌, 무엇을 할 때 악화/완화되는지 등)

지금 단계에서는:
- 여전히 혀/설진/사진 이야기는 절대 꺼내지 않는다.
- "증상 이야기를 더 자세히 듣는" 데에 집중한다.
- 다음 단계가 수면(sleep_check)이라는 것을 염두에 두고,
  마지막 문장에서 자연스럽게 "잠은 어떠신지" 쪽으로 방향을 살짝 예고해도 된다.
"""

    elif stage == "sleep_check":
        specific = """
[현재 단계: sleep_check]

목표:
- 수면의 길이, 질, 패턴을 파악한다.
  (몇 시간 자는지, 잘 때/깰 때 어떤지, 자도 피로가 풀리는지 등)

지금 단계에서는:
- 혀/설진/사진 언급 금지.
- 수면이 증상과 어떻게 연관되는지 짧게 설명해 주고,
- 구체적인 수면 패턴에 대해 2~3개의 질문을 한다.
- 다음 단계는 소화(digestion_check)이므로,
  마지막에 "이 다음엔 소화/배 쪽도 같이 보겠다" 정도의 예고는 해도 좋다.
"""

    elif stage == "digestion_check":
        specific = """
[현재 단계: digestion_check]

목표:
- 소화 상태, 배변 패턴, 식후 컨디션 등을 확인한다.
  (소화불량, 더부룩함, 변비/설사, 식욕, 식후 피로감 등)

지금 단계에서는:
- 아직 혀/설진/사진 이야기를 꺼내지 않는다.
- 소화와 전신 피로/통증/컨디션의 연관성을 1~2줄 정도 설명해주고,
- 구체적인 소화/배변 관련 질문 2~3개를 던진다.
- 다음 단계는 혀 상태(tongue_select)라는 것을 염두에 두고,
  "이 다음에는 겉으로 보이는 신호(예: 혀 상태)를 통해 안쪽 장기를 교차 확인할 예정" 정도의 예고만 한다.
  **단, 여기서도 '혀 사진을 선택해 달라' 같은 직접 행동 지시는 하지 않는다.**
"""

    elif stage == "tongue_select":
        specific = """
[현재 단계: tongue_select]

목표:
- 이제서야 혀 상태(설진)를 꺼낸다.
- "거울을 보고 자신의 혀를 확인해보고, 화면의 혀 사진 중 가장 비슷한 것을 고르라"고 안내한다.
- 각 혀 타입이 어떤 의미인지 대략 설명하고, 환자가 '내 몸이 생각보다 안 좋구나'를 느끼도록 한다.

지금 단계에서는:
- 반드시 '혀', '혀 상태', '혀 사진', '거울을 보시고' 등의 표현을 사용해도 된다.
- 단, 구체적인 진단명/치료법을 확정 짓지 말고, "가능성이 크다/의심된다/체크가 필요하다" 정도의 톤으로.
- 마지막에는 "이제 이 데이터를 바탕으로 치료/한약/프로그램 제안까지 연결할 수 있다"는 정도까지 언급해도 좋다.
"""

    elif stage == "conversion":
        specific = """
[현재 단계: conversion]

목표:
- 지금까지의 상담 흐름을 원장님 입장에서 정리해주고,
- "이런 AI 실장을 원장님 한의원에 붙였을 때" 어떤 효과가 있는지 그림을 그려 준다.
- 자연스럽게 도입 의향/도입 문의로 이어지도록 한다.

지금 단계에서는:
- 더 이상 혀 사진 선택을 요구하지 않는다.
- 매출, 전환율, 야간 예약, 24시간 상담 등의 키워드를 적절히 활용해도 좋다.
- 다만 지나치게 과장된 광고 문구는 피하고, '실제 원장님 입장에서 현실감 있는 톤'을 유지한다.
"""

    else:  # complete 혹은 기타
        specific = """
[현재 단계: complete 또는 기타]

목표:
- 이미 상담/데모 흐름이 끝난 단계이므로,
- 원장님이 원하면 다시 처음부터 체험할 수 있다는 정도의 마무리 멘트를 한다.
- 새로운 의학적 상담을 깊게 시작하기보다는,
  "데모 종료" 내지 "다시 시작" 관점에서 가볍게 응대한다.
"""

    return base + "\n" + specific


# ----------------------------------------
# LLM 호출 유틸
# ----------------------------------------
def _call_llm(system_instruction: str, history: List[Dict[str, str]], user_input: str) -> str:
    """Gemini 호출. 실패 시 아주 단순한 fallback 문구."""
    # history: [{"role": "user"/"ai", "text": "..."}]

    if _model is None:
        # API 없을 때 간단 fallback
        return (
            "원장님 말씀 이해했습니다. 이 환경에서는 실제 AI 모델 호출이 제한되어 있어 "
            "아주 단순하게만 응답드릴 수 있습니다. 증상에 대해 조금만 더 구체적으로 "
            "설명해 주시면, 그에 맞춰 다음 질문을 이어가겠습니다."
        )

    msgs = [
        {"role": "system", "parts": [system_instruction]},
    ]

    for msg in history:
        role = msg.get("role", "ai")
        text = msg.get("text", "")
        if not text:
            continue
        g_role = "user" if role == "user" else "assistant"
        msgs.append({"role": g_role, "parts": [text]})

    # 마지막 턴 사용자 발화
    msgs.append({"role": "user", "parts": [user_input]})

    try:
        res = _model.generate_content(msgs)
        text = (res.text or "").strip()
        if not text:
            raise ValueError("empty response")
        return text
    except Exception:
        return (
            "원장님 말씀 잘 들었습니다. 이 단계에서는 증상을 조금 더 구체적으로 듣고, "
            "수면/소화/생활 패턴을 차근차근 확인하는 역할을 합니다. "
            "조금만 더 자세히 말씀해 주시면, 그에 맞춰 다음 질문을 드리겠습니다."
        )


# ----------------------------------------
# 스테이지 전이 로직
# ----------------------------------------
def _get_next_stage(current_stage: str) -> str:
    """한 번에 한 단계씩만 전진하도록 강제."""
    flow = [
        "initial",
        "symptom_explore",
        "sleep_check",
        "digestion_check",
        "tongue_select",
        "conversion",
        "complete",
    ]

    if current_stage not in flow:
        return "symptom_explore"

    idx = flow.index(current_stage)
    if idx < len(flow) - 1:
        return flow[idx + 1]
    return current_stage


# ----------------------------------------
# 메인 엔트리
# ----------------------------------------
def generate_ai_response(
    user_input: str,
    context: Dict[str, Any],
    history_for_llm: List[Dict[str, str]],
) -> str:
    """
    app.py에서 호출하는 함수.

    - context["stage"]를 읽어서 system prompt를 만든다.
    - LLM을 호출해서 답변 텍스트를 받는다.
    - 다음 단계(next_stage)를 '한 단계만' 전진시켜 [[STAGE:...]] 태그로 붙인다.
    """
    current_stage = context.get("stage", "initial")
    system_instruction = _build_system_instruction(current_stage)

    llm_text = _call_llm(system_instruction, history_for_llm, user_input)

    # 다음 단계는 무조건 한 칸만 전진
    next_stage = _get_next_stage(current_stage)

    # app.py에서 [[STAGE:...]]를 파싱해서 stage를 업데이트한다
    return f"{llm_text}\n\n[[STAGE:{next_stage}]]"

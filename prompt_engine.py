# prompt_engine.py
"""
한의원 AI 실장 전용 프롬프트 엔진

역할:
- app.py에서 넘겨준 context['stage']에 따라
  각 단계별로 '무슨 톤으로 / 무엇을 물어볼지'를 LLM에게 지시한다.
- 마지막 줄에 [[STAGE:...]] 태그를 붙여서, 다음 단계만 app.py에 알려준다.

플로우:
initial → symptom_explore → sleep_check → digestion_check → tongue_select → conversion → complete
"""

from typing import Any
import streamlit as st

# ============================================
# 0. 모델 준비 (Gemini 사용, 없으면 폴백)
# ============================================
try:
    import google.generativeai as genai

    try:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=API_KEY)
        _MODEL = genai.GenerativeModel("gemini-1.5-flash-latest")
    except Exception:
        _MODEL = None
except Exception:
    genai = None
    _MODEL = None


def get_prompt_engine() -> Any:
    """app.py와 인터페이스 맞추기용. 필요하면 여기서 모델 핸들 꺼내 쓸 수 있음."""
    return _MODEL


# ============================================
# 1. 단계별 기본 폴백 멘트
# ============================================
def _fallback_response(user_input: str, stage: str) -> str:
    """모델이 없거나 에러났을 때 최소한의 기본 멘트."""
    if stage == "initial":
        return (
            "말씀만 들어도 요즘 많이 지치고 불편하셨던 게 느껴집니다.\n\n"
            "어느 부위가, 언제부터, 어떤 상황에서 가장 힘드신지\n"
            "편하게 한 번만 더 말씀해 주실 수 있을까요?"
        )
    elif stage == "symptom_explore":
        return (
            "지금 설명해 주신 증상을 보니, 단순히 하루 이틀의 피곤함은 아닌 것 같습니다.\n\n"
            "이번에는 하루 중 언제 증상이 더 심해지는지,\n"
            "특정 자세나 상황에서 더 악화되는 순간이 있는지도 함께 알려주시면 좋겠습니다."
        )
    elif stage == "sleep_check":
        return (
            "이제 수면 상태를 한 번 같이 보겠습니다.\n\n"
            "평균적으로 몇 시쯤 잠자리에 드시고, 몇 시간 정도 주무시는지,\n"
            "자고 일어나도 개운하지 않은 날이 더 많은지도 알려주세요."
        )
    elif stage == "digestion_check":
        return (
            "이제 소화 쪽을 체크해보겠습니다.\n\n"
            "식사 후에 속이 더부룩하거나 답답한 느낌이 자주 있으신지,\n"
            "대변은 규칙적인 편인지도 함께 알려주세요."
        )
    elif stage == "tongue_select":
        return (
            "지금까지의 증상, 수면, 소화 패턴을 보면 몸 안쪽의 에너지 공장이 많이 지친 상태일 수 있습니다.\n\n"
            "겉으로 보이는 혀 상태를 보면 안쪽 장기의 상태를 조금 더 정확하게 볼 수 있습니다.\n"
            "거울을 보시고 혀를 한 번 살펴보신 뒤, 화면에 보이는 혀 사진 중 가장 비슷한 것을 선택해 주세요."
        )
    elif stage == "conversion":
        return (
            "지금까지 정리해보면, 스스로 버티기에는 꽤 부담이 쌓여 있는 상태로 보입니다.\n\n"
            "한약과 치료를 통해 체계적으로 관리해 주면, 몸이 회복되는 속도 자체를 바꿀 수 있습니다.\n"
            "원하시면 원장님과 상의해서 보다 구체적인 치료 방향과 계획을 잡아볼 수 있도록 도와드리겠습니다."
        )
    else:  # complete 포함
        return (
            "오늘 이야기 나눠주셔서 감사합니다.\n\n"
            "언제든지 몸 상태가 걱정되실 때는 이렇게 편하게 말씀만 해 주세요.\n"
            "필요하시면 다시 한 번 지금까지의 내용을 정리해서 설명도 도와드리겠습니다."
        )


# 단계별 기본 다음 단계 맵
_NEXT_STAGE_MAP = {
    "initial": "symptom_explore",
    "symptom_explore": "sleep_check",
    "sleep_check": "digestion_check",
    "digestion_check": "tongue_select",
    "tongue_select": "conversion",   # 실제 전환은 app.py에서 혀 선택 후 conversion으로 이동
    "conversion": "complete",
    "complete": "complete",
}


# ============================================
# 2. 메인 함수: generate_ai_response
# ============================================
def generate_ai_response(user_input: str, context: dict, history: str) -> str:
    """
    app.py에서:
        raw_output = generate_ai_response(user_input, context, history_for_llm)

    출력 형식 (반드시):
        (환자에게 보여줄 상담 멘트)

        [[STAGE:다음단계]]

    가능한 단계:
        - initial
        - symptom_explore
        - sleep_check
        - digestion_check
        - tongue_select
        - conversion
        - complete
    """
    stage = context.get("stage", "initial")

    # ----------------------------------------
    # 2-1. 단계별 역할 설명
    # ----------------------------------------
    stage_guidance = {
        "initial": """
- 환자가 처음 증상을 이야기하는 단계입니다.
- 해야 할 일:
  * 따뜻하게 공감해 줍니다.
  * '언제부터 / 어느 부위 / 어떤 상황에서' 불편한지 가볍게 1~3개 정도 질문합니다.
- 하지 말 것:
  * 혀 / 거울 / 사진 / 백태 / 설진 같은 단어를 꺼내지 않습니다.
  * 치료 비용, 패키지, 시술 설명 등은 언급하지 않습니다.
- 다음 단계:
  * [[STAGE:symptom_explore]] 로 진행합니다.
""",
        "symptom_explore": """
- 주 증상을 조금 더 구체화하는 단계입니다.
- 해야 할 일:
  * 환자가 말한 부위와 상황을 바탕으로 2~3개의 추가 질문을 던집니다.
    예: 어떤 동작에서 더 심해지는지, 하루 중 언제가 더 힘든지 등.
  * 지금까지 들은 내용을 짧게 정리해 주며 '혼자 참은 시간이 길었겠다'는 공감을 표현합니다.
- 하지 말 것:
  * 아직 혀 / 거울 / 사진 / 설진 언급 금지.
  * 치료 세부 계획, 약 이름, 비용 이야기를 꺼내지 않습니다.
- 다음 단계:
  * [[STAGE:sleep_check]] 로 진행합니다.
""",
        "sleep_check": """
- 수면 상태를 집중적으로 확인하는 단계입니다.
- 해야 할 일:
  * 총 수면 시간, 잠드는 데 걸리는 시간, 자다가 깨는지 등을 2~3개 질문합니다.
  * 수면과 현재 증상의 연관성을 부드럽게 설명해 줍니다.
- 하지 말 것:
  * 여전히 혀 / 거울 / 설진 언급 금지.
  * 너무 단정적으로 '그래서 이 병이다'라고 말하지 않습니다.
- 다음 단계:
  * [[STAGE:digestion_check]] 로 진행합니다.
""",
        "digestion_check": """
- 소화와 대변 패턴만 확인하는 단계입니다.
- 해야 할 일:
  * 식사 후 더부룩함, 트림, 명치 답답함, 변비/설사 여부 등을 2~3개 질문합니다.
  * '먹은 것을 에너지로 바꾸는 공장(비위)이 얼마나 잘 돌아가고 있는지'를 쉽게 풀어 설명해 줍니다.
- 하지 말 것:
  * 이 단계에서는 혀 / 거울 / 사진 / 설진 같은 단어를 절대 꺼내지 않습니다.
  * 혀 상태를 보자는 말도 하지 않습니다. 그건 다음 단계의 몫입니다.
- 다음 단계:
  * [[STAGE:tongue_select]] 로 진행합니다.
""",
        "tongue_select": """
- 이 단계에서 처음으로 혀 / 거울 / 설진 이야기를 꺼냅니다.
- 해야 할 일:
  * 지금까지 나온 증상, 수면, 소화 패턴을 한두 문장으로 정리해 줍니다.
  * '겉으로 보이는 혀 상태를 보면 안쪽 장기의 상태를 더 정확하게 볼 수 있다'는 점을 설명합니다.
  * 환자에게 이렇게 안내합니다:
    - 거울을 보시고 본인의 혀를 한 번 살펴보시라고 합니다.
    - 화면에 보이는 혀 사진 4개 중에서 가장 비슷한 것을 하나 골라달라고 안내합니다.
- 하지 말 것:
  * 여기서 새로 소화/수면을 다시 캐묻지 않습니다.
  * 과도한 공포 조장은 하지 않습니다. (예: 큰 병일 수 있다 식으로 단정 금지)
- 다음 단계:
  * 일반적으로 [[STAGE:tongue_select]] 를 유지하거나,
    짧게 혀 선택이 어려울 때의 팁을 한 번 더 안내해 줄 수 있습니다.
  * 실제로 conversion 단계로 넘어가는 것은 app.py에서 혀를 선택했을 때 처리합니다.
""",
        "conversion": """
- 혀 선택 후, 지금까지 정보를 바탕으로 치료 필요성을 정리하는 단계입니다.
- 해야 할 일:
  * 증상 / 수면 / 소화 / 혀 상태(요약)를 연결해서 설명해 줍니다.
  * '이 정도면 한 번 제대로 체계적으로 관리해 보는 것이 좋다'는 메시지를 전합니다.
  * '원장님과 상의해 한약이나 치료 계획을 세우면, 어느 지점을 목표로 회복을 도와드릴지'를 이야기합니다.
  * 부담스럽지 않게, '필요하시면 예약이나 상담을 도와드릴 수 있다'는 톤으로 마무리합니다.
- 하지 말 것:
  * 가격, 횟수, 구체적 패키지 등은 여기서 직접 언급하지 않습니다.
- 다음 단계:
  * 보통 [[STAGE:complete]] 로 마무리합니다.
""",
        "complete": """
- 견적/예약 접수까지 끝난 상태로 가정하는 단계입니다.
- 해야 할 일:
  * 감사 인사를 전하고, '궁금한 점 생기면 언제든지 편하게 물어보라'고 안내합니다.
  * 필요하면 생활 관리나 간단한 주의사항 한두 가지 정도를 덧붙일 수 있습니다.
- 다음 단계:
  * [[STAGE:complete]] 로 유지합니다.
""",
    }

    stage_text = stage_guidance.get(stage, stage_guidance["initial"])

    # ----------------------------------------
    # 2-2. 시스템 프롬프트 구성
    # ----------------------------------------
    system_prompt = f"""
너는 한의원 'AI 수석 실장'이다.

목표:
- 환자의 말을 잘 받아주고 공감하면서,
- 원장님이 보기 좋게 정보가 정리되도록 단계별로 질문을 이어간다.
- 말투는 실제 한의원 카운터에 있는 실장이 사용하는 자연스러운 존댓말 한국어여야 한다.

절대 규칙:
- 환자가 어떤 말을 하더라도, 지금 '단계(stage)'에 맞는 질문과 설명만 한다.
- 아직 오지 않은 단계의 내용을 미리 땡겨서 말하지 않는다.
  (예: stage가 initial이나 symptom_explore일 때 혀/거울/설진을 꺼내지 말 것)
- 한 번의 응답에서 1~3개 정도의 질문만 던지고, 나머지는 공감과 정리 위주로 말한다.
- 리스트를 쓰더라도 너무 교과서처럼 딱딱하지 않게, 실제 상담 대화처럼 작성한다.
- 의학적 확진, 위험한 경고, 무조건적인 단정은 피하고,
  '가능성이 높아 보인다', '점검이 필요해 보인다' 식으로 완곡하게 말한다.

현재 단계(stage):
{stage}

현재 단계에서의 역할/주의사항:
{stage_text}

대화 히스토리(요약 또는 포맷된 문자열):
{history}

마지막 환자 발화:
{user_input}

출력 형식:
1) 먼저 환자에게 보여줄 상담 멘트를 자연스럽게 작성한다.
2) 줄바꿈 두 번 뒤, 마지막 줄에 정확히 다음 형식으로만 stage를 쓴다:

   [[STAGE:다음단계]]

예시 출력 (형식만 참고):

"요즘 어깨 때문에 많이 힘드셨겠어요. 잠깐만 들어도 그동안 혼자 버티고 계셨던 게 느껴집니다.

혹시 통증이 제일 심해지는 시간이 따로 있으실까요?
예를 들면, 아침에 일어날 때가 더 뻐근한지, 아니면 하루 일과 끝나고 저녁이 더 힘드신지 궁금합니다.

[[STAGE:symptom_explore]]"
"""

    # ----------------------------------------
    # 2-3. 모델이 없을 때: 안전 폴백
    # ----------------------------------------
    if _MODEL is None:
        base = _fallback_response(user_input, stage)
        next_stage = _NEXT_STAGE_MAP.get(stage, "symptom_explore")
        return f"{base}\n\n[[STAGE:{next_stage}]]"

    # ----------------------------------------
    # 2-4. LLM 호출
    # ----------------------------------------
    try:
        response = _MODEL.generate_content(
            [
                {"role": "system", "parts": [system_prompt]},
                # history는 system_prompt 안에 녹였으므로, 여기서는 마지막 발화만 user로 준다
                {"role": "user", "parts": [user_input]},
            ]
        )
        text = (response.text or "").strip()
    except Exception:
        base = _fallback_response(user_input, stage)
        next_stage = _NEXT_STAGE_MAP.get(stage, "symptom_explore")
        return f"{base}\n\n[[STAGE:{next_stage}]]"

    # ----------------------------------------
    # 2-5. 혹시 태그를 안 붙였으면 강제로 붙여주기
    # ----------------------------------------
    if "[[STAGE:" not in text:
        next_stage = _NEXT_STAGE_MAP.get(stage, "symptom_explore")
        text = text + f"\n\n[[STAGE:{next_stage}]]"

    return text

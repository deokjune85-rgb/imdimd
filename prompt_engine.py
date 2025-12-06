# prompt_engine.py
"""
한의원 AI 실장 전용 프롬프트 엔진

역할:
- app.py에서 넘겨준 context['stage']에 따라
  각 단계별로 '무슨 톤으로 / 무엇을 물어볼지'를 LLM에게 지시한다.
- 마지막 줄에 [[STAGE:...]] 태그를 붙여서, 다음 단계만 app.py에 알려준다.
"""

from typing import Any
import streamlit as st

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
    """지금은 모델 핸들 자체는 안 쓰지만, 인터페이스 맞추기용."""
    return _MODEL


def _fallback_response(user_input: str, stage: str) -> str:
    """모델이 없을 때 최소한의 안전용 답변."""
    if stage == "symptom_explore":
        return (
            "요즘 많이 힘드셨겠네요.\n\n"
            "어느 쪽이, 언제부터, 어떤 느낌으로 불편하신지\n"
            "조금만 더 구체적으로 이야기해 주실 수 있을까요?"
        )
    elif stage == "sleep_check":
        return (
            "수면 상태를 한 번 같이 볼까요?\n\n"
            "평균적으로 몇 시쯤 잠자리에 드시고,\n"
            "몇 시간 정도 주무시는지 알려주시면 좋겠습니다."
        )
    elif stage == "digestion_check":
        return (
            "이제 소화 쪽을 체크해보겠습니다.\n\n"
            "식사 후에 속이 더부룩하거나 답답한 느낌이 자주 있으신가요?\n"
            "대변은 규칙적인 편인지도 함께 알려주세요."
        )
    else:
        return (
            "말씀만 들어도 요즘 많이 지치셨던 게 느껴집니다.\n\n"
            "어떤 상황에서 증상이 특히 심해지는지\n"
            "조금만 더 자세히 이야기해 주시면, 단계별로 정리해 드리겠습니다."
        )


def generate_ai_response(user_input: str, context: dict, history: str) -> str:
    """
    app.py에서:
        raw_output = generate_ai_response(user_input, context, history_for_llm)
    이렇게 호출됨.

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

    # ------------------------------------
    # 1. 단계별 역할 설명
    # ------------------------------------
    stage_guidance = {
        "initial": """
- 환자가 처음 증상을 이야기하는 단계.
- 해야 할 일:
  * 따뜻하게 공감해준다.
  * '언제부터 / 어느 부위 / 어떤 느낌' 정도만 간단히 묻는다.
- 하지 말 것:
  * 혀 / 거울 / 사진 / 백태 / 설진 같은 단어를 꺼내지 않는다.
  * 한 번에 너무 많은 질문을 쏟아내지 않는다.
- 다음 단계:
  * [[STAGE:symptom_explore]] 로 진행한다.
""",
        "symptom_explore": """
- 주 증상을 조금 더 구체화하는 단계.
- 해야 할 일:
  * 환자가 말한 부위와 상황을 바탕으로, 2~3개의 추가 질문을 던진다.
  * 평소 패턴(시간대, 계절, 특정 동작 등)을 물어본다.
- 하지 말 것:
  * 아직 혀 / 거울 / 사진 언급 금지.
  * 한약치료, 비용, 패키지 같은 판매 멘트는 쓰지 않는다.
- 다음 단계:
  * [[STAGE:sleep_check]] 로 진행한다.
""",
        "sleep_check": """
- 수면 상태만 집중해서 확인하는 단계.
- 해야 할 일:
  * 총 수면 시간, 잠드는 데 걸리는 시간, 자주 깨는지 등을 2~3개 질문한다.
  * 증상과 수면의 연관성을 부드럽게 짚어준다.
- 하지 말 것:
  * 아직 혀 / 거울 / 사진 언급 금지.
- 다음 단계:
  * [[STAGE:digestion_check]] 로 진행한다.
""",
        "digestion_check": """
- 소화와 대변 패턴을 확인하는 단계.
- 해야 할 일:
  * 식후 더부룩함, 트림, 명치 답답함, 변비/설사 등을 2~3개 질문한다.
  * '몸이 에너지를 만드는 공장(비위)이 제대로 돌고 있는지'를 설명해준다.
  * 마지막 부분에서 처음으로 '혀 상태를 보면 안에 있는 장기 상태를 더 정확히 볼 수 있다'는 말을 꺼내고,
    거울을 보고 혀 사진 중 하나를 고르게 유도한다.
- 반드시 할 것:
  * 답변의 마지막 줄에는 [[STAGE:tongue_select]] 를 쓴다.
""",
        "tongue_select": """
- 혀 종류 선택은 화면 UI에서 처리되므로, 이 단계에서는 LLM이 별도 안내를 많이 할 필요는 없다.
- 일반적으로 이 단계에서 generate_ai_response는 거의 호출되지 않거나,
  '혓바닥 사진 선택이 어려우시면, 가장 비슷한 느낌의 것을 골라주셔도 된다' 정도의 짧은 안내 정도만 한다.
- 다음 단계:
  * 혀를 선택하면 app.py에서 conversion 단계로 이동한다.
""",
        "conversion": """
- 혀 진단과 지금까지의 정보를 바탕으로, 치료 필요성을 정리하고 한의원 내원/치료 동기를 높이는 단계.
- 해야 할 일:
  * 지금까지 나온 정보들을 한두 문단으로 정리한다.
  * '이 정도면 한약/치료를 통해 체계적으로 관리하는 것이 좋다'는 메시지를 준다.
  * 부담스럽지 않게, '필요하면 예약을 도와드릴 수 있다' 정도로 자연스럽게 마무리한다.
- 다음 단계:
  * [[STAGE:complete]] 또는 여전히 상담을 이어가고 싶다면 [[STAGE:conversion]] 유지.
""",
        "complete": """
- 견적/예약 접수까지 끝난 상태.
- 해야 할 일:
  * 감사 인사와 함께, 궁금한 점이 있으면 언제든지 물어보라고 안내한다.
- 다음 단계:
  * [[STAGE:complete]] 로 유지.
""",
    }

    stage_text = stage_guidance.get(stage, stage_guidance["initial"])

    # ------------------------------------
    # 2. 시스템 프롬프트 구성
    # ------------------------------------
    system_prompt = f"""
너는 한의원 'AI 수석 실장'이다.

목표:
- 환자의 말을 잘 받아주고, 공감하면서도
- 단계별로 정보를 구조화해서 원장님의 진료와 한약 처방이 쉬워지게 돕는다.
- 말투는 부드러운 존댓말, 실제 한의원 카운터에서 자주 쓰는 자연스러운 한국어여야 한다.

절대 규칙:
- 환자가 어떤 말을 하더라도, 지금 '단계(stage)'에 맞는 질문과 설명만 한다.
- 아직 오지 않은 단계의 내용을 미리 땡겨서 말하지 않는다.
  (예: stage가 initial이나 symptom_explore일 때 혀 / 거울 / 설진을 꺼내지 말 것)
- 한 번의 응답에서 1~3개 정도의 질문만 던지고, 나머지는 공감과 정리 위주로 말한다.
- 리스트를 쓰더라도, 너무 교과서처럼 딱딱하지 않게 쓴다.
- **의학적 확진, 위험한 경고, 무조건적인 단정**은 피하고, '가능성이 높아 보인다', '점검이 필요해 보인다' 식으로 완곡하게 말한다.

현재 단계(stage):
{stage}

현재 단계에서의 역할/주의사항:
{stage_text}

대화 히스토리(요약 형태):
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

    # ------------------------------------
    # 3. 모델이 없을 때: 안전한 폴백
    # ------------------------------------
    if _MODEL is None:
        base = _fallback_response(user_input, stage)
        # 폴백에서도 최소한 다음 단계 태그는 달아 준다
        next_stage = {
            "initial": "symptom_explore",
            "symptom_explore": "sleep_check",
            "sleep_check": "digestion_check",
            "digestion_check": "tongue_select",
            "tongue_select": "conversion",
            "conversion": "complete",
            "complete": "complete",
        }.get(stage, "symptom_explore")
        return f"{base}\n\n[[STAGE:{next_stage}]]"

    # ------------------------------------
    # 4. LLM 호출
    # ------------------------------------
    try:
        response = _MODEL.generate_content(
            [
                {"role": "system", "parts": [system_prompt]},
                # history는 system_prompt에 이미 녹였으므로, 여기서는 마지막 발화만 user로 준다
                {"role": "user", "parts": [user_input]},
            ]
        )
        text = response.text or ""
    except Exception:
        # 에러 시에도 폴백
        base = _fallback_response(user_input, stage)
        next_stage = {
            "initial": "symptom_explore",
            "symptom_explore": "sleep_check",
            "sleep_check": "digestion_check",
            "digestion_check": "tongue_select",
            "tongue_select": "conversion",
            "conversion": "complete",
            "complete": "complete",
        }.get(stage, "symptom_explore")
        return f"{base}\n\n[[STAGE:{next_stage}]]"

    # 혹시 모델이 태그를 깜빡했을 경우를 대비해서, 최소한 기본 단계는 달아준다
    if "[[STAGE:" not in text:
        next_stage = {
            "initial": "symptom_explore",
            "symptom_explore": "sleep_check",
            "sleep_check": "digestion_check",
            "digestion_check": "tongue_select",
            "tongue_select": "conversion",
            "conversion": "complete",
            "complete": "complete",
        }.get(stage, "symptom_explore")
        text = text.strip() + f"\n\n[[STAGE:{next_stage}]]"

    return text

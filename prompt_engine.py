"""
prompt_engine.py
한의원 AI 실장 데모용 프롬프트 엔진 (GEMINI_API_KEY + Gemini 2.0 Flash)

역할:
- app.py에서 넘겨준 context['stage']에 따라
  어떤 톤/내용으로 말할지 LLM에게 지시한다.
- 제미나이가 정상 동작할 때는 LLM 사용.
- 제미나이가 429/오류 나면 자동으로 "룰 기반 오프라인 모드"로 떨어져서
  원장님 눈에는 끊기지 않는 상담처럼 보이게 한다.

허용 단계:
- initial
- symptom_explore
- sleep_check
- digestion_check
- tongue_select
- conversion
- complete
"""

from typing import Any, Dict, List
import os

import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# -----------------------------
# 전역 상태
# -----------------------------
MODEL_NAME: str = "gemini-2.0-flash"

_api_key_source: str = "none"
_init_error: str = ""
_model = None


# -----------------------------
# API 키 로딩 (GEMINI_API_KEY)
# -----------------------------
def _load_api_key() -> str:
    """GEMINI_API_KEY 를 st.secrets 또는 환경변수에서 찾는다."""
    global _api_key_source

    # 1) Streamlit secrets
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            _api_key_source = "st.secrets['GEMINI_API_KEY']"
            return key
    except Exception:
        pass

    # 2) 환경 변수
    key = os.getenv("GEMINI_API_KEY")
    if key:
        _api_key_source = "os.environ['GEMINI_API_KEY']"
        return key

    _api_key_source = "none"
    return ""


# -----------------------------
# 모델 초기화
# -----------------------------
_api_key = _load_api_key()

if genai is not None and _api_key:
    try:
        genai.configure(api_key=_api_key)
        _model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        _model = None
        _init_error = f"{type(e).__name__}: {str(e)}"
elif genai is None:
    _init_error = "ImportError: google-generativeai 미설치 또는 로딩 실패"
elif not _api_key:
    _init_error = "GEMINI_API_KEY를 secrets/env에서 찾지 못함"


def get_prompt_engine() -> Dict[str, Any]:
    """상태 확인용 (app.py에서 디버깅용으로 쓸 수 있음)."""
    return {
        "model": _model,
        "name": MODEL_NAME,
        "api_key_source": _api_key_source,
        "init_error": _init_error,
        "has_genai": genai is not None,
    }


# -----------------------------
# (참고용) 스테이지별 시스템 설명 텍스트
#  - 지금은 LLM prompt에도 쓰고,
#  - 오프라인 모드에서는 참고용 설명 역할만 한다.
# -----------------------------
def _build_system_instruction(stage: str) -> str:
    base = """
당신은 '한의원 AI 수석 실장' 역할을 체험시키는 데모 봇입니다.
대화 상대는 실제 환자가 아니라 '한의원 원장님'이며, 원장님이 환자 역할을 연기하고 있습니다.

공통 규칙:
- 항상 존댓말을 사용하세요.
- 상대를 "원장님"이라고 부르며, 예의 바른 톤을 유지하세요.
- 답변은 한국어로 3~8줄 정도의 문단으로 작성하세요. (너무 짧게 한 줄 금지)
- 한 번에 한 단계에 해당하는 내용만 다루고, 질문은 1~3개 정도만 하세요.
- "환자의 감정 공감" → "현재 단계에 맞는 질문" 흐름을 지키세요.
- 욕설, 장난, 의미 없는 입력도 나올 수 있습니다. 그런 경우에도 침착하게 대응하세요.

단계 전환 규칙(매우 중요):
- 단계 이름: initial, symptom_explore, sleep_check, digestion_check, tongue_select, conversion, complete
- 당신은 각 답변의 마지막 줄에 반드시 [[STAGE:...]] 형식의 태그를 넣어야 합니다.
- 사용자가 욕설/장난/의학과 무관한 말을 했다고 판단되면,
  현재 단계를 유지하고 [[STAGE:현재단계]]로 끝내세요.
- 사용자가 현재 단계의 질문에 '의미 있는 의학적 정보'로 답했다고 판단될 때만
  다음 단계로 진행하세요.
- tongue_select 이전 단계에서는 혀/설진/혀 사진/이미지 같은 단어를 절대 꺼내지 마세요.
"""

    if stage == "initial":
        specific = """
[현재 단계: initial]

목표:
- 원장님이 환자 역할로 던진 첫 증상/불편감에 공감해 줍니다.
- "어떤 점이 가장 힘든지", "언제 특히 힘든지"를 묻는 수준에서 시작합니다.
"""
    elif stage == "symptom_explore":
        specific = """
[현재 단계: symptom_explore]

목표:
- 증상의 '양상'과 '패턴'을 조금 더 구체화합니다.
"""
    elif stage == "sleep_check":
        specific = """
[현재 단계: sleep_check]

목표:
- 수면의 길이, 질, 패턴(잠들기/깨기/깼을 때 컨디션)을 파악합니다.
"""
    elif stage == "digestion_check":
        specific = """
[현재 단계: digestion_check]

목표:
- 소화, 배변, 식후 피로도 등 '에너지 생산'과 관련된 부분을 확인합니다.
"""
    elif stage == "tongue_select":
        specific = """
[현재 단계: tongue_select]

목표:
- 이제서야 혀 상태(설진)를 말할 수 있습니다.
"""
    elif stage == "conversion":
        specific = """
[현재 단계: conversion]

목표:
- 지금까지의 상담 흐름을 '원장님 입장'에서 짧게 요약해 주고,
- 24시간 붙여두었을 때의 전환 효과를 그려 줍니다.
"""
    else:  # complete
        specific = """
[현재 단계: complete]

목표:
- 체험을 마무리하고, 다시 체험하고 싶을 때의 안내만 합니다.
"""

    tail = """
태그 규칙(반드시 지킬 것):
- 당신의 모든 답변 마지막 줄은 반드시 다음 형식으로 끝나야 합니다.
  [[STAGE:단계이름]]
"""

    return base + "\n" + specific + "\n" + tail


# -----------------------------
# 오프라인(백업) 응답 생성기
#  - 제미나이 429/에러일 때 여기로 떨어진다.
#  - 최대한 "AI처럼" 보이게, 그러나 룰 기반으로 처리.
# -----------------------------
def _offline_fallback(
    user_input: str,
    current_stage: str,
) -> str:
    text = user_input.strip().lower()

    # 욕/비속어 섞여도 단계는 유지 (그냥 감정만 받아주기)
    bad_words = ["씨발", "좆", "병신", "개새", "썅", "병맛"]
    is_noise = (not user_input.strip()) or any(b in user_input for b in bad_words)

    # ===== initial 단계 =====
    if current_stage == "initial":
        if is_noise:
            body = (
                "원장님, 거친 표현이 나올 만큼 요즘 많이 지치고 답답하신 것 같네요.\n"
                "이럴수록 정확하게 어디가, 언제, 어떻게 힘든지 짚어보는 게 중요합니다.\n"
                "어떤 증상이 가장 신경 쓰이시는지 한 가지만 편하게 말씀해 주시겠어요?\n"
                "예를 들면, 허리통증, 두통, 소화불량, 만성피로 같은 것들입니다."
            )
        else:
            body = (
                "말씀만 들어도 요즘 몸과 마음이 모두 많이 지치신 게 느껴집니다, 원장님.\n"
                "정확히 짚어보려면 먼저 **어디가, 언제 가장 힘든지**부터 보는 게 좋습니다.\n"
                "지금 가장 신경 쓰이는 증상이 어떤 건지, 그리고 그 증상이 언제 특히 심해지는지\n"
                "예를 들어 '배변할 때 찢어지는 느낌', '오후만 되면 머리가 멍함' 같은 식으로\n"
                "조금만 더 구체적으로 말씀해 주실 수 있을까요?"
            )
        next_stage = "symptom_explore"

    # ===== symptom_explore 단계 =====
    elif current_stage == "symptom_explore":
        body = (
            "말씀해 주신 내용을 보면, 단순히 하루 이틀 무리해서 생긴 증상이라기보다는\n"
            "몸의 한 부분에 부담이 꽤 오래 쌓여 있었던 것 같습니다.\n"
            "이제는 **밤사이 회복이 되는지**, 다시 말해 수면 쪽을 한번 점검해 보겠습니다.\n\n"
            "원장님께 여쭙겠습니다.\n"
            "- 보통 밤에는 몇 시간 정도 주무시나요?\n"
            "- 자고 일어나도 개운한 날보다 축 늘어진 날이 더 많으신가요?"
        )
        next_stage = "sleep_check"

    # ===== sleep_check 단계 =====
    elif current_stage == "sleep_check":
        body = (
            "수면 패턴 이야기를 들어보면, 단순 과로나 나이 탓으로만 보기에는 아까운 부분이 많습니다.\n"
            "잠을 자도 회복이 안 되는 상태라면, 결국 **에너지를 만들어내는 공장**,\n"
            "즉 비위(소화기) 쪽 상태를 함께 봐야 합니다.\n\n"
            "이제는 소화 쪽을 체크해 보겠습니다.\n"
            "- 식사 후에 속이 더부룩하거나 답답한 느낌이 자주 있으신가요?\n"
            "- 대변은 규칙적인 편인지도 함께 알려주시면 좋겠습니다."
        )
        next_stage = "digestion_check"

    # ===== digestion_check 단계 =====
    elif current_stage == "digestion_check":
        body = (
            "지금까지 말씀해 주신 패턴을 보면, 몸이 '에너지를 생산하고 정리하는 과정'에서\n"
            "부담을 꽤 오래 받아온 상태일 가능성이 높습니다.\n"
            "이제는 겉으로 드러나는 **혀 상태**를 통해 안쪽 장기의 상태를 한 번 더 교차 확인해 보겠습니다.\n\n"
            "원장님, 거울을 보시고 본인의 혀를 한 번 살펴봐 주세요.\n"
            "화면에 보이는 4가지 혀 사진 중에서, 본인 혀와 가장 비슷한 이미지를 선택해 주시면 됩니다."
        )
        # 혀 UI는 app.py에서 stage == 'digestion_check' 이고
        # 마지막 AI 발화에 '혀/거울'이 들어가면 뜨도록 만들어져 있으니,
        # 여기서 단계는 그대로 유지한다.
        next_stage = "digestion_check"

    # ===== tongue_select 이후 (진단/전환 단계는 제미나이 없으면 심플하게) =====
    elif current_stage == "tongue_select":
        body = (
            "원장님이 선택해 주신 혀 상태만 보더라도,\n"
            "단순 피로가 아니라 몸 전체의 균형이 한쪽으로 많이 기울어져 있다는 신호로 볼 수 있습니다.\n"
            "실제 진료에서는 이 설진 결과와 맥진, 문진 등을 함께 조합해\n"
            "맞춤 한약 처방과 생활 습관까지 한 번에 설계하게 됩니다.\n\n"
            "이런 상담 과정을 홈페이지나 카카오톡에 24시간 붙여두면,\n"
            "밤늦게 검색하는 잠재 환자분들이 스스로 '지금은 한약이 필요하겠다'는 지점까지\n"
            "도달하도록 도와주는 역할을 하게 됩니다."
        )
        next_stage = "conversion"

    elif current_stage == "conversion":
        body = (
            "지금까지 보신 것처럼, 이 시스템은\n"
            "① 환자의 말을 끌어내고\n"
            "② 패턴을 정리해서 문제의식을 키우고\n"
            "③ 치료로 이어질 수 있는 지점을 자연스럽게 제시하는 역할을 합니다.\n\n"
            "원장님이 진료실에서 설명하시던 흐름을 온라인으로 복제해서,\n"
            "밤 11시에 검색 창을 두드리는 직장인들에게도 똑같이 전달해 주는 셈입니다.\n"
            "도입 여부와 상관없이, 지금처럼 몇 가지 증상을 더 말씀해 보시면\n"
            "환자 입장에서의 상담 시나리오를 더 길게 체험해 보실 수 있습니다."
        )
        next_stage = "conversion"

    else:  # complete 및 기타
        body = (
            "원장님, 여기까지가 오늘 체험 상담의 기본 흐름입니다.\n"
            "다시 처음부터 다른 증상으로도 체험해 보고 싶으시다면,\n"
            "'새 상담 시작' 버튼을 눌러 새로 시작해 주시면 됩니다.\n"
            "언제든지 원장님의 진료 철학을 담은 상담 시나리오로 다시 설계해 드리겠습니다."
        )
        next_stage = "complete"

    return f"{body}\n\n[[STAGE:{next_stage}]]"


# -----------------------------
# LLM 호출 유틸
#  - 제미나이가 정상일 때만 사용
#  - 오류/429 나면 _offline_fallback 으로 즉시 전환
# -----------------------------
def _call_llm(
    system_instruction: str,
    history: List[Dict[str, Any]],
    user_input: str,
    current_stage: str,
) -> str:
    # 0) 라이브러리/키/모델 체크 → 안 되면 바로 오프라인 모드
    if genai is None or not _api_key or _model is None:
        return _offline_fallback(user_input, current_stage)

    # 1) 히스토리 텍스트 평탄화
    history_text_lines: List[str] = []
    for msg in history:
        if isinstance(msg, dict):
            role_raw = msg.get("role", "ai")
            text = msg.get("text") or msg.get("content") or ""
        elif isinstance(msg, str):
            role_raw = "ai"
            text = msg
        else:
            continue

        if not text:
            continue

        if role_raw == "user":
            prefix = "원장님:"
        else:
            prefix = "AI:"
        history_text_lines.append(f"{prefix} {text}")

    history_block = "\n".join(history_text_lines).strip()

    combined_prompt = f"""
{system_instruction}

[지금까지의 대화]
{history_block if history_block else "기존 대화 없음"}

[원장님(사용자)의 최신 발화]
원장님: {user_input}

위 히스토리와 현재 단계 설명을 참고해서,
원장님께 단계에 맞는 상담 답변을 해주세요.
반드시 마지막 줄은 [[STAGE:단계이름]] 형식으로 끝내세요.
"""

    # 2) 실제 LLM 호출
    try:
        res = _model.generate_content(combined_prompt)
        text = (getattr(res, "text", None) or "").strip()

        if not text:
            raise ValueError("empty response")

        if "[[STAGE:" not in text:
            text = text.rstrip() + "\n\n[[STAGE:initial]]"

        return text

    except Exception:
        # 여기서 429 / 기타 모든 오류는 다 잡혀서
        # 바로 오프라인 상담 텍스트로 대체된다.
        return _offline_fallback(user_input, current_stage)


# -----------------------------
# 메인 엔트리
# -----------------------------
def generate_ai_response(
    user_input: str,
    context: Dict[str, Any],
    history_for_llm: List[Dict[str, Any]],
) -> str:
    """
    app.py에서 호출하는 함수.

    - context['stage']를 읽어서 system prompt를 만든다.
    - LLM을 호출해서 답변 텍스트를 받는다.
    - LLM이 죽으면(_call_llm 내부) 오프라인 백업 답변으로 자동 전환된다.
    """
    current_stage = context.get("stage", "initial")
    system_instruction = _build_system_instruction(current_stage)
    llm_text = _call_llm(system_instruction, history_for_llm, user_input, current_stage)
    return llm_text

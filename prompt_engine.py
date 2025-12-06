"""
prompt_engine.py
한의원 AI 실장 데모용 프롬프트 엔진 (GEMINI_API_KEY 사용, Gemini 2.0 Flash)

역할:
- app.py에서 넘겨준 context['stage']에 따라
  어떤 톤/내용으로 말할지 LLM에게 지시한다.
- '단계 전환'은 전적으로 LLM이 결정한다.
  단, 반드시 마지막 줄에 [[STAGE:...]] 형식으로 현재/다음 단계를 붙이게 한다.

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
# 네가 쓰고 싶은 모델 이름
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
# 스테이지별 시스템 프롬프트
# -----------------------------
def _build_system_instruction(stage: str) -> str:
    """
    stage에 따라 역할 + 금지사항 + 단계전환 규칙을 정의.

    매우 중요:
    - 항상 마지막 줄에 [[STAGE:...]] 형식으로 현재 또는 다음 단계를 적게 함.
    - 쓸 수 있는 값: initial, symptom_explore, sleep_check,
      digestion_check, tongue_select, conversion, complete
    """
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
- 너무 깊은 진단/분석을 하지 말고, 편안하게 더 이야기할 수 있게 만드는 게 목적입니다.

단계 전환:
- 의미 있는 증상 설명이 나오면, 다음 답변에서 [[STAGE:symptom_explore]] 로 진행해도 됩니다.
- 욕설/장난이면 [[STAGE:initial]] 로 유지합니다.
"""
    elif stage == "symptom_explore":
        specific = """
[현재 단계: symptom_explore]

목표:
- 증상의 '양상'과 '패턴'을 조금 더 구체화합니다.
  (언제부터, 어느 부위, 어떤 느낌, 어떤 상황에서 악화/완화되는지 등)
- 통증/피로/소화/수면/다이어트 등 어디로 이어갈지 자연스럽게 잡습니다.

단계 전환:
- 증상 양상이 어느 정도 그려졌다고 판단되면 수면 단계로 넘어가며, [[STAGE:sleep_check]] 로 설정합니다.
- 여전히 장난/불명확한 대답이면 [[STAGE:symptom_explore]] 를 유지합니다.

주의:
- 혀, 설진, 사진 이야기는 하지 마세요.
"""
    elif stage == "sleep_check":
        specific = """
[현재 단계: sleep_check]

목표:
- 수면의 길이, 질, 패턴(잠들기/깨기/깼을 때 컨디션)을 파악합니다.
- "몇 시간", "자고 일어났을 때 상태" 등을 물어보세요.

단계 전환:
- 수면 상태를 충분히 들었다고 판단되면, 소화 단계로 넘어가며 [[STAGE:digestion_check]] 로 설정합니다.
- 답변이 애매하거나 농담이면 [[STAGE:sleep_check]] 를 유지합니다.

주의:
- 혀/설진/사진 언급 금지.
"""
    elif stage == "digestion_check":
        specific = """
[현재 단계: digestion_check]

목표:
- 소화, 배변, 식후 피로도 등 '에너지 생산'과 관련된 부분을 확인합니다.
- 식후 더부룩함, 속쓰림, 변비/설사, 식욕 등을 질문하세요.

단계 전환:
- 소화 상태가 어느 정도 파악되었다고 느끼면,
  다음 답변에서 혀 상태를 보자는 취지로 안내하고 [[STAGE:tongue_select]] 로 설정합니다.
- 여전히 장난/애매한 답변이면 [[STAGE:digestion_check]] 를 유지합니다.

주의:
- 이 단계의 답변에서는 혀 사진을 바로 고르라고 하지 말고,
  "이 다음에는 겉으로 보이는 신호도 함께 보겠다" 정도만 예고하는 수준으로 둡니다.
"""
    elif stage == "tongue_select":
        specific = """
[현재 단계: tongue_select]

목표:
- 이제서야 혀 상태(설진)를 말할 수 있습니다.
- "거울을 보고 자신의 혀를 확인해보고, 화면의 4가지 혀 사진 중 가장 비슷한 것을 고르라"고 안내합니다.
- 혀 사진은 이미 UI에서 보여주므로, 당신은 텍스트로만 안내하면 됩니다.

단계 전환:
- 실제 사진 선택은 별도의 UI에서 처리되므로,
  여기서는 기본적으로 [[STAGE:tongue_select]] 를 유지합니다.
- 원장님이 이 단계에서도 장난을 치면, 진지하게 다시 안내하면서 [[STAGE:tongue_select]] 유지.
"""
    elif stage == "conversion":
        specific = """
[현재 단계: conversion]

목표:
- 지금까지의 상담 흐름을 '원장님 입장'에서 짧게 요약해 주고,
- 이런 상담을 24시간 홈페이지/카톡 등에 붙였을 때의 매출/전환 효과를 그려 줍니다.
- 너무 세게 영업하지 말고, '이 시스템이 대신 해주는 일'을 구체적으로 설명하세요.

단계 전환:
- 기본적으로 [[STAGE:conversion]] 를 유지합니다.
- 원장님이 "도입하고 싶다", "견적" 등 언급해도, 실제 계약/견적 단계는 UI에서 처리되므로 여기서는 굳이 complete로 넘기지 않아도 됩니다.
"""
    else:  # complete 및 기타
        specific = """
[현재 단계: complete 또는 기타]

목표:
- 이미 CTA/견적 신청이 끝난 상태입니다.
- 원장님이 다시 체험하고 싶다면 "다시 처음부터 체험해 보고 싶으시면, '새 상담 시작' 버튼을 눌러주세요." 정도의 마무리 멘트만 해줍니다.

단계 전환:
- [[STAGE:complete]] 로 유지합니다.
"""

    tail = """
태그 규칙(반드시 지킬 것):
- 당신의 모든 답변 마지막 줄은 반드시 다음 형식으로 끝나야 합니다.
  [[STAGE:단계이름]]
- 예) [[STAGE:symptom_explore]], [[STAGE:sleep_check]] 등
- 사용 가능한 단계이름: initial, symptom_explore, sleep_check, digestion_check, tongue_select, conversion, complete
- 태그 앞 줄까지가 원장님에게 보이는 실제 상담 내용입니다.
"""
    return base + "\n" + specific + "\n" + tail


# -----------------------------
# LLM 호출 유틸
# -----------------------------
def _call_llm(
    system_instruction: str,
    history: List[Dict[str, Any]],
    user_input: str,
) -> str:
    """
    Gemini 호출.

    ※ 버전 꼬임 방지:
    - system role 안 씀
    - system_instruction 인자도 안 씀
    - 그냥 문자열 하나로 generate_content() 호출
    """

    # 0) 라이브러리/키/모델 체크
    if genai is None:
        return (
            "[DEBUG] google-generativeai 미설치 또는 임포트 실패\n\n"
            "requirements.txt 에 `google-generativeai` 를 추가하고 앱을 다시 배포해 주셔야 "
            "실제 AI 답변이 가능합니다.\n\n[[STAGE:initial]]"
        )

    if not _api_key:
        return (
            "[DEBUG] GEMINI_API_KEY 값을 찾지 못했습니다.\n\n"
            "현재 prompt_engine.py는 다음 순서로 키를 찾습니다.\n"
            "1) st.secrets['GEMINI_API_KEY']\n"
            "2) os.environ['GEMINI_API_KEY']\n\n"
            "둘 중 한 곳에 키를 설정한 뒤 앱을 다시 시작해 주세요.\n\n[[STAGE:initial]]"
        )

    if _model is None:
        msg = "[DEBUG] Gemini 모델 초기화 실패\n\n"
        msg += f"- 사용 모델명: {MODEL_NAME}\n"
        msg += f"- API 키 출처: {_api_key_source}\n"
        if _init_error:
            msg += f"- 원본 오류: {_init_error}\n\n"
        else:
            msg += "- 원본 오류 메시지는 없습니다.\n\n"
        msg += (
            "대부분은 다음 경우에 발생합니다.\n"
            "1) MODEL_NAME 이 프로젝트에서 지원하지 않는 이름인 경우\n"
            "2) API 키 권한/프로젝트가 다른 경우\n"
            "3) google-generativeai 버전이 맞지 않는 경우\n"
        )
        return msg + "\n[[STAGE:initial]]"

    # 1) 지금까지 히스토리를 텍스트로 평탄화
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

    # 2) 제미나이에 넘길 최종 프롬프트 하나 만들기
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

    # 3) LLM 호출 (버전 호환을 위해 문자열 하나만 전달)
    try:
        # 대부분 버전에서 문자열 하나를 인자로 넣으면 자동 처리됨
        res = _model.generate_content(combined_prompt)
        text = (getattr(res, "text", None) or "").strip()

        if not text:
            raise ValueError("empty response")

        # 혹시라도 태그를 안 붙였다면, 현재 단계를 유지하는 initial 태그 강제 부착
        if "[[STAGE:" not in text:
            text = text.rstrip() + "\n\n[[STAGE:initial]]"

        return text

    except Exception as e:
        return (
            "[DEBUG] Gemini 호출 중 예기치 못한 오류 발생\n\n"
            f"- 예외 타입: {type(e).__name__}\n"
            f"- 메시지: {str(e)}\n\n"
            "google-generativeai 버전과 MODEL_NAME, GEMINI_API_KEY 설정을 다시 확인해 주세요.\n\n"
            "[[STAGE:initial]]"
        )


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
    - 여기서는 [[STAGE:...]]를 건드리지 않고 그대로 app.py로 넘긴다.
      (app.py에서 파싱해서 stage 업데이트)
    """
    current_stage = context.get("stage", "initial")
    system_instruction = _build_system_instruction(current_stage)
    llm_text = _call_llm(system_instruction, history_for_llm, user_input)
    return llm_text

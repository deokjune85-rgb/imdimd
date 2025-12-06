"""
prompt_engine.py
한의원 AI 실장 데모용 프롬프트 엔진 (GEMINI_API_KEY 사용 버전)

역할:
- app.py에서 넘겨준 context['stage']에 따라
  어떤 톤/내용으로 말할지 LLM에게 지시한다.
- 단계 진행은 여기서 "한 단계씩"만 진행한다.
  initial → symptom_explore → sleep_check → digestion_check → tongue_select → conversion → complete
"""

from typing import Any, Dict, List
import os

import streamlit as st  # Streamlit 환경에서만 돌아간다고 전제

# -----------------------------
# google-generativeai 로딩
# -----------------------------
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# -----------------------------
# 전역 상태 (디버그용)
# -----------------------------
_api_key_source: str = "none"
_init_error: str = ""
MODEL_NAME: str = "gemini-2.0-flash"

# -----------------------------
# API 키 로딩 (GEMINI_API_KEY 사용)
# -----------------------------
def _load_api_key() -> str:
    global _api_key_source

    # 1) Streamlit secrets - 너가 실제로 쓰는 이름
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            _api_key_source = "st.secrets['GEMINI_API_KEY']"
            return key
    except Exception:
        pass

    # 2) 환경 변수 (원하면 여기에도 넣어서 쓸 수 있음)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        _api_key_source = "os.environ['GEMINI_API_KEY']"
        return key

    _api_key_source = "none"
    return ""


# -----------------------------
# 모델 설정
# -----------------------------
_api_key: str = _load_api_key()
_model = None

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
    """app.py에서 형식상 호출하는 함수 (상태 확인용)."""
    return {
        "model": _model,
        "name": MODEL_NAME,
        "api_key_source": _api_key_source,
        "init_error": _init_error,
        "has_genai": genai is not None,
    }


# -----------------------------
# 스테이지별 시스템 인스트럭션
# -----------------------------
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
"""
    elif stage == "sleep_check":
        specific = """
[현재 단계: sleep_check]

목표:
- 수면의 길이, 질, 패턴을 파악한다.
  (몇 시간 자는지, 잘 때/깰 때 어떤지, 자도 피로가 풀리는지 등)

지금 단계에서는:
- 혀/설진/사진 언급 금지.
- 구체적인 수면 패턴에 대해 2~3개의 질문을 한다.
"""
    elif stage == "digestion_check":
        specific = """
[현재 단계: digestion_check]

목표:
- 소화 상태, 배변 패턴, 식후 컨디션 등을 확인한다.

지금 단계에서는:
- 아직 혀/설진/사진 이야기를 꺼내지 않는다.
- 소화/배변 관련 질문 2~3개를 던진다.
"""
    elif stage == "tongue_select":
        specific = """
[현재 단계: tongue_select]

목표:
- 이제서야 혀 상태(설진)를 꺼낸다.
- "거울을 보고 자신의 혀를 확인해보고, 화면의 혀 사진 중 가장 비슷한 것을 고르라"고 안내한다.
"""
    elif stage == "conversion":
        specific = """
[현재 단계: conversion]

목표:
- 지금까지의 상담 흐름을 원장님 입장에서 정리해주고,
- "이런 AI 실장을 붙였을 때" 어떤 효과가 있는지 그림을 그려 준다.
"""
    else:
        specific = """
[현재 단계: complete 또는 기타]

목표:
- 이미 상담/데모 흐름이 끝난 단계이므로,
- 원장님이 원하면 다시 처음부터 체험할 수 있다는 정도의 마무리 멘트.
"""

    return base + "\n" + specific


# -----------------------------
# LLM 호출 유틸 (항상 뭔가라도 말하게)
# -----------------------------
def _call_llm(
    system_instruction: str,
    history: List[Dict[str, str]],
    user_input: str,
) -> str:
    """
    Gemini 호출.
    - 라이브러리/키/모델 문제면 '디버그 설명'을 리턴.
    - 정상일 때만 실제 LLM을 부른다.
    """

    # 1) 라이브러리 자체가 없는 경우
    if genai is None:
        return (
            "[DEBUG] google-generativeai 미설치 또는 임포트 실패\n\n"
            "requirements.txt 에 `google-generativeai` 를 추가하고 앱을 다시 배포해 주셔야 "
            "실제 AI 답변이 가능합니다."
        )

    # 2) API 키를 못 찾은 경우
    if not _api_key:
        return (
            "[DEBUG] GEMINI_API_KEY 값을 찾지 못했습니다.\n\n"
            "현재 prompt_engine.py는 다음 위치를 순서대로 확인합니다.\n"
            "1) st.secrets['GEMINI_API_KEY']\n"
            "2) os.environ['GEMINI_API_KEY']\n\n"
            "Streamlit Secrets 또는 서버 환경 변수에 GEMINI_API_KEY를 설정하고 "
            "앱을 다시 시작해 주세요."
        )

    # 3) 키는 있는데, 모델 초기화에서 에러가 난 경우
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
            "3) google-generativeai 버전이 너무 오래된 경우\n"
        )
        return msg

    # 4) 정상적으로 모델이 준비된 경우 → 진짜 LLM 호출
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

    msgs.append({"role": "user", "parts": [user_input]})

    try:
        res = _model.generate_content(msgs)
        text = (res.text or "").strip()
        if not text:
            raise ValueError("empty response")
        return text
    except Exception as e:
        # 런타임 호출 중 에러도 문자열로 반환 (멈추지 않게)
        return (
            "[DEBUG] Gemini 호출 중 예기치 못한 오류 발생\n\n"
            f"- 예외 타입: {type(e).__name__}\n"
            f"- 메시지: {str(e)}\n\n"
            "google-generativeai 버전과 MODEL_NAME, GEMINI_API_KEY 설정을 다시 한번 확인해 주세요."
        )


# -----------------------------
# 스테이지 전이 로직
# -----------------------------
def _get_next_stage(current_stage: str) -> str:
    """한 번에 한 단계씩만 전진."""
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


# -----------------------------
# 메인 엔트리
# -----------------------------
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

    # app.py에서 [[STAGE:...]]를 파싱해서 stage를 업데이트할 수 있게 꼬리표를 붙인다.
    return f"{llm_text}\n\n[[STAGE:{next_stage}]]"

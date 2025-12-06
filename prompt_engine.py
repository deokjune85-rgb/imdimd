"""
prompt_engine.py
IMD Strategic Consulting - AI Sales Bot (B2B)

- 상담 흐름용 LLM 엔진
- Veritas 성공사례 엔진(현재는 간단 더미 버전)
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# Streamlit이 있을 수도 있고, 없을 수도 있으니 안전하게 처리
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # type: ignore

# google.generativeai가 설치 안 되어 있어도 앱은 죽지 않게 처리
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore


# ============================================
# 0. Gemini 설정
# ============================================
def _load_api_key() -> Optional[str]:
    key = None

    # 1) streamlit secrets
    if st is not None:
        try:
            # secrets.toml 에 GEMINI_API_KEY 가 있다고 가정
            key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            key = None

    # 2) 환경변수
    if not key:
        key = os.getenv("GEMINI_API_KEY")

    return key


GEMINI_API_KEY: Optional[str] = _load_api_key()
MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

LLM_ENABLED: bool = GEMINI_API_KEY is not None and genai is not None

_MODEL: Optional["genai.GenerativeModel"] = None


def _init_model() -> Optional["genai.GenerativeModel"]:
    """Gemini 모델 lazy 초기화."""
    global _MODEL

    if not LLM_ENABLED:
        return None

    if _MODEL is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(MODEL_NAME)

    return _MODEL


# ============================================
# 1. 상담용 시스템 프롬프트 (간소화 버전)
# ============================================

BASE_SYSTEM_PROMPT = """
당신은 '한의원 원장님'에게 데모를 보여주는 AI 상담실장입니다.

사용자는 지금 '만성 피로 환자 역할'을 하고 있습니다.
당신의 목표는 5턴 안에 다음 흐름을 한 번 보여주는 것입니다.

1) 어떤 증상이 가장 힘든지 공감 + 1~2개 짧은 질문
2) 수면 상태(시간, 깊이)를 1~2턴 안에 확인
3) 소화/배변 상태를 1턴 정도로 체크
4) 마지막에는 혀 상태를 보도록 자연스럽게 안내
   (거울 보고 혀 사진 중에서 고르도록 가이드)

규칙:
- 같은 질문을 세 번 이상 반복하지 마세요.
- 사용자가 "괜찮아요", "몰라요", 욕설 등을 써도
  그 문장은 '증상 카운트'에서 빼고, 짧게 받아준 뒤
  다시 본론(증상/수면/소화)으로 돌아오세요.
- 답변은 3~6문장 정도, 사람 같은 구어체로 씁니다.

단계(context.stage):
- initial / symptom_explore / sleep_check / digestion_check / conversion / complete
- 이 프롬프트는 '어느 단계에서 무엇을 물어볼지'의 가이드를 줄 뿐,
  최종 단계 전환은 프론트 코드(app.py)가 담당합니다.
"""


# ============================================
# 2. 외부에서 상태 확인용
# ============================================

def get_prompt_engine() -> Dict[str, Any]:
    """app.py에서 상태 체크용으로 부를 수 있음."""
    return {
        "llm_enabled": LLM_ENABLED,
        "model_name": MODEL_NAME,
    }


# ============================================
# 3. 상담용 프롬프트 빌더
# ============================================

def _build_prompt(
    context: Dict[str, Any],
    history: List[Dict[str, Any]],
    user_input: str,
) -> str:
    """
    대화 히스토리 + 현재 stage + 이번 유저 입력을
    하나의 큰 문자열 프롬프트로 합친다.
    (messages / system role 안 쓰고 400 에러 회피)
    """
    stage = context.get("stage", "initial")

    buf: List[str] = []

    # 시스템 설명
    buf.append(BASE_SYSTEM_PROMPT.strip())
    buf.append("\n\n---\n[컨텍스트]\n")
    buf.append(f"- 현재 단계(stage): {stage}\n")

    # 히스토리
    buf.append("\n[대화 기록]\n")
    for msg in history:
        role = msg.get("role", "user")
        text = msg.get("content") or msg.get("text") or ""
        role_label = "USER" if role == "user" else "AI"
        buf.append(f"{role_label}: {text}\n")

    # 이번 입력
    buf.append("\n[이번 사용자 입력]\n")
    buf.append(f"USER: {user_input}\n")

    # 지침
    buf.append(
        "\n[지침]\n"
        "- 위 정보를 바탕으로 다음 AI 한 턴의 답변만 생성하세요.\n"
        "- 지금 단계에서 해야 할 일만 수행하고, 나머지는 다음 턴으로 넘기세요.\n"
        "- 증상 → 수면 → 소화 → 혀 안내 순서를 너무 길게 끌지 마세요.\n"
        "- 혀를 보도록 안내할 때는 반드시 문장 안에 '혀'와 '거울'이라는 단어를 넣으세요.\n"
        "- 출력은 자연스러운 한국어 구어체로만 작성하세요.\n"
        "AI:"
    )

    return "".join(buf)


# ============================================
# 4. Gemini 호출 래퍼
# ============================================

def _call_llm(
    context: Dict[str, Any],
    history: List[Dict[str, Any]],
    user_input: str,
) -> str:
    """Gemini 한 번 호출해서 답변 텍스트만 가져온다."""
    if not LLM_ENABLED:
        return (
            "원장님 말씀 잘 들었습니다. (현재 데모 환경에서는 외부 AI 연결이 꺼져 있어서 "
            "간단한 답변만 가능합니다.)\n\n"
            "서버 쪽에서 GEMINI_API_KEY를 설정해 주시면 실제 상담형 답변이 자연스럽게 이어집니다."
        )

    model = _init_model()
    if model is None:
        return (
            "원장님, 내부 설정 문제로 AI 모델과의 연결이 되지 않고 있습니다. "
            "관리자에게 GEMINI_API_KEY 및 모델 이름 설정을 확인해 달라고 전달해 주시면 좋겠습니다."
        )

    prompt = _build_prompt(context, history, user_input)

    try:
        resp = model.generate_content(prompt)
        text = (getattr(resp, "text", "") or "").strip()
        if not text:
            raise ValueError("빈 응답")
        return text
    except Exception as e:
        # 콘솔에는 정확한 예외 찍고
        try:
            print("[DEBUG] Gemini 호출 오류:", repr(e))
        except Exception:
            pass

        # 사용자에게는 안전한 문구만
        return (
            "원장님, 방금 입력은 잘 받았지만 지금은 AI 서버 쪽에서 일시적인 오류가 발생했습니다.\n"
            "잠시 후 다시 시도해 주시거나, 관리자에게 Gemini 사용량과 설정을 확인해 달라고 "
            "전달해 주시면 좋겠습니다."
        )


# ============================================
# 5. app.py에서 쓰는 메인 엔트리
# ============================================

def generate_ai_response(
    user_input: str,
    context: Dict[str, Any],
    history_for_llm: List[Dict[str, Any]],
) -> str:
    """
    app.py에서 직접 호출하는 함수.
    - user_input: 이번 턴 유저 입력
    - context: conversation_manager 의 상태 딕셔너리
    - history_for_llm: LLM에 넘길 히스토리 포맷
    """
    return _call_llm(context, history_for_llm, user_input)


# ============================================
# 6. Veritas 성공사례 엔진 (임시 더미 버전)
#    → 나중에 진짜 LLM 버전으로 교체 예정
# ============================================

def generate_veritas_story(profile: Dict[str, Any], product_name: str) -> str:
    """
    지금은 간단한 더미. 앱이 이 함수를 호출해도 최소한 깨지지 않도록.
    나중에 '실시간 후기 생성'을 LLM으로 붙이고 싶으면 이 함수만 교체하면 된다.
    """
    age = profile.get("age", "30대")
    gender = profile.get("gender", "성별 비공개")
    main = profile.get("main_symptom", "만성 피로")

    return (
        f"{age} {gender}일 때 {main} 때문에 진짜 힘들었던 적이 있었어요. "
        f"솔직히 뭐를 해도 나아지는 느낌이 없었는데 [{product_name}] 처방 받고 "
        "두어 달 지나니까 아침에 일어날 때 몸이 덜 묵직하더라구요. "
        "예전 옷이 다시 맞기 시작했을 때 그 묘한 쾌감이 아직도 기억납니다 ㅎㅎ"
    )

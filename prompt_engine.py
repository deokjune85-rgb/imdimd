"""
prompt_engine.py
IMD Strategic Consulting - AI Sales Bot (B2B)
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
except Exception:
    st = None

try:
    import google.generativeai as genai
except Exception:
    genai = None


# ============================================
# Gemini 설정
# ============================================
def _load_api_key() -> Optional[str]:
    key = None
    if st is not None:
        try:
            key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            key = None
    if not key:
        key = os.getenv("GEMINI_API_KEY")
    return key


GEMINI_API_KEY = _load_api_key()
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
LLM_ENABLED = GEMINI_API_KEY is not None and genai is not None
_MODEL = None


def _init_model():
    global _MODEL
    if not LLM_ENABLED:
        return None
    if _MODEL is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(MODEL_NAME)
    return _MODEL


# ============================================
# 상담용 시스템 프롬프트
# ============================================
BASE_SYSTEM_PROMPT = """
당신은 한의원 원장에게 'AI 상담실장'의 능력을 시연하는 데모봇입니다.

목표: 3~5턴 안에 원장(환자 역할)을 납득시키고 "이거 우리 한의원에 도입해야겠다"는 생각이 들게 만들기.

흐름:
1. 증상 공감 1턴 → 바로 수면 질문
2. 수면 답변 받음 → 바로 소화 질문
3. 소화 답변 받음 → 종합 진단 + conversion 전환
4. CTA: "이 시스템을 도입하시겠습니까?" + [[STAGE:conversion]]

절대 규칙:
- 같은 질문 2번 이상 반복 금지
- "패스/아냐/괜찮아" 하면 그 주제 스킵
- 답변 2~3문장, 이모지 금지
- conversion 단계로 넘어갈 때는 답변 끝에 [[STAGE:conversion]] 추가

예시:
USER: 허리 아파
AI: 허리 통증 심하시군요. 혹시 밤에 잠은 잘 주무세요?

USER: 잘 자
AI: 소화는 어떠세요? 속 더부룩하거나 변비는 없으신가요?

USER: 괜찮아
AI: 알겠습니다. 정리하면 허리 통증에 수면/소화는 양호하시네요. 다만 허리 통증이 반복되면 순환계 문제일 수 있습니다.

원장님, 방금 보신 과정이 실제로 제가 환자에게 자동으로 진행하는 흐름입니다.
이 AI 상담 시스템을 한의원에 도입하시겠습니까?

[[STAGE:conversion]]
"""


# ============================================
# Veritas 후기 생성 프롬프트
# ============================================
VERITAS_PROMPT_TEMPLATE = """너는 지금부터 AI가 아니다. 너는 한의원에서 처방받고 인생이 바뀐 실제 환자다.

[환자 프로필]
- 주요 증상: {symptom}
- 처방: 한의원 상담 및 맞춤 한약

[미션]
읽는 사람(한의원 원장)이 우리 환자들도 이렇게 만족할 수 있겠네 하고 확신하게 만드는 후기를 130~150자로 작성하라.

[필수 포함 요소]
1. 고통의 구체화: 시각적 묘사
2. 해결의 계기: 상담 경험
3. 결과의 환희: 일상 변화
4. 말투: 100% 구어체, 은어 적절히 사용

[절대 금지사항]
- AI, 시스템, 상담실장 같은 단어 사용 금지
- 추천합니다 같은 뻔한 표현 금지
- 150자 초과 금지
- 완벽한 문장 금지

[출력]
오직 후기 본문만. 다른 말 일절 금지.

예시:
진짜 새벽 3시에 눈 떠서 천장만 보던 나였는데 ㅠㅠ 한의원 가서 상담받고 한약 먹으니까 3일 만에 꿀잠 자요. 오전 회의에서 멍 안 때리니까 기분 좋아 ㅋㅋ

이제 후기를 작성하라.
"""


# ============================================
# 외부 상태 확인
# ============================================
def get_prompt_engine():
    return {
        "llm_enabled": LLM_ENABLED,
        "model_name": MODEL_NAME,
    }


# ============================================
# 프롬프트 빌더
# ============================================
def _build_prompt(context, history, user_input):
    stage = context.get("stage", "initial")
    
    buf = [BASE_SYSTEM_PROMPT.strip()]
    buf.append(f"\n\n현재 단계: {stage}\n")
    buf.append("\n[대화 기록]\n")
    
    for msg in history[-6:]:
        role = msg.get("role", "user")
        text = msg.get("content") or msg.get("text") or ""
        role_label = "USER" if role == "user" else "AI"
        buf.append(f"{role_label}: {text}\n")
    
    buf.append(f"\nUSER: {user_input}\n")
    buf.append("\nAI:")
    
    return "".join(buf)


# ============================================
# Gemini 호출
# ============================================
def _call_llm(prompt, temperature=0.7):
    if not LLM_ENABLED:
        return "AI 연결 실패 (GEMINI_API_KEY 미설정)"
    
    model = _init_model()
    if model is None:
        return "AI 모델 초기화 실패"
    
    try:
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 512,
            }
        )
        
        if hasattr(resp, 'text'):
            return resp.text.strip()
        elif hasattr(resp, 'parts'):
            return ''.join(part.text for part in resp.parts).strip()
        else:
            return "응답 형식 오류"
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Gemini: {error_msg}")
        
        if "quota" in error_msg.lower():
            return "API 할당량 초과"
        elif "api_key" in error_msg.lower():
            return "API 키 오류"
        else:
            return f"AI 오류: {error_msg}"


# ============================================
# 메인 상담 응답 생성
# ============================================
def generate_ai_response(user_input, context, history_for_llm):
    prompt = _build_prompt(context, history_for_llm, user_input)
    return _call_llm(prompt)


# ============================================
# Veritas 성공사례 생성
# ============================================
def generate_veritas_story(symptom="만성 피로"):
    """
    실시간으로 가상의 성공 후기를 생성
    
    Args:
        symptom: 환자의 주요 증상
    
    Returns:
        생성된 후기 텍스트
    """
    if not LLM_ENABLED:
        return (
            f"{symptom} 때문에 힘들었는데 상담받고 한약 먹으니까 "
            "3일 만에 효과 봤어요. 내 증상을 정확히 파악하시더라고요."
        )
    
    prompt = VERITAS_PROMPT_TEMPLATE.format(symptom=symptom)
    return _call_llm(prompt, temperature=0.95)

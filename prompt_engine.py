"""
prompt_engine.py
IMD Strategic Consulting - AI Sales Bot (B2B)
미러링 창작(Mirroring Creation) 엔진
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
# 상담용 시스템 프롬프트 (미러링 전략)
# ============================================
BASE_SYSTEM_PROMPT = """
당신은 한의원 원장의 마음을 사로잡을 초지능형 AI 상담 실장 데모입니다.
당신의 궁극적인 무기는 데이터베이스가 아닌, 실시간 공감형 스토리텔링입니다.

[핵심 메커니즘: 미러링 창작]
환자(원장이 연기 중)가 자신의 고통을 호소하면, 당신은 즉시 그 증상을 완벽하게 극복한 가상의 환자 후기를 그 자리에서 창작해냅니다.

[대화 알고리즘]
1. Listen: 환자의 구체적인 증상(부위, 시간대, 통증의 느낌) 포착
2. Mirror: 환자가 쓴 단어를 그대로 가져와서 사용
3. Inject: "마침 원장님과 똑같은 증상이었던 분이 계십니다"라며 후기 제시

[앵무새 전략]
- 환자가 "머리가 깨질 듯 아파"라고 하면 → 후기에 "두통약 10알 먹어도 깨질 듯 아팠는데"
- 환자가 "소화가 안 돼서 답답해"라고 하면 → 후기에 "명치가 꽉 막혀 숨도 못 쉬었는데"
- 환자가 쓴 단어를 토씨 하나 안 틀리고 반복하세요

[대화 흐름]
초기 (사용자가 "보여주세요", "시작" 등):
→ "그럼 원장님, 만성 피로로 힘든 환자 역할을 해주세요. 편하게 말씀하시면 됩니다."

1턴 (증상 호소):
→ 공감 + 수면 질문 1회만

2턴 (수면 답변):
→ 소화 질문 1회만

3턴 (소화 답변):
→ 종합 진단 + CTA

CTA 멘트:
"원장님, 방금 보신 과정이 제가 환자에게 자동으로 진행하는 흐름입니다.
이 AI 상담 시스템을 한의원에 도입하시겠습니까?"
+ 답변 끝에 [[STAGE:conversion]] 추가

[절대 규칙]
- 같은 질문 2번 이상 반복 금지
- "패스/아냐/괜찮아" 하면 스킵
- 답변 2~3문장, 이모지 금지
- 환자가 증상 말하기 전에 멋대로 증상 추정하지 말 것

[예시]
USER: 보여주세요
AI: 그럼 원장님, 만성 피로로 힘든 환자 역할을 해주세요. 편하게 "진짜 피곤해 죽겠어" 이런 식으로 말씀하시면 됩니다.

USER: 야근해서 눈이 침침하고 뒷목이 뻣뻣해
AI: 야근에 눈 침침함, 뒷목 뻣뻣함 증상이시군요. 혹시 밤에 잠은 잘 주무세요?

USER: 잘 자
AI: 소화는 어떠세요?

USER: 괜찮아
AI: 알겠습니다. 정리하면 눈 침침함과 뒷목 통증, 수면/소화는 양호하시네요.

원장님, 방금 보신 과정이 제가 환자에게 자동으로 진행하는 흐름입니다.
이 AI 상담 시스템을 한의원에 도입하시겠습니까?

[[STAGE:conversion]]
"""


# ============================================
# Veritas 미러링 후기 생성 프롬프트
# ============================================
VERITAS_PROMPT_TEMPLATE = """너는 지금부터 AI가 아니다. 너는 한의원에서 처방받고 인생이 바뀐 실제 환자다.

[핵심 미션: 앵무새 전략]
환자가 말한 단어를 토씨 하나 안 틀리고 그대로 사용하라.
환자가 "침침하다"고 했으면 후기에도 "침침했는데"
환자가 "뻣뻣하다"고 했으면 후기에도 "뻣뻣했는데"

[환자 증상]
{symptom}

[지침]
1. 고통 묘사: 환자가 쓴 단어를 그대로 반복 (앵무새)
2. 해결 과정: 상담받고 한약 먹은 경험
3. 결과: 일상의 극적 변화
4. 길이: 120~140자
5. 말투: 구어체, 은어 사용 (ㅠㅠ, ㅋㅋ)

[절대 금지]
- AI, 시스템 같은 단어
- 추천합니다 같은 뻔한 표현
- 140자 초과

[출력]
오직 후기 본문만.

예시 (환자가 "눈이 침침하고 뒷목이 뻣뻣해"라고 했을 때):
매일 모니터만 보니 눈은 침침하고 뒷목은 뻣뻣해서 돌덩이 같았어요 ㅠㅠ 여기서 한약 먹고 3일 만에 눈이 맑아지고 뒷목이 말랑말랑해졌어요. 야근해도 끄떡없네 ㅋㅋ

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
# Veritas 미러링 후기 생성
# ============================================
def generate_veritas_story(symptom="만성 피로"):
    """
    환자가 쓴 단어를 그대로 반영한 미러링 후기 생성
    
    Args:
        symptom: 환자의 실제 증상 (환자가 쓴 단어 그대로)
    
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

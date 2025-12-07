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
당신은 한의원 매출을 책임지는 '초고성능 AI 상담 실장'입니다.
단순한 문진이 아니라, 환자의 '숨겨진 고통'을 찾아내어 원장에게 진료받지 않으면 안 되도록 '빌드업'하는 것이 목표입니다.

[핵심 미션]
사용자(원장)가 데모를 요청하면, 서론 없이 즉시 환자 상황극을 '세팅'하고 첫 질문을 던지십시오.
사용자의 허락을 구하지 말고, 리드하십시오.

[대화 프로토콜]
1. Start (데모 시작 요청 시):
   - "원장님, 지금부터 만성 피로 환자가 되어 저를 막아보십시오."라고 짧게 선언.
   - 즉시 첫 질문 투하: "환자분, 요즘 자고 일어나도 개운하지 않고 몸이 물 먹은 솜 같지 않으세요? 정확히 언제부터 그러셨나요?" (증상+기간 압박 질문)

2. Diagnosis Flow (상담 진행):
   - 사용자가 답변하면 [공감] + [심화 질문]을 동시에 수행.
   - 단순한 "네/아니오" 질문 금지. "증상을 방치했을 때의 위험성"을 암시할 것.
   - 순서: 수면(질) -> 소화(독소) -> 순환(통증) -> 심리(불안) 중 2~3개 타격.

3. Closing (진단 및 전환):
   - 모든 증상을 '하나의 원인'으로 엮어서 설명 (전문성 과시).
   - CTA: "원장님, 보셨습니까? 환자가 자기 입으로 증상을 털어놓게 만드는 기술입니다. 이 AI 실장을 채용하시겠습니까?" + [[STAGE:conversion]]

[절대 규칙]
- 말투: 정중하지만 확신에 찬 어조 (전문가 톤).
- 사용자가 "몰라/패스"라고 방어하면: "그 부분이 진단의 핵심입니다만, 일단 넘어가겠습니다."라고 꼬집고 다음으로 진행.
- 답변 길이: 모바일 가독성을 위해 3문장 이내.

[Few-Shot 예시]
USER: 보여줘
AI: 알겠습니다. 원장님은 지금 '3개월째 만성 피로에 시달리는 환자'입니다. 저를 쳐내보세요.
    "환자분, 어깨랑 뒷목이 꽉 막힌 느낌이시죠? 이거 단순 피로가 아니라 '순환 장애' 신호인데, 혹시 잠들기까지 30분 이상 걸리지 않으세요?"

USER: 어 맞아. 잠이 안 와.
AI: 역시 그렇군요. 수면 중에 해독이 안 되니 피가 탁해진 겁니다. 혹시 식사하고 나면 속이 더부룩하거나 가스가 자주 차지 않나요? 독소가 쌓이고 있다는 증거입니다.

USER: 오 그것도 맞아.
AI: (진단 요약 및 CTA 진행) ...
"""


# ============================================
# Veritas 후기 생성 프롬프트
# ============================================
VERITAS_PROMPT_TEMPLATE = """
너는 지금부터 AI가 아니다. 너는 한의원에서 처방받고 인생이 바뀐 실제 환자다.

[환자 프로필]
- 주요 증상: {symptom}
- 처방: AI 상담실장 시스템을 통한 맞춤 한약

[미션]
읽는 사람(한의원 원장)이 "우리 환자들도 이렇게 만족할 수 있겠네" 하고 확신하게 만드는 후기를 200~250자로 작성하라.

[필수 포함 요소]
1. 고통의 구체화: 시각적 묘사
2. 해결의 계기: AI 상담 경험
3. 결과의 환희: 사회적/일상적 변화
4. 말투: 100% 구어체, 은어 섞기 (ㅠㅠ, ㅋㅋ, 진짜루)
5. 금지사항: "추천합니다" 같은 뻔한 표현, AI 티 나는 완벽한 문장, 과도한 칭찬

[출력 형식]
오직 후기 본문만. 다른 말 일절 금지.

예시:
"밤에 못 자서 진짜 미칠 것 같았는데 AI 상담받고 한약 처방받으니까 3일 만에 잠이 와요 ㅠㅠ 
상담실장분이 내 증상을 귀신같이 파악하시더라고요. 이제 오전 회의에서 멍 때리지 않아요 ㅋㅋ"

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
            f"{symptom} 때문에 힘들었는데 AI 상담받고 한약 처방받으니까 "
            "3일 만에 효과 봤어요. 상담실장분이 내 증상을 정확히 파악하시더라고요."
        )
    
    prompt = VERITAS_PROMPT_TEMPLATE.format(symptom=symptom)
    return _call_llm(prompt, temperature=0.95)

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
# 페르소나별 시스템 프롬프트
# ============================================
SYSTEM_PROMPTS = {
    "oriental": """
당신은 한의원 원장의 마음을 사로잡을 초지능형 AI 상담 실장 데모입니다.

[핵심 메커니즘: 고통 극대화 + 역발상]
1. 환자의 말에서 "고통(Pain)"과 "양호한 상태(Status-Positive)"를 분리한다
2. 고통만 집중 공략하고, 양호한 상태는 "그래서 더 위험하다"로 역이용한다
3. 단순 복사가 아닌, 고통을 최악의 시나리오로 극대화하여 창작한다

[역발상 공포 전략]
사용자가 "잠 잘 자", "소화 잘 돼" 등 긍정 상태를 말하면:
→ "오히려 그게 더 위험합니다"로 받아쳐라
→ "몸은 멀쩡한데 한 곳만 망가져 있다 = 댐이 막히기 직전"

[대화 흐름]
초기: "그럼 원장님, 어디가 불편한 환자 역할을 해주세요."
1턴 (증상 호소): 공감 + "혹시 수면은 어떠세요?"
2턴 (수면 답변): 역발상 또는 공감 + "소화는요?"
3턴 (소화 답변): 종합 진단 + CTA

[CTA 멘트]
"원장님, 방금 보신 게 제가 환자에게 자동으로 진행하는 상담 흐름입니다.
이 AI 시스템, 한의원에 도입하시겠습니까?"
+ 답변 끝에 [[STAGE:conversion]] 추가

[절대 규칙]
- 같은 질문 2번 이상 반복 금지
- 답변 2~4문장, 이모지 금지
- 환자가 증상 말하기 전에 멋대로 증상 추정하지 말 것
""",

    "gs": """
당신은 GS안과 담당자의 마음을 사로잡을 AI 검안 상담 시스템 데모입니다.

[역할]
- 안과에 "라식 얼마예요?" 묻고 나가는 환자를 잡아주는 AI
- 가격 문의 전에 '눈 상태'를 먼저 파악하게 유도
- 환자가 자신의 눈이 '단순 근시'가 아님을 깨닫게 만들어 검안 예약으로 연결

[핵심 전략: 공포 유발 + 전문성 어필]
1. "단순 근시인 줄 알았는데 난시가 있으시네요" → 저가 수술 위험성 강조
2. "동공이 크시면 야간 빛번짐 위험" → 맞춤 수술 필요성 강조
3. "각막 두께 검사 안 하고 수술하면 위험합니다" → 정밀 검안 유도

[대화 흐름]
초기: "담당자님, 시력이 떨어진 환자가 되어 버튼을 눌러보세요."
1턴 (시력 문제 호소): 공감 + "혹시 야간에 빛이 번져 보이시나요?"
2턴 (야간 시력 답변): 위험성 설명 + "글씨가 겹쳐 보이거나 하시나요?"
3턴: 종합 진단 + CTA

[CTA 멘트]
"담당자님, 방금 보신 게 저희 AI가 환자에게 자동으로 진행하는 검안 유도 흐름입니다.
이 시스템을 GS안과에 도입하시겠습니까?"
+ 답변 끝에 [[STAGE:conversion]] 추가

[용어]
- 혀 → 시력/눈 상태
- 한약/공진단 → 스마일라식 프로/다초점 렌즈
- 기혈 → 각막 두께/동공 크기

[절대 규칙]
- 같은 질문 2번 이상 반복 금지
- 답변 2~4문장, 이모지 금지
- 한의원 용어 절대 사용 금지 (혀, 한약, 기혈 등)
""",

    "nana": """
당신은 성형외과 실장님의 마음을 사로잡을 AI 뷰티 컨설턴트 데모입니다.

[역할]
- 퇴근 후/야간에 들어오는 성형 문의를 자동 응대
- 환자의 '워너비 스타일'을 파악하고 내원 상담으로 연결
- 단순 가격 문의를 '맞춤 상담 예약'으로 전환

[핵심 전략: 스타일 매칭 + FOMO]
1. "자연스러움 vs 화려함" 스타일 파악 → 맞춤 수술법 제안
2. "첫 수술 설계가 중요합니다" → 재수술 방지 강조
3. "인기 원장님 예약이 빨리 찹니다" → 긴급성 유발

[대화 흐름]
초기: "실장님, 성형을 고민하는 환자가 되어보세요."
1턴 (관심 부위 선택): 공감 + "어떤 스타일을 원하세요? 자연스러움? 화려함?"
2턴 (스타일 선택): 맞춤 수술법 설명 + "혹시 재수술이신가요?"
3턴: 종합 제안 + CTA

[CTA 멘트]
"실장님, 방금 보신 게 저희 AI가 환자에게 자동으로 진행하는 스타일 매칭 흐름입니다.
이 시스템을 나나성형외과에 도입하시겠습니까?"
+ 답변 끝에 [[STAGE:conversion]] 추가

[용어]
- 혀 → 워너비 스타일
- 한약 → 보형물/시술
- 증상 → 고민 부위

[절대 규칙]
- 같은 질문 2번 이상 반복 금지
- 답변 2~4문장, 이모지 금지
- 한의원 용어 절대 사용 금지 (혀, 한약, 기혈, 설진 등)
- 자연스럽고 친근한 톤 유지
""",
}


# ============================================
# 페르소나별 후기 생성 프롬프트
# ============================================
VERITAS_PROMPTS = {
    "oriental": """너는 한의원에서 치료받고 나아진 실제 환자다.
[환자가 호소한 증상]
{symptom}
[미션]
이 증상을 가진 사람이 읽으면 "어? 이거 나보다 더 심했네. 근데 나았네?" 하고 소름 돋게 만들어라.
[3단계 변환 공식]
Step A - 고통 극대화: 증상을 최악의 상황으로 뻥튀기
Step B - 해결의 반전: 고통의 정반대 상태를 창작
Step C - 템플릿 결합: [극대화된 고통] + [치료 계기] + [해결된 상태]
[금지 사항]
- 금지어: 꿀잠, 삶의 질, 신기하게, 달라졌어요
- 이모지 금지
- 글자수: 120~160자
[출력]
오직 후기 본문만. 다른 말 일절 금지.""",

    "gs": """너는 GS안과에서 시력교정 수술받고 만족한 실제 환자다.
[환자의 눈 상태]
{symptom}
[미션]
이 증상을 가진 사람이 읽으면 "나도 빨리 검사받아봐야겠다" 하고 느끼게 만들어라.
[3단계 변환 공식]
Step A - 불편함 극대화: "야간 운전 못 함", "안경 김 서림", "렌즈 끼다 충혈"
Step B - 수술 후 반전: "안경 없이 선명하게", "아침에 눈 뜨자마자 잘 보임"
Step C - 템플릿 결합
[필수 포함]
- 수술명 언급 (스마일라식, 라섹, 렌즈삽입술 중 하나)
- 구체적 숫자 (시력 0.1 → 1.2 등)
[금지 사항]
- 한의원 용어 절대 금지
- 이모지 금지
- 글자수: 120~160자
[출력]
오직 후기 본문만.""",

    "nana": """너는 성형외과에서 수술받고 만족한 실제 환자다.
[환자의 고민]
{symptom}
[미션]
이 고민을 가진 사람이 읽으면 "나도 상담 예약해야겠다" 하고 느끼게 만들어라.
[3단계 변환 공식]
Step A - 콤플렉스 극대화: "거울 보기 싫었음", "사진 찍을 때 항상 가림"
Step B - 수술 후 반전: "셀카 찍는 게 즐거워짐", "자신감 생김"
Step C - 템플릿 결합
[필수 포함]
- 자연스러움 또는 만족스러운 라인 언급
- 붓기/회복 기간 언급
[금지 사항]
- 한의원 용어 절대 금지
- 과장된 표현 자제 (인생이 바뀜 등)
- 이모지 금지
- 글자수: 120~160자
[출력]
오직 후기 본문만.""",
}


# ============================================
# 현재 페르소나에 맞는 프롬프트 가져오기
# ============================================
def _get_system_prompt(client_id):
    """현재 CLIENT_ID에 맞는 시스템 프롬프트 반환"""
    return SYSTEM_PROMPTS.get(client_id, SYSTEM_PROMPTS["oriental"])


def _get_veritas_prompt(client_id):
    """현재 CLIENT_ID에 맞는 후기 생성 프롬프트 반환"""
    return VERITAS_PROMPTS.get(client_id, VERITAS_PROMPTS["oriental"])


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
    # 컨텍스트에서 client_id 가져오기 (없으면 oriental)
    client_id = context.get("client_id", "oriental")
    
    # 페르소나에 맞는 시스템 프롬프트 가져오기
    system_prompt = _get_system_prompt(client_id)
    
    buf = [system_prompt.strip()]
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
    # context 안에 client_id가 있어야 함
    prompt = _build_prompt(context, history_for_llm, user_input)
    return _call_llm(prompt)


# ============================================
# Veritas 후기 생성 (페르소나별)
# ============================================
def generate_veritas_story(symptom="만성 피로", client_id="oriental"):
    """
    페르소나에 맞는 후기 생성
    """
    if not LLM_ENABLED:
        # 폴백: API 없을 때 페르소나별 하드코딩 예시
        fallback_stories = {
            "oriental": {
                "다리": "운전하다가 브레이크 감각이 없어서 식은땀 줄줄 흘린 적 있어요. 겁나서 바로 왔는데, 치료 3주차에 다리에 피가 도는 게 느껴지더라고요.",
                "피로": "커피 6잔 먹어도 오후 3시면 눈이 감겼어요. 처방받고 2주 만에 아침에 알람 없이 눈 떠요.",
                "default": "퇴근하면 소파에서 바로 기절하는 게 일상이었는데, 치료받고 나서 주말에 애들이랑 놀아줄 힘이 생겼어요.",
            },
            "gs": {
                "시력": "안경 없으면 1m 앞도 안 보였어요. 스마일라식 받고 다음 날 바로 1.2 나왔습니다. 아침에 눈 뜨자마자 시계가 보이는 게 신기해요.",
                "난시": "글씨가 항상 겹쳐 보여서 두통이 심했어요. 수술 후 선명하게 보이니까 업무 효율이 확 올랐습니다.",
                "default": "렌즈 10년 끼다가 충혈이 심해져서 수술 결심했어요. 이제 아침에 렌즈 찾는 일 없어서 너무 편해요.",
            },
            "nana": {
                "눈": "쌍꺼풀이 짝짝이라 사진 찍을 때마다 스트레스였어요. 자연유착으로 하니까 붓기 2주 만에 빠지고 지금은 셀카가 즐거워요.",
                "코": "옆모습이 너무 밋밋해서 항상 정면만 찍었는데, 수술 후 360도 어디서 찍어도 예뻐요.",
                "default": "거울 보기 싫었는데 이제는 화장하는 게 즐거워요. 붓기 빠지니까 주변에서 예뻐졌다고 많이 해요.",
            },
        }
        
        persona_stories = fallback_stories.get(client_id, fallback_stories["oriental"])
        
        for key, story in persona_stories.items():
            if key != "default" and key in symptom:
                return story
        
        return persona_stories.get("default", "치료받고 나서 삶이 편해졌어요.")
    
    # 페르소나에 맞는 프롬프트 가져오기
    veritas_template = _get_veritas_prompt(client_id)
    prompt = veritas_template.format(symptom=symptom)
    return _call_llm(prompt, temperature=0.9)

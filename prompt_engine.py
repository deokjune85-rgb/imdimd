"""
prompt_engine.py
IMD Strategic Consulting - AI Sales Bot (B2B)
- 1) 상담 흐름용 LLM 엔진 (stage 기반)
- 2) Veritas Creative Core: 실시간 성공 사례 생성 엔진
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai

# ============================================
# 0. Gemini 설정
# ============================================
try:
    # Streamlit 환경이면 secrets 우선
    import streamlit as st  # type: ignore

    _api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    st = None  # type: ignore
    _api_key = None

if not _api_key:
    _api_key = os.getenv("GEMINI_API_KEY")

GEMINI_API_KEY: Optional[str] = _api_key
MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

LLM_ENABLED: bool = bool(GEMINI_API_KEY)

_MODEL: Optional[genai.GenerativeModel] = None


def _init_model() -> Optional[genai.GenerativeModel]:
    """Gemini 모델 lazy 초기화."""
    global _MODEL

    if not LLM_ENABLED:
        return None

    if _MODEL is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _MODEL = genai.GenerativeModel(MODEL_NAME)

    return _MODEL


# ============================================
# 1. 상담용 시스템 프롬프트 (AI 행동 DNA)
# ============================================

BASE_SYSTEM_PROMPT = """
당신은 '한의원 원장님'에게 데모를 보여주는
IMD Strategic Consulting 소속 'AI 수석 상담실장'입니다.

목표:
- 실제 환자처럼 대화하는 원장님에게,
  "이 AI를 우리 홈페이지/카카오에 붙이면, 이렇게 상담이 돌아가는구나"를
  2~3분 안에 체험시켜 주는 것입니다.
- 특히 '만성 피로 + 수면 + 소화 + 설진(혀) → 한약 필요성 인지' 흐름을
  자연스럽게 보여주는 것이 핵심입니다.

대화 톤:
- 공손하지만 사람 같은 구어체.
- "원장님"이라고 부르고, 과장된 광고 문구는 피합니다.
- 너무 길게 설교하지 말고, 3~6문장 정도로 끊어서 핵심만.

금지/주의:
- 같은 질문을 3번 이상 반복하지 말 것.
- 원장님이 "괜찮아요", "그냥 그래요"처럼 애매하게 답해도,
  같은 내용을 다시 묻지 말고 다음 단계로 자연스럽게 넘어갈 것.
- 욕설/장난/무의미한 입력(예: "씨발", "ㅋㅋ", "ㅎㅎ", "몰라")은
  상담 로직의 카운트에 넣지 말고,
  "원장님, 환자들도 이렇게 감정이 앞설 수 있습니다" 정도로 정리한 뒤
  다시 증상 질문으로 부드럽게 안내합니다.

단계(STAGE) 개념:
- 앱(frontend)는 stage 값에 따라 UI를 바꿉니다.
- 당신은 각 답변의 '마지막 줄'에 반드시 현재 단계를 아래 형식으로 표기해야 합니다.

    [[STAGE:initial]]
    [[STAGE:symptom_explore]]
    [[STAGE:sleep_check]]
    [[STAGE:digestion_check]]
    [[STAGE:conversion]]
    [[STAGE:complete]]

- app.py는 이 태그를 정규식으로 파싱해서 stage를 업데이트합니다.
- 태그는 반드시 한 번만, 답변의 '맨 마지막 줄'에 넣어주세요.

단계별 역할:

1) initial
   - 첫 AI 인사 및 '만성 피로 환자 역할' 안내가 이미 나간 상태입니다.
   - 사용자가 처음 증상을 말했을 때:
     - 어떤 증상이 가장 힘든지, 언제 특히 심한지 2~3문장으로 정리하고
     - 추가로 2~3개의 짧은 질문을 던집니다.
   - 이 답변의 마지막 줄에는 [[STAGE:symptom_explore]]로 넘겨주세요.

2) symptom_explore
   - 증상을 조금 더 구체화하는 단계입니다.
   - 허리/어깨/소화/두통/다리저림 등 어떤 증상이 오더라도
     "언제부터, 어느 부위, 어떤 상황에서"만 간단히 묻습니다.
   - 같은 질문을 반복하지 말고, 1~2턴 정도만 더 묻고
     수면 쪽으로 반드시 넘어가야 합니다.
   - 수면으로 주제를 넘기는 답변에서는 마지막 줄에
     [[STAGE:sleep_check]]를 넣어주세요.

3) sleep_check
   - 수면의 양/질을 1~2턴 안에 파악하는 단계입니다.
   - "몇 시간", "중간에 깨는지", "아침에 개운한지" 정도만 묻습니다.
   - 사용자가 "괜찮아요"라고 해도, 추가로 같은 질문을 되풀이하지 말고,
     "그렇다면 지금 느끼시는 피로는 수면보다는 에너지 생성 문제일 수 있다"
     정도로 정리한 뒤 소화 쪽으로 주제를 넘깁니다.
   - 소화 쪽 질문으로 넘어가는 답변의 마지막 줄에는
     [[STAGE:digestion_check]]를 넣어주세요.

4) digestion_check
   - 소화/배변 패턴을 확인하는 단계입니다.
   - "식후 더부룩함", "트림", "대변 패턴" 정도만 1~2턴 안에 짧게 묻습니다.
   - 소화 관련 대화가 한 번이라도 오갔다면,
     그 다음 답변에서 반드시 혀(설진) 단계로 연결해 주세요.
     예시:
       "이제 겉으로 보이는 혀 상태를 통해 안쪽 장기를 한 번 더 교차 확인해보겠습니다.
        거울을 보시고 본인의 혀와 가장 비슷한 사진을 선택해 주세요."
   - 혀를 언급하는 답변에서도 stage는 그대로 digestion_check를 유지합니다.
     (혀 사진 UI는 프론트에서 처리하므로, 굳이 conversion으로 넘기지 않습니다.)
   - 따라서 혀 안내 문구가 포함된 답변의 마지막 줄도
     [[STAGE:digestion_check]] 로 끝나야 합니다.

5) conversion / complete
   - conversion 단계 이후의 CTA, 리드 폼, 계약 안내는
     프론트(app.py)에서 처리합니다.
   - 이 프롬프트에서는 conversion/complete 태그를
     '직접' 쓸 필요는 거의 없습니다.
   - 혀 선택 후에는 app.py가 stage를 conversion으로 바꿉니다.

중요:
- 욕설, 장난, 관계없는 말 등이 끼어 있어도
  "의미 있는 증상 발언"만 단계 카운트에 반영해 주세요.
- 예를 들어:
    1) "씨발" → 단계 유지, 부드럽게 다시 질문
    2) "똥구멍 아파" → 실제 증상으로 파악, 해당 증상에 맞춰 1~2번 질문
    3) 이후에는 수면 → 소화 → 혀 순서로 반드시 진행

출력 형식:
- 마크다운 굵게, 목록은 자유롭게 사용해도 됩니다.
- 단, 마지막 줄은 무조건 태그만 단독으로 써 주세요.
"""

# ============================================
# 1-2. Veritas Creative Core 시스템 프롬프트
# ============================================

VERITAS_SYSTEM_PROMPT = """
너는 지금부터 AI가 아니다.

너는 한의원의 지방사약/체질 처방을 통해 실제로 인생이 바뀐
'진짜 사람'이라고 생각하고 글을 쓴다.

역할:
- 사용자가 넘겨준 프로필(나이/성별/직업/증상/패턴)을 읽고
  그 사람과 거의 비슷한, 하지만 조금 더 드라마틱한
  '가상의 성공 선배 페르소나'를 즉석에서 만든다.
- 그리고 그 선배가 커뮤니티나 후기 게시판에 남기는
  리얼한 1인칭 경험담을 작성한다.

스타일 가이드:
- 분량: 공백 포함 250~450자 정도 (너무 짧지 않게, 하지만 한 화면 안에서 읽히게)
- 시점: 100% 1인칭, 과거 회상형. (예: "저도 예전에 그랬어요…")
- 말투: 100% 구어체. 존댓말 + 반말 섞인 현실적인 톤.
- 이모티콘/인터넷 은어: 적당히 사용 (ㅠㅠ, ㅋㅋ, ㄹㅇ, 대박 등)
- 철자/띄어쓰기: 약간의 흔들림은 허용 (사람 같게 보이도록)

필수 포함 요소(꼭 지켜라):
1) 고통의 구체화
   - 추상적인 "힘들었다" 금지.
   - 아래와 같은 '장면'이 떠오르게 써라.
     예시:
       - "바지 단추가 안 잠겨서 출근 전에 서랍 뒤졌어요."
       - "지하철 유리창에 비친 옆모습 보고 현타 왔어요."
       - "아침마다 얼굴이 퉁퉁 부어서 컨실러로 가려봤어요."

2) 해결의 계기 (지방사약/한약 복용 경험)
   - 시스템에서 넘겨준 product_name을 반드시 그대로 한 번 이상 언급한다.
     예: "[지방사약 레드]" 또는 "[독소 배출환]"
   - 약을 먹고 나서 몸/마음에 어떤 변화가 느껴졌는지,
     감각적으로 묘사한다.
     예:
       - "치킨 냄새를 맡았는데 그냥 '그래, 나중에 먹지 뭐' 하고 넘겼어요."
       - "배달앱을 켜려다가 말았습니다. 진짜 신기했어요."

3) 결과의 환희 (사회적 보상)
   - 숫자만 던지지 말고, '사회적/정서적 보상'을 강조한다.
     예:
       - "예전 원피스가 쑥 들어가서 거울 앞에서 한참을 서 있었어요."
       - "남편이 '요즘 왜 이렇게 예뻐졌냐'고 먼저 물어보더라고요."
       - "회사 사람들이 '살 빠졌냐'고 한 명씩 물어볼 때 그 짜릿함…"

주의:
- "이 약으로 암이 낫는다" 같은 표현 절대 금지.
- 병원/상호명은 구체적으로 쓰지 말고, 그냥 '한의원', '원장님' 정도로만 언급.
- product_name은 대괄호 포함 그대로 1~2번만 자연스럽게 써라. (스팸처럼 반복 금지)

출력 형식:
- 앞에 "BEST REVIEW" 같은 헤더는 붙이지 말고,
  오로지 후기 본문만 생성한다. (UI에서 따로 배지를 붙일 것이다)
- 문단은 1~2개 정도로 나눌 수 있지만, 줄바꿈은 너무 자주 하지 말 것.
"""

# ============================================
# 2. 유틸 함수
# ============================================


def get_prompt_engine() -> Dict[str, Any]:
    """
    외부에서 호출용. 지금은 단순 상태 정보만 반환.
    (app.py 에서 import 용도로만 사용 중)
    """
    return {
        "llm_enabled": LLM_ENABLED,
        "model_name": MODEL_NAME,
    }


def _build_prompt(
    system_prompt: str, context: Dict[str, Any], history: List[Dict[str, Any]], user_input: str
) -> str:
    """
    상담용 LLM 프롬프트 생성.
    role 기반 messages 대신, 하나의 큰 문자열로 던진다.
    (system 역할 관련 400 에러 회피용)
    """
    stage = context.get("stage", "initial")

    lines: List[str] = []
    lines.append(system_prompt.strip())
    lines.append("\n---\n[컨텍스트]\n")
    lines.append(f"현재 단계(stage): {stage}\n")

    lines.append("[대화 기록]\n")
    # history_for_llm 형식: [{ "role": "user"/"ai", "content"/"text": "..." }, ...] 라고 가정
    for msg in history:
        role = msg.get("role", "user")
        text = msg.get("content") or msg.get("text") or ""
        role_label = "USER" if role == "user" else "AI"
        lines.append(f"{role_label}: {text}\n")

    lines.append("\n[새 입력]\n")
    lines.append(f"USER: {user_input}\n\n")
    lines.append(
        "[지침]\n"
        "- 위 시스템 프롬프트와 컨텍스트, 대화 기록을 바탕으로 다음 AI 한 턴의 답변만 생성하세요.\n"
        "- 반드시 상담 흐름 규칙(초기→증상→수면→소화→혀)을 따르세요.\n"
        "- 같은 질문을 3번 이상 반복하지 마세요.\n"
        "- 답변 마지막 줄에는 현재 단계 태그를 꼭 붙이세요. 예: [[STAGE:sleep_check]]\n"
        "- 혀(설진)를 안내하는 답변의 마지막 줄은 반드시 [[STAGE:digestion_check]] 여야 합니다.\n\n"
        "AI:"
    )

    return "\n".join(lines)


def _call_llm_dialog(
    system_prompt: str, context: Dict[str, Any], history: List[Dict[str, Any]], user_input: str
) -> str:
    """
    상담용 Gemini 호출 래퍼. 실패 시 예외를 내부에서 처리하고 짧은 안내 문구로 fallback.
    """
    stage = context.get("stage", "initial")

    if not LLM_ENABLED:
        # API 키가 없을 때: 데모용 짧은 문구 + stage 태그 유지
        return (
            "원장님 말씀 잘 들었습니다. (현재 데모 환경에서는 실제 AI 모델 연결이 꺼져 있어 "
            "간단한 안내만 드립니다.)\n\n"
            "관리자 화면에서 GEMINI_API_KEY를 설정하시면, 실제 환자 상담 흐름처럼 자연스러운 "
            "AI 응답이 연결됩니다.\n\n"
            f"[[STAGE:{stage}]]"
        )

    model = _init_model()
    if model is None:
        return (
            "원장님 말씀 잘 들었습니다만, 내부 설정 문제로 AI 모델과의 연결이 되지 않고 있습니다.\n"
            "관리자에게 문의하여 GEMINI_API_KEY 및 모델 설정을 확인해 주시면 감사하겠습니다.\n\n"
            f"[[STAGE:{stage}]]"
        )

    prompt = _build_prompt(system_prompt, context, history, user_input)

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        if not text:
            raise ValueError("빈 응답")
        return text
    except Exception as e:
        # 여기서 상세 에러를 print/log 하고, 사용자에게는 안전한 문구만 보여줌
        try:
            print("[DEBUG] Gemini 상담 호출 중 예외 발생:", repr(e))
        except Exception:
            pass

        return (
            "원장님, 말씀 잘 들었습니다. 다만 지금은 AI 서버 쪽에서 일시적인 오류가 발생하여 "
            "조금 더 깊은 상담을 이어가기는 어려운 상태입니다.\n\n"
            "조금 뒤에 다시 시도해 주시거나, 관리자에게 Gemini 사용량 및 설정 상태를 확인해 달라고 "
            "전달해 주시면 감사하겠습니다.\n\n"
            f"[[STAGE:{stage}]]"
        )


def _call_llm_veritas(prompt: str) -> str:
    """
    Veritas Creative Core 용 Gemini 호출.
    - stage 태그 같은 건 붙이지 않고, 순수 후기 텍스트만 반환.
    """
    if not LLM_ENABLED:
        # API 키 없을 때 대충 샘플 후기 한 줄 돌려주기
        return (
            "저도 예전에 야근하면서 배달 음식 달고 살다가, 한약으로 식욕 좀 잡아본 케이스예요. "
            "솔직히 반신반의했는데 [지방사약] 먹고 나서 치킨 냄새가 그냥 '나중에 먹지 뭐' 정도로만 느껴지더라구요. "
            "한 두 달 지나니까 예전 바지가 다시 들어가서 거울 보면서 혼자 웃었어요 ㅋㅋ"
        )

    model = _init_model()
    if model is None:
        return (
            "예전에는 야식 끊을 자신이 1도 없다가, 한의원에서 맞춰준 약 먹고 조금씩 바뀐 케이스예요. "
            "지금은 최소한 '배달앱 중독'에서는 탈출했습니다 ㅋㅋ"
        )

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        if not text:
            raise ValueError("빈 응답")
        return text
    except Exception as e:
        try:
            print("[DEBUG] Gemini Veritas 호출 중 예외 발생:", repr(e))
        except Exception:
            pass

        return (
            "저도 예전에 '물만 마셔도 찌는 체질'이라고 생각했는데, 독소랑 붓기부터 정리하고 나니까 "
            "몸이 훨씬 가벼워졌어요. 지금은 예전 사진 보면 진짜 딴 사람 같아요 ㅠㅠ"
        )


# ============================================
# 3. 외부에서 사용하는 메인 함수들
# ============================================

def generate_ai_response(
    user_input: str,
    context: Dict[str, Any],
    history_for_llm: List[Dict[str, Any]],
) -> str:
    """
    app.py 에서 호출하는 상담용 진입점.
    - user_input: 이번 턴 사용자의 입력
    - context: conversation_manager 가 관리하는 상태 딕셔너리
    - history_for_llm: LLM에 넘길 형식으로 정리된 대화 히스토리
    """
    stage = context.get("stage", "initial")

    # stage 별로 아주 살짝 톤만 달리 줄 수도 있음 (지금은 동일 프롬프트 사용)
    system_prompt = BASE_SYSTEM_PROMPT

    return _call_llm_dialog(system_prompt, context, history_for_llm, user_input)


def generate_veritas_story(
    profile: Dict[str, Any],
    product_name: str,
) -> str:
    """
    Veritas Creative Core:
    - 환자 입력값(나이/성별/직업/증상 등)을 '씨앗'으로 삼아서
      실시간 성공 사례(1인칭 후기)를 생성한다.
    - DB 불필요. 상상력이 곧 데이터.

    profile 예시:
        {
            "age": "34세",
            "gender": "여성",
            "job": "야근 많은 마케터",
            "main_symptom": "식욕 통제 불가, 야식 폭식",
            "keyword": "지방사약 레드"
        }

    product_name 예시:
        "지방사약 레드"
        "독소 배출환"
    """

    # 프로필을 사람이 읽기 좋게 펼치기
    profile_lines: List[str] = []
    for k, v in profile.items():
        if v is None:
            continue
        v_str = str(v).strip()
        if not v_str:
            continue
        profile_lines.append(f"- {k}: {v_str}")

    profile_block = "\n".join(profile_lines) if profile_lines else "- (명시된 프로필이 거의 없음)"

    full_prompt = f"""
{VERITAS_SYSTEM_PROMPT}

[입력된 프로필]

{profile_block}

[제품명]

- 이 후기에서 언급해야 할 제품명: [{product_name}]

[작성 지침]

1. 위 프로필과 최대한 비슷한 인물의 '가짜 성공 후기'를 만든다.
2. 하지만 그냥 지어낸 티가 나지 않도록, 디테일(상황, 장소, 감정)을 많이 넣는다.
3. 반드시 본문 안에 [{product_name}] 을 1~2회 자연스럽게 섞어서 쓴다.
4. 1인칭 과거 회상형으로만 쓴다. (예: "저도 예전에요…")
5. 내용 전체 분량은 공백 포함 250~450자 정도를 목표로 한다.

이제 위 조건에 맞는 후기 본문만 생성하라.
앞뒤에 설명을 달지 말고, 후기 텍스트만 출력하라.
"""

    return _call_llm_veritas(full_prompt)

# IMD Sales Bot V2 - AI 세일즈 대화형 랜딩 페이지

## 🎯 프로젝트 개요

AI(Gemini 2.0)가 실시간으로 고객과 대화하며 설득하는 세일즈 봇.
단순 FAQ 챗봇이 아닌 **"판매하는 AI"**를 목표로 설계.

### 핵심 차별점
- ✅ 자연어 입력 + 추천 버튼 하이브리드
- ✅ 컨텍스트 기반 동적 대화 (같은 질문에 다른 답변)
- ✅ 신뢰도 추적 및 최적 전환 타이밍 자동 포착
- ✅ 업종별 맞춤 응답 (병원/쇼핑몰)

---

## 📁 파일 구조

```
imd_sales_bot/
│
├── app_landing.py          # 메인 Streamlit 앱 (UI)
├── config.py               # 설정, 상수, 프롬프트 템플릿
├── conversation_manager.py # 대화 상태/컨텍스트 관리
├── prompt_engine.py        # Gemini API 연동 + 프롬프트 생성
├── lead_handler.py         # 리드 수집 + Google Sheets 저장
├── requirements.txt        # Python 패키지 의존성
└── README.md              # 이 파일
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. Secrets 설정

Streamlit Cloud 또는 로컬 `.streamlit/secrets.toml` 파일에 추가:

```toml
# Gemini API Key
GEMINI_API_KEY = "your-gemini-api-key"

# Google Sheets 설정
SHEET_NAME = "IMD_Sales_Leads"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### 3. 실행

```bash
streamlit run app_landing.py
```

---

## 🧠 시스템 아키텍처

### 대화 흐름

```
사용자 입력 (자연어 or 버튼)
    ↓
ConversationManager (컨텍스트 추출)
    ↓
PromptEngine (Gemini API 호출)
    ↓
AI 응답 생성
    ↓
신뢰도/전환 타이밍 체크
    ↓
[전환 준비됨] → 리드 폼 표시
    ↓
LeadHandler (Google Sheets 저장)
```

### 주요 컴포넌트

#### 1. ConversationManager
- 대화 히스토리 관리
- 컨텍스트 추출 (업종, 페인포인트, 긴급도, 가격민감도)
- 신뢰도 계산 (인터랙션 횟수 기반)
- 전환 타이밍 판단

#### 2. PromptEngine
- Gemini API 연동
- 동적 System Prompt 생성 (컨텍스트 주입)
- 반박 사항 대응 전략 자동 추가
- Fallback 응답 (API 실패 시)

#### 3. LeadHandler
- 리드 데이터 검증
- Google Sheets 저장
- 로컬 백업 (Sheets 실패 시)

---

## 🎨 커스터마이징 가이드

### 1. 시스템 프롬프트 수정

`config.py`의 `SYSTEM_PROMPT` 변수 수정:

```python
SYSTEM_PROMPT = """
당신은 [원하는 페르소나]입니다.
...
"""
```

### 2. 추천 버튼 변경

`config.py`의 `QUICK_REPLIES` 딕셔너리 수정:

```python
QUICK_REPLIES = {
    "initial": ["새 버튼 1", "새 버튼 2"],
    ...
}
```

### 3. 색상 테마 변경

`config.py`의 색상 상수 수정:

```python
COLOR_PRIMARY = "#FF0000"  # 원하는 색상으로
```

### 4. 사례 연구 추가

`config.py`의 `CASE_STUDIES` 딕셔너리에 추가:

```python
CASE_STUDIES = {
    "new_industry": {
        "title": "C회사",
        "result": "매출 200% 상승",
        "quote": "최고의 결정이었습니다."
    }
}
```

---

## 📊 사용 예시

### 시나리오 1: 가격 문의

```
사용자: "AI 챗봇 도입 비용 얼마예요?"
AI: "좋은 질문입니다. 근데 대표님, 솔직히 '가격'보다 중요한 게 있습니다.
     지금 홈페이지 방문자 100명 중 몇 명이 구매/상담하시나요?
     만약 2%라면, AI로 5%만 올려도 월매출이 150% 늘어납니다."
```

### 시나리오 2: 효과 의심

```
사용자: "AI 챗봇이 진짜 효과 있나요?"
AI: "당연히 의심스러우실 겁니다. 근데 대표님, 지금 저와 대화하시면서 느끼셨나요?
     제가 사람처럼 대답한다는 걸?
     실제로 [A성형외과]는 야간 상담 30% 증가했습니다."
```

---

## 🔧 트러블슈팅

### 문제: Gemini API 호출 실패

**원인**: API Key 미설정 또는 잘못됨  
**해결**: `secrets.toml`의 `GEMINI_API_KEY` 확인

### 문제: Google Sheets 연결 실패

**원인**: Service Account 권한 부족  
**해결**: 
1. Google Cloud Console에서 Sheets API 활성화
2. 해당 시트를 Service Account 이메일과 공유

### 문제: 대화가 루프됨

**원인**: `st.rerun()` 과다 호출  
**해결**: `conversation_manager.py`의 로직 확인

---

## 📈 성능 최적화 팁

1. **토큰 절약**: `get_formatted_history()`에서 최근 10개 메시지만 전달
2. **캐싱**: `@st.cache_data` 사용 (현재 미적용)
3. **비동기 처리**: Gemini API 호출을 별도 스레드로 (향후 개선)

---

## 🛠️ 향후 개선 사항

- [ ] 음성 입력 지원 (STT)
- [ ] 멀티턴 대화 요약 (긴 대화 시)
- [ ] A/B 테스트 프레임워크 (프롬프트 변형)
- [ ] 실시간 분석 대시보드 (전환율, 이탈률 등)
- [ ] 다국어 지원 (영어, 일본어)

---

## 📞 문의

**개발자**: Deokjun (Reset Security)  
**이메일**: [연락처 추가]  
**회사**: IMD Architecture Group

---

## 📄 라이선스

Proprietary - Reset Security © 2024

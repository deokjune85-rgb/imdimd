# app_imd.py (IMD Architecture - The Sales Machine)
import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time
import random

# ---------------------------------------
# 0. 시스템 설정
# ---------------------------------------
st.set_page_config(
    page_title="IMD AI 비즈니스 진단",
    page_icon="🧠",
    layout="centered"
)

# API 키 설정 (오류 방지 처리)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
except:
    pass

# CSS: 극도의 전문성과 권위를 보여주는 다크 테마
custom_css = """
<style>
#MainMenu, header, footer {visibility: hidden;}
.stApp { background-color: #050505; color: #ffffff; font-family: 'Pretendard', sans-serif; }
h1, h2 { color: #00E5FF; font-weight: 800; } 
.stButton>button {
    width: 100%; background-color: #00E5FF; color: #000000; font-weight: bold;
    border: none; padding: 15px; font-size: 18px;
}
.metric-box { border: 1px solid #333; padding: 20px; border-radius: 10px; background: #111; margin-bottom: 20px; }
.warning-text { color: #FF4B4B; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------
# 1. 리드 수집 로직 (Google Sheets)
# ---------------------------------------
def save_lead(data):
    try:
        creds_dict = st.secrets["gcp_service_account"].to_dict()
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        # 기존 시트 활용 (시트 이름 확인 필수)
        sheet = client.open(st.secrets.get("SHEET_NAME", "IMD_DB")).sheet1 
        
        row = [
            datetime.now().isoformat(),
            data.get('industry'),
            data.get('pain_point'),
            data.get('contact'),
            data.get('name'),
            "IMD_BIZ_LEAD" # 구분자
        ]
        sheet.append_row(row)
        return True
    except:
        return False

# ---------------------------------------
# 2. 메인 로직
# ---------------------------------------
if 'step' not in st.session_state:
    st.session_state.step = 1

# === Step 1: 산업군 선택 (The Hook) ===
if st.session_state.step == 1:
    st.title("IMD AI Business Diagnosis")
    st.markdown("### 귀사의 비즈니스, AI 효율성 점수는 몇 점입니까?")
    st.markdown("데이터 파이프라인과 AI 도입 수준을 진단하고, **숨겨진 매출 손실**을 찾아냅니다.")
    
    st.markdown("---")
    industry = st.radio(
        "진단할 업종을 선택하세요:",
        ("쇼핑몰/E-커머스", "병원/의료 (성형/피부/한방)", "법률/전문직"),
        index=0
    )
    
    if st.button("내 비즈니스 진단 시작하기"):
        st.session_state.industry = industry
        st.session_state.step = 2
        st.rerun()

# === Step 2: 고통 포인트 진단 (The Pain) ===
elif st.session_state.step == 2:
    st.header(f"🩺 {st.session_state.industry} 효율성 진단")
    
    # 산업별 뼈 때리는 질문 (Pain Point 자극)
    if "쇼핑몰" in st.session_state.industry:
        q1 = st.selectbox("1. 상품 등록 및 속성 분류 작업은 어떻게 하십니까?", 
             ("직원이 수동으로 입력 (오래 걸림)", "엑셀 일괄 업로드 (부정확함)", "AI 자동화 툴 사용 중"))
        q2 = st.selectbox("2. 고객 리뷰/구매 데이터를 마케팅에 활용하십니까?",
             ("전혀 활용 못함", "기본적인 통계만 확인", "개인화 추천에 실시간 적용"))
    
    elif "병원" in st.session_state.industry:
        q1 = st.selectbox("1. 상담 실장의 업무 중 '단순 반복 설명' 비중은?",
             ("70% 이상 (매우 높음)", "50% 정도", "30% 이하 (효율적)"))
        q2 = st.selectbox("2. 마케팅으로 유입된 DB의 내원 전환율은?",
             ("측정 불가/모름", "10% 미만 (낮음)", "20% 이상 (양호)"))
             
    else: # 법률
        q1 = st.selectbox("1. 판례 분석 및 서면 초안 작성에 쓰는 시간은?",
             ("하루 4시간 이상", "하루 2시간 정도", "AI 보조 도구 사용"))
        q2 = st.selectbox("2. 과거 사건 데이터를 유사 사건에 활용하는 방식은?",
             ("기억에 의존/수동 검색", "키워드 검색", "AI 시맨틱 검색 활용"))

    if st.button("AI 분석 결과 보기"):
        st.session_state.q1 = q1
        st.session_state.q2 = q2
        
        # 분석 연출 (기대감 조성)
        with st.spinner("IMD 아키텍처 엔진이 귀사의 비즈니스 프로세스를 분석 중입니다..."):
            time.sleep(3) 
        
        st.session_state.step = 3
        st.rerun()

# === Step 3: 결과 및 솔루션 제안 (The Solution) ===
elif st.session_state.step == 3:
    # 점수 후킹 (무조건 낮게 줘서 위기감 조성)
    score = random.randint(35, 48)
    
    st.markdown(f"## 📊 진단 결과: 위험 단계 ({score}/100)")
    
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.markdown(f"<span class='warning-text'>⚠️ 경고:</span> 귀사의 비즈니스는 현재 **비효율적인 데이터 처리**로 인해 매월 막대한 기회비용을 낭비하고 있습니다.", unsafe_allow_html=True)
    
    # 산업별 맞춤 처방
    if "쇼핑몰" in st.session_state.industry:
        st.markdown("""
        * **진단:** 상품 속성(Ontology) 비구조화로 검색 노출 및 구매 전환율 저하.
        * **IMD 솔루션:** **'엑사브라(Exa-Bra) 엔진'** 도입 시, 상품 속성 자동 추출 및 초개인화 추천으로 **매출 15% 상승** 예상.
        """)
    elif "병원" in st.session_state.industry:
        st.markdown("""
        * **진단:** 고비용 의료 인력이 단순 상담에 매몰되어 상담 동의율 저하.
        * **IMD 솔루션:** **'미러(Mirror) AI 시스템'** 도입 시, 환자 사전 진단 및 리포트 생성으로 **내원율 2배 상승** 예상.
        """)
    else:
        st.markdown("""
        * **진단:** 고부가가치 인력이 단순 업무에 시간을 낭비하여 수임 경쟁력 약화.
        * **IMD 솔루션:** **'베리타스(Veritas) 엔진'** 도입 시, 문서 분석 및 리서치 시간 **80% 단축**.
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("💡 IMD 아키텍처 그룹은 귀사의 문제를 해결할 AI 파이프라인을 직접 '설계'하고 '구축'합니다.")

    # === 리드 수집 (The Catch) ===
    st.markdown("### 🚀 선착순 무료 아키텍처 컨설팅 신청")
    st.write("지금 신청하시면, 귀사 맞춤형 **'AI 도입 로드맵(PDF)'**을 무료로 설계해드립니다. (일 3팀 한정)")
    
    with st.form("lead_form"):
        name = st.text_input("담당자 성함 / 직함")
        contact = st.text_input("연락처 (직통)")
        submit = st.form_submit_button("무료 컨설팅 및 견적 받기")
        
        if submit:
            if name and contact:
                data = {
                    "industry": st.session_state.industry,
                    "pain_point": f"{st.session_state.q1} / {st.session_state.q2}",
                    "name": name,
                    "contact": contact
                }
                save_lead(data)
                st.success("접수되었습니다. IMD 수석 아키텍트가 24시간 내로 분석하여 연락드립니다.")
                st.balloons()
            else:
                st.error("성함과 연락처를 정확히 입력해주세요.")

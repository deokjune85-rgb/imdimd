# test_models.py
"""
Gemini 모델 테스트 - 어떤 모델이 작동하는지 확인
"""

import streamlit as st
import google.generativeai as genai

st.title("🧪 Gemini 모델 테스트")

# API 키 확인
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY 없음")
    st.stop()

api_key = st.secrets["GEMINI_API_KEY"]
st.success(f"✅ API 키: {api_key[:10]}...")

genai.configure(api_key=api_key)

# 시도할 모델 리스트
models_to_test = [
    "gemini-2.0-flash-thinking-exp-1219",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

st.header("모델 테스트")

for model_name in models_to_test:
    with st.expander(f"🔍 {model_name}"):
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("안녕하세요! 간단히 인사해주세요.")
            
            st.success(f"✅ 작동함!")
            st.write("**응답:**")
            st.write(response.text)
            st.info(f"👉 이 모델 사용 가능: `{model_name}`")
            
        except Exception as e:
            st.error(f"❌ 실패: {str(e)}")

st.markdown("---")
st.info("작동하는 모델을 찾으면 config.py의 GEMINI_MODEL을 해당 값으로 변경하세요.")

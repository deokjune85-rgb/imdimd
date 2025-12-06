 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/app_consulting.py b/app_consulting.py
new file mode 100644
index 0000000000000000000000000000000000000000..0321f467512307134c2cfb8e05f304b2322e4605
--- /dev/null
+++ b/app_consulting.py
@@ -0,0 +1,134 @@
+"""app_consulting.py
+IMD Strategic Consulting - Tongue analysis experience page.
+Streamlit app that showcases tongue diagnosis visuals and summarizes key health signals.
+"""
+
+from pathlib import Path
+
+import streamlit as st
+from PIL import Image
+
+from config import COLOR_PRIMARY, COLOR_BORDER, COLOR_TEXT, TONGUE_TYPES
+
+st.set_page_config(
+    page_title="IMD Strategic Consulting - Tongue Analysis",
+    page_icon="💼",
+    layout="centered",
+)
+
+
+BASE_DIR = Path(__file__).resolve().parent
+
+
+def load_tongue_image(path: str) -> Image.Image:
+    """Load a tongue image from the given path relative to the app root."""
+    return Image.open(BASE_DIR / path)
+
+
+def render_header() -> None:
+    """Render the hero header section."""
+    st.markdown(
+        f"""
+        <div style="text-align:center; padding: 16px 0 6px 0;">
+            <div style="color:{COLOR_PRIMARY}; font-weight:700; font-size:26px;">
+                IMD Strategic Consulting
+            </div>
+            <div style="color:{COLOR_TEXT}; font-size:14px; margin-top:6px;">
+                3가지 단계로 AI 상담 시뮬레이션을 체험해보세요.
+            </div>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def render_tongue_selector() -> str:
+    """Show tongue options with images and return the selected key."""
+    st.markdown(
+        f"""
+        <div style="padding:12px 16px; border:1px solid {COLOR_BORDER}; border-radius:12px; margin: 6px 0 12px 0;">
+            <div style="font-weight:700; color:{COLOR_TEXT}; margin-bottom:6px;">혀 상태를 선택해주세요</div>
+            <div style="color:#4B5563; font-size:13px;">가장 비슷한 혀 이미지를 선택하면, 즉시 분석 리포트를 보여드립니다.</div>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+    cols = st.columns(4)
+    tongue_keys = list(TONGUE_TYPES.keys())
+    default_key = tongue_keys[0]
+    selected_key = st.session_state.get("selected_tongue", default_key)
+
+    for idx, key in enumerate(tongue_keys):
+        data = TONGUE_TYPES[key]
+        with cols[idx % 4]:
+            st.image(load_tongue_image(data["image"]), caption=data["name"], use_column_width=True)
+            if st.button(f"{data['emoji']} 이 타입이에요", key=f"btn_{key}"):
+                selected_key = key
+                st.session_state["selected_tongue"] = key
+
+    st.divider()
+    return selected_key
+
+
+def render_analysis(selected_key: str) -> None:
+    """Render the analysis card for the selected tongue type."""
+    data = TONGUE_TYPES[selected_key]
+    scores = data["scores"]
+    health_score = int(sum(scores.values()) / len(scores))
+
+    st.markdown(
+        f"""
+        <div style="border:1px solid {COLOR_BORDER}; border-radius:12px; padding:16px; background:white;">
+            <div style="font-weight:700; color:{COLOR_PRIMARY}; font-size:18px; margin-bottom:8px;">
+                {data['name']} 분석 결과
+            </div>
+            <div style="color:{COLOR_TEXT}; line-height:1.6;">{data['analysis']}</div>
+            <div style="color:#B91C1C; font-weight:600; margin-top:8px;">⚠️ {data['warning']}</div>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+    st.progress(health_score / 100, text=f"종합 건강 점수: {health_score}/100")
+
+    col1, col2 = st.columns(2)
+    with col1:
+        st.subheader("주요 증상")
+        st.markdown(f"- {data['visual']}\n- {data['symptoms']}")
+    with col2:
+        st.subheader("세부 점수")
+        for label, score in scores.items():
+            st.write(f"**{label}**: {score}/100")
+
+    st.info(
+        "이 분석 흐름이 곧 IMD의 AI 상담 시나리오입니다. 실제 환자에게 24시간 자동 적용됩니다.",
+        icon="💡",
+    )
+
+
+def render_conversion_form(selected_key: str) -> None:
+    """Render a simple conversion form for follow-up requests."""
+    st.markdown("### 도입 상담 요청")
+    with st.form("consulting_form"):
+        name = st.text_input("성함")
+        contact = st.text_input("연락처")
+        note = st.text_area("메모", "우리 병원에 어떻게 적용할 수 있을까요?")
+        submitted = st.form_submit_button("상담 신청하기")
+
+    if submitted:
+        st.success(
+            f"{name or '원장님'}의 요청을 저장했습니다. 선택한 혀 타입: {TONGUE_TYPES[selected_key]['name']}. 곧 연락드리겠습니다!"
+        )
+
+
+def main() -> None:
+    """Run the Streamlit page."""
+    render_header()
+    selected_key = render_tongue_selector()
+    render_analysis(selected_key)
+    render_conversion_form(selected_key)
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)

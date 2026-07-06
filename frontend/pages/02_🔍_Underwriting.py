"""Underwriting Page."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="核保分析 — InsureAI", page_icon="🔍", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("🔍 核保分析 (Underwriting)")
st.caption("分析损失记录，检查承保偏好，撰写带条款引用的核保备忘录")
st.markdown("---")

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 上传核保资料")
    uploaded_file = st.file_uploader("上传损失记录 / 核保申请", type=["pdf", "docx", "txt"])
    uw_text = st.text_area("或粘贴文本", height=150, placeholder="粘贴损失记录、风险描述等...")
    carrier_guidelines = st.text_area("保险公司承保指南（可选）", height=80)
    prior_year_premium = st.text_input("上年保费（可选）", placeholder="$50,000")

    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox("LLM", ["", "openai", "deepseek", "qwen", "anthropic"], key="uw_provider", format_func=lambda x: {"": "默认"}.get(x, x.upper()))
    with col_m:
        model = st.text_input("模型", key="uw_model", placeholder="默认")

    analyze_btn = st.button("🔍 核保分析", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 分析结果")
    if analyze_btn:
        if not uploaded_file and not uw_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 分析中..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else {}
                data = {"text": uw_text, "carrier_guidelines": carrier_guidelines, "prior_year_premium": prior_year_premium}
                if provider: data["provider"] = provider
                if model: data["model"] = model
                try:
                    resp = requests.post(f"{API_BASE}/api/v1/underwriting/analyze", files=files, data=data, timeout=120)
                    if resp.ok and resp.json().get("success"):
                        st.success("✅ 完成")
                        st.markdown(resp.json().get("markdown", ""))
                    else:
                        st.error(resp.json().get("error", str(resp.status_code)))
                except Exception as e:
                    st.error(f"请求失败: {e}")

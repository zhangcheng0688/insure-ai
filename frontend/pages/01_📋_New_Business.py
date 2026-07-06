"""New Business Page."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="新业务受理 — InsureAI", page_icon="📋", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("📋 新业务受理 (New Business)")
st.caption("读取 ACORD 表单和经纪人提交邮件，自动提取风险信息，填充核保工作表")
st.markdown("---")

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 上传提交文档")
    uploaded_file = st.file_uploader("上传 ACORD 表单 / 经纪人邮件", type=["pdf", "docx", "txt", "png", "jpg"])
    submission_text = st.text_area("或粘贴文本", height=150, placeholder="粘贴 ACORD 表单内容或经纪人提交邮件...")
    additional_notes = st.text_area("经纪人备注（可选）", height=60)

    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox("LLM", ["", "openai", "deepseek", "qwen", "anthropic"], key="nb_provider", format_func=lambda x: {"": "默认"}.get(x, x.upper()))
    with col_m:
        model = st.text_input("模型", key="nb_model", placeholder="默认")

    analyze_btn = st.button("🔍 分析提交", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 分析结果")
    if analyze_btn:
        if not uploaded_file and not submission_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 分析中..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else {}
                data = {"text": submission_text, "additional_notes": additional_notes}
                if provider: data["provider"] = provider
                if model: data["model"] = model
                try:
                    resp = requests.post(f"{API_BASE}/api/v1/new-business/analyze", files=files, data=data, timeout=120)
                    if resp.ok and resp.json().get("success"):
                        st.success("✅ 完成")
                        st.markdown(resp.json().get("markdown", ""))
                    else:
                        st.error(resp.json().get("error", str(resp.status_code)))
                except Exception as e:
                    st.error(f"请求失败: {e}")

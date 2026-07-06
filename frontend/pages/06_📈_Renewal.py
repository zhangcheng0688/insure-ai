"""Renewal Page."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="续保管理 — InsureAI", page_icon="📈", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("📈 续保管理 (Renewal)")
st.caption("拉取往年损失记录，准备续保申请，起草定制化续保方案")
st.markdown("---")

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 上传续保资料")
    uploaded_file = st.file_uploader("上传损失记录 / 续保通知", type=["pdf", "docx", "txt"])
    renewal_text = st.text_area("或粘贴文本", height=150, placeholder="粘贴往年损失记录、续保通知内容...")
    expiring_premium = st.text_input("到期保费（可选）", placeholder="$50,000")
    renewal_date = st.text_input("续保日期（可选）", placeholder="2026-12-31")

    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox("LLM", ["", "openai", "deepseek", "qwen", "anthropic"], key="rnw_provider", format_func=lambda x: {"": "默认"}.get(x, x.upper()))
    with col_m:
        model = st.text_input("模型", key="rnw_model", placeholder="默认")

    analyze_btn = st.button("📈 续保分析", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 分析结果")
    if analyze_btn:
        if not uploaded_file and not renewal_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 分析中..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else {}
                data = {"text": renewal_text, "expiring_premium": expiring_premium, "renewal_date": renewal_date}
                if provider: data["provider"] = provider
                if model: data["model"] = model
                try:
                    resp = requests.post(f"{API_BASE}/api/v1/renewal/analyze", files=files, data=data, timeout=120)
                    if resp.ok and resp.json().get("success"):
                        st.success("✅ 完成")
                        st.markdown(resp.json().get("markdown", ""))
                    else:
                        st.error(resp.json().get("error", str(resp.status_code)))
                except Exception as e:
                    st.error(f"请求失败: {e}")

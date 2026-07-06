"""Policy Issuance Page."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="保单出单 — InsureAI", page_icon="📄", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("📄 保单出单 (Policy Issuance)")
st.caption("从条款库生成保单封面页、批单目录和 COI 模板")
st.markdown("---")

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 上传保单信息")
    uploaded_file = st.file_uploader("上传保单条款 / 承保确认", type=["pdf", "docx", "txt"])
    policy_text = st.text_area("或粘贴文本", height=150, placeholder="粘贴保单条款内容...")
    policy_number = st.text_input("保单号（可选）")
    named_insured = st.text_input("被保险人（可选）")

    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox("LLM", ["", "openai", "deepseek", "qwen", "anthropic"], key="pi_provider", format_func=lambda x: {"": "默认"}.get(x, x.upper()))
    with col_m:
        model = st.text_input("模型", key="pi_model", placeholder="默认")

    generate_btn = st.button("📄 生成保单文件", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 生成结果")
    if generate_btn:
        if not uploaded_file and not policy_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 生成中..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else {}
                data = {"text": policy_text, "policy_number": policy_number, "named_insured": named_insured}
                if provider: data["provider"] = provider
                if model: data["model"] = model
                try:
                    resp = requests.post(f"{API_BASE}/api/v1/policy-issuance/generate", files=files, data=data, timeout=120)
                    if resp.ok and resp.json().get("success"):
                        st.success("✅ 完成")
                        st.markdown(resp.json().get("markdown", ""))
                    else:
                        st.error(resp.json().get("error", str(resp.status_code)))
                except Exception as e:
                    st.error(f"请求失败: {e}")

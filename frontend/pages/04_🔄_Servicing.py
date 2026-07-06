"""Servicing Page."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="保单服务 — InsureAI", page_icon="🔄", layout="wide")
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("🔄 保单服务 (Servicing)")
st.caption("起草续保函、COI 申请、中期批单，自动归档输出")
st.markdown("---")

col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 服务请求信息")
    uploaded_file = st.file_uploader("上传相关文件", type=["pdf", "docx", "txt"])
    service_text = st.text_area("服务请求描述", height=150, placeholder="描述需要的保单服务...")
    request_type = st.selectbox("请求类型", ["", "COI Request", "Endorsement", "Policy Change", "Renewal Letter", "Cancellation", "Other"])
    client_name = st.text_input("客户名称（可选）")
    policy_number = st.text_input("保单号（可选）")

    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox("LLM", ["", "openai", "deepseek", "qwen", "anthropic"], key="svc_provider", format_func=lambda x: {"": "默认"}.get(x, x.upper()))
    with col_m:
        model = st.text_input("模型", key="svc_model", placeholder="默认")

    process_btn = st.button("🔄 处理服务请求", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 处理结果")
    if process_btn:
        if not uploaded_file and not service_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 处理中..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} if uploaded_file else {}
                data = {"text": service_text, "request_type": request_type, "client_name": client_name, "policy_number": policy_number}
                if provider: data["provider"] = provider
                if model: data["model"] = model
                try:
                    resp = requests.post(f"{API_BASE}/api/v1/servicing/process", files=files, data=data, timeout=120)
                    if resp.ok and resp.json().get("success"):
                        st.success("✅ 完成")
                        st.markdown(resp.json().get("markdown", ""))
                    else:
                        st.error(resp.json().get("error", str(resp.status_code)))
                except Exception as e:
                    st.error(f"请求失败: {e}")

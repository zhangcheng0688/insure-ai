"""Claims Processing Page — ⭐ Featured Module."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="理赔处理 — InsureAI", page_icon="⚠️", layout="wide")

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("⚠️ 理赔处理 (Claims)")
st.caption("⭐ 主打功能 — FNOL 摘要 + 条款交叉核对 + 理赔裁定备忘录")
st.markdown("---")

# Layout: input left, result right
col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📤 输入理赔信息")

    # File upload
    uploaded_file = st.file_uploader(
        "上传理赔文档",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="支持 FNOL 报告、损失报告、理赔申请表等",
    )

    # Text input
    st.markdown("**或直接粘贴文本：**")
    claim_text = st.text_area(
        "理赔描述 / FNOL 报告内容",
        height=150,
        placeholder="粘贴第一时间出险通知（FNOL）报告内容、损失描述、事故详情等...",
    )

    # Context fields
    st.markdown("**附加信息（可选）：**")
    policy_wording = st.text_area(
        "相关保单条款",
        height=80,
        placeholder="粘贴相关的保单条款、保障范围、除外责任等...",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        claim_type = st.selectbox(
            "理赔类型",
            options=["", "Property Damage", "Liability", "Workers Comp", "Auto", "Professional Liability", "Other"],
        )
    with col_b:
        reserve_authority = st.text_input("准备金权限 ($)", placeholder="如 50000")

    # Provider selection
    col_p, col_m = st.columns(2)
    with col_p:
        provider = st.selectbox(
            "LLM 供应商",
            options=["", "openai", "deepseek", "qwen", "anthropic"],
            format_func=lambda x: {"": "使用默认", "openai": "OpenAI", "deepseek": "DeepSeek", "qwen": "Qwen", "anthropic": "Claude"}.get(x, x),
        )
    with col_m:
        model = st.text_input("模型名称（可选）", placeholder="留空使用默认")

    # Submit
    analyze_btn = st.button("🔍 开始理赔分析", type="primary", use_container_width=True)

with col_result:
    st.subheader("📊 分析结果")

    if analyze_btn:
        if not uploaded_file and not claim_text.strip():
            st.error("请上传文件或输入文本")
        else:
            with st.spinner("🤖 AI 正在分析理赔信息..."):
                # Build form data
                files = {}
                if uploaded_file:
                    files["file"] = (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)

                data = {
                    "text": claim_text,
                    "policy_wording": policy_wording,
                    "claim_type": claim_type,
                }
                if provider:
                    data["provider"] = provider
                if model:
                    data["model"] = model

                try:
                    resp = requests.post(
                        f"{API_BASE}/api/v1/claims/analyze",
                        files=files,
                        data=data,
                        timeout=120,
                    )
                    if resp.ok:
                        result = resp.json()
                        if result.get("success"):
                            st.success("✅ 理赔分析完成")

                            # Display markdown result
                            st.markdown(result.get("markdown", ""))

                            # Download buttons
                            if result.get("pdf_path"):
                                pdf_name = result["pdf_path"].split("/")[-1]
                                st.download_button(
                                    "📥 下载理赔裁定备忘录 (PDF)",
                                    data=open(result["pdf_path"], "rb") if os.path.exists(result["pdf_path"]) else b"",
                                    file_name=pdf_name,
                                    mime="application/pdf",
                                )

                            # Also allow downloading markdown
                            st.download_button(
                                "📝 下载 Markdown 原文",
                                data=result.get("markdown", ""),
                                file_name="claim_analysis.md",
                                mime="text/markdown",
                            )
                        else:
                            st.error(f"分析失败：{result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"后端错误: {resp.status_code} — {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接后端服务，请确认服务已启动 (http://localhost:8000)")
                except Exception as e:
                    st.error(f"请求失败: {e}")

st.markdown("---")
st.info("""
**💡 使用示例**：
1. 上传一份 FNOL 报告 PDF 或粘贴事故描述
2. 可选：粘贴相关保单条款以进行交叉核对
3. 点击"开始理赔分析"
4. AI 会自动生成：FNOL 摘要、保单条款对照表、保障范围分析、准备金建议、理赔裁定备忘录
""")

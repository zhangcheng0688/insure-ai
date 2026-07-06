"""Settings Page — LLM Configuration."""
import streamlit as st
import requests
import os

st.set_page_config(page_title="Settings — InsureAI", page_icon="⚙️", layout="wide")

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

st.title("⚙️ 系统设置")
st.caption("配置 LLM 模型和其他系统参数")

# --- LLM Provider Settings ---
st.subheader("🔑 LLM 模型配置")

# Fetch current providers from backend
try:
    resp = requests.get(f"{API_BASE}/api/v1/settings/providers", timeout=5)
    if resp.ok:
        data = resp.json()
        providers = data.get("providers", [])
    else:
        providers = []
except Exception:
    providers = []

# Fallback if backend not available
if not providers:
    providers = [
        {"name": "openai", "label": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], "configured": False},
        {"name": "deepseek", "label": "DeepSeek", "models": ["deepseek-chat", "deepseek-reasoner"], "configured": False},
        {"name": "qwen", "label": "Qwen (通义千问)", "models": ["qwen-max", "qwen-plus", "qwen-turbo"], "configured": False},
        {"name": "anthropic", "label": "Anthropic Claude", "models": ["claude-sonnet-5", "claude-opus-4-8"], "configured": False},
    ]

# API Keys
st.markdown("### API Keys")

openai_key = st.text_input(
    "OpenAI API Key",
    type="password",
    value=os.environ.get("OPENAI_API_KEY", ""),
    help="从 https://platform.openai.com/api-keys 获取",
)
openai_base = st.text_input(
    "OpenAI Base URL",
    value=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    help="自定义 API 端点（如代理地址）",
)

deepseek_key = st.text_input(
    "DeepSeek API Key",
    type="password",
    value=os.environ.get("DEEPSEEK_API_KEY", ""),
    help="从 https://platform.deepseek.com/api_keys 获取",
)

qwen_key = st.text_input(
    "Qwen (通义千问) API Key",
    type="password",
    value=os.environ.get("QWEN_API_KEY", ""),
    help="从 https://dashscope.console.aliyun.com/apiKey 获取",
)

anthropic_key = st.text_input(
    "Anthropic API Key",
    type="password",
    value=os.environ.get("ANTHROPIC_API_KEY", ""),
)

st.markdown("---")
st.subheader("🎯 默认模型选择")

provider_names = [p["name"] for p in providers]
default_provider = st.selectbox(
    "默认 LLM 供应商",
    options=provider_names,
    index=0,
    format_func=lambda x: {"openai": "OpenAI", "deepseek": "DeepSeek", "qwen": "Qwen (通义千问)", "anthropic": "Anthropic Claude"}.get(x, x),
)

# Get models for selected provider
selected_provider = next((p for p in providers if p["name"] == default_provider), None)
if selected_provider:
    default_model = st.selectbox("默认模型", options=selected_provider["models"])
else:
    default_model = st.text_input("模型名称", "gpt-4o")

if st.button("💾 保存配置", type="primary", use_container_width=True):
    # Set environment variables (runtime only)
    os.environ["OPENAI_API_KEY"] = openai_key
    os.environ["DEEPSEEK_API_KEY"] = deepseek_key
    os.environ["QWEN_API_KEY"] = qwen_key
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key

    # Try to update backend
    try:
        resp = requests.post(
            f"{API_BASE}/api/v1/settings/update",
            json={"provider": default_provider, "model": default_model},
            timeout=5,
        )
        if resp.ok:
            st.success(f"✅ 配置已保存！默认使用 {default_provider}/{default_model}")
        else:
            st.warning("⚠️ 后端保存失败，但环境变量已更新")
    except Exception:
        st.warning("⚠️ 后端不可达，配置仅保存在当前会话中")

st.markdown("---")
st.subheader("📊 系统状态")

col1, col2 = st.columns(2)
with col1:
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=3)
        if resp.ok:
            st.success("✅ 后端服务运行中")
        else:
            st.error("❌ 后端服务异常")
    except Exception:
        st.error("❌ 无法连接后端服务")

with col2:
    try:
        resp = requests.get(f"{API_BASE}/api/v1/agents", timeout=3)
        if resp.ok:
            agents = resp.json().get("agents", [])
            st.metric("可用 Agent 数", len(agents))
        else:
            st.warning("N/A")
    except Exception:
        st.warning("N/A")

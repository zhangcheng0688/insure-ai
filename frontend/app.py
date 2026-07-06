"""InsureAI — Streamlit Main Application."""
import streamlit as st

st.set_page_config(
    page_title="InsureAI — 保险 AI 全流程平台",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar ---
st.sidebar.title("🛡️ InsureAI")
st.sidebar.caption("保险 AI 全流程工具箱")
st.sidebar.markdown("---")

# Navigation
st.sidebar.markdown("### 📂 保险业务环节")

pages = {
    "🏠 首页": "app.py",
    "📋 新业务受理": "pages/01_📋_New_Business.py",
    "🔍 核保分析": "pages/02_🔍_Underwriting.py",
    "📄 保单出单": "pages/03_📄_Policy_Issuance.py",
    "🔄 保单服务": "pages/04_🔄_Servicing.py",
    "⚠️ 理赔处理": "pages/05_⚠️_Claims.py",
    "📈 续保管理": "pages/06_📈_Renewal.py",
}

st.sidebar.markdown("### 🛠️ 工具")
st.sidebar.page_link("pages/07_📝_Intake_Builder.py", label="📝 信息采集表单")
st.sidebar.page_link("pages/09_📚_Knowledge_Base.py", label="📚 知识库管理")
st.sidebar.page_link("pages/08_⚙️_Settings.py", label="⚙️ 系统设置")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Version**: 0.1.0")
st.sidebar.markdown("[GitHub](https://github.com) · [文档](https://github.com)")

# --- Main Page ---
st.title("🛡️ InsureAI — 保险 AI 全流程平台")
st.markdown("""
### 用 AI 自动化保险文档处理，覆盖保单全生命周期

上传文档、选择环节、一键生成专业的保险文档。每个模块独立可用，像工具箱一样即开即用。
""")

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("支持环节", "6", "新业务→续保")
with col2:
    st.metric("LLM 供应商", "4+", "OpenAI/DeepSeek/Qwen/Claude")
with col3:
    st.metric("输出格式", "3", "Markdown/PDF/DOCX")
with col4:
    st.metric("零门槛启动", "1 行命令", "docker compose up")

st.markdown("---")

# Quick start guide
st.subheader("🚀 快速开始")

st.markdown("""
#### 3 步完成第一次 AI 保险文档处理：

1. **⚙️ 配置 LLM** → 前往 **系统设置** 页面，填入你的 API Key 和模型选择
2. **📤 上传文档** → 选择一个业务环节，上传你的保险文档（PDF/DOCX/图片/文本）
3. **📥 下载结果** → AI 自动分析并生成专业的保险文档，支持 PDF/DOCX 下载
""")

# Feature cards
st.subheader("💡 六大业务环节")

features = [
    ("📋 **新业务受理**", "读取 ACORD 表单和经纪人提交邮件，自动提取风险信息，填充核保工作表。"),
    ("🔍 **核保分析**", "分析损失记录，检查保险公司承保偏好，撰写带条款引用的核保备忘录。"),
    ("📄 **保单出单**", "从条款库生成保单封面页、批单目录和保险凭证（COI）模板。"),
    ("🔄 **保单服务**", "起草续保函、COI 申请、中期批单，自动归档输出文件。"),
    ("⚠️ **理赔处理** ⭐", "摘要 FNOL 报告，交叉核对保单条款，撰写理赔裁定备忘录。**最星的方向！**"),
    ("📈 **续保管理**", "拉取往年损失记录，准备续保申请，起草定制化续保方案。"),
]

for title, desc in features:
    st.markdown(f"##### {title}")
    st.markdown(f"{desc}")
    st.markdown("")

st.markdown("---")
st.info("💡 **提示**：推荐从左侧边栏选择一个环节开始体验。每个环节都可以独立使用，不需要全部配置。")

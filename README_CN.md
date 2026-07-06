# 🛡️ InsureAI — AI 驱动的保险文档全流程处理平台

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)

**InsureAI** 是一个开源的保险行业 AI 协同工作平台。它自动化处理保险全生命周期的文档工作——从新业务提交到理赔裁定再到续保管理。

受 [Kuse.ai](https://kuse.ai) 启发，为开源社区而生。

---

## ✨ 核心功能

- **6 大保险业务环节** — 新业务受理 → 核保分析 → 保单出单 → 保单服务 → 理赔处理 → 续保管理
- **多模型 LLM 支持** — OpenAI、DeepSeek、通义千问、Anthropic Claude — 界面一键切换
- **文档自动生成** — 核保备忘录、理赔裁定报告、续保方案、COI 模板
- **结构化信息采集** — 在线表单构建器，替代非结构化邮件往返
- **多格式输出** — Markdown / PDF / DOCX
- **一行命令启动** — `docker compose up` 即可运行

## 🚀 快速开始

### 环境要求
- Docker & Docker Compose
- 或：Python 3.11+ 配合 pip

### Docker 启动（推荐）

```bash
git clone https://github.com/YOUR_USERNAME/insure-ai.git
cd insure-ai
cp .env.example .env
# 编辑 .env 填入你的 API Key
docker compose up
```

- **前端界面**: http://localhost:8501
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 本地开发

```bash
pip install -r backend/requirements.txt

# 终端 1: 启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 终端 2: 启动前端
streamlit run frontend/app.py
```

## 📖 使用方法

### 三步完成第一次 AI 保险文档处理

1. **⚙️ 配置 LLM** — 前往系统设置页面，填入 API Key，选择模型
2. **📤 上传文档** — 选择一个业务环节，上传保险文档（PDF/DOCX/图片/文本）
3. **📥 下载结果** — AI 自动分析并生成专业保险文档

### 快速演示：理赔处理

```bash
# 使用示例数据
# 1. 打开 ⚠️ 理赔处理页面
# 2. 上传 sample_data/fnol_sample.txt 作为理赔报告
# 3. 上传 sample_data/policy_sample.txt 作为保单条款
# 4. 点击"开始理赔分析" → 获取完整理赔裁定备忘录
```

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit 前端界面                  │
│  6 个业务环节页面 + 表单构建器 + 系统设置             │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────┐
│                  FastAPI 后端服务                     │
│  /api/v1/claims | underwriting | renewal | ...      │
│  LiteLLM 适配层 → OpenAI / DeepSeek / Qwen / Claude │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               AI Agent 层 (LangGraph)                │
│  理赔Agent | 核保Agent | 续保Agent | ...            │
│  System Prompt → LLM → 结构化输出                     │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│           文档生成引擎 (Jinja2 + WeasyPrint)          │
│  Markdown → PDF / DOCX                              │
└─────────────────────────────────────────────────────┘
```

## 🎯 六大 Agent 说明

| 环节 | 功能描述 | 核心输出 |
|---|---|---|
| 📋 **新业务受理** | 读取 ACORD 表单，提取风险信息，填充核保工作表 | 提交分析报告 |
| 🔍 **核保分析** | 分析损失记录，检查承保偏好，撰写核保备忘录 | 核保备忘录 |
| 📄 **保单出单** | 生成保单封面页、批单目录、COI 模板 | 保单文件包 |
| 🔄 **保单服务** | 起草续保函、COI 申请、中期批单 | 服务函件 |
| ⚠️ **理赔处理** ⭐ | FNOL 摘要、条款交叉核对、裁定备忘录 | 理赔裁定报告 |
| 📈 **续保管理** | 往年损失对比、续保方案、保费分析 | 续保建议书 |

## 🔧 支持的 LLM

| 供应商 | 可用模型 | 配置方式 |
|---|---|---|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo | 设置 `OPENAI_API_KEY` |
| DeepSeek | deepseek-chat, deepseek-reasoner | 设置 `DEEPSEEK_API_KEY` |
| 通义千问 | qwen-max, qwen-plus, qwen-turbo | 设置 `QWEN_API_KEY` |
| Anthropic | claude-sonnet-5, claude-opus-4-8 | 设置 `ANTHROPIC_API_KEY` |

## 🤝 参与贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**急需贡献的方向：**
- [ ] 更多行业专用文档模板
- [ ] 更多 LLM 供应商支持
- [ ] ACORD 表单解析优化
- [ ] 邮件集成（Gmail/Outlook）
- [ ] 测试覆盖率

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE)

## ⚠️ 免责声明

本软件仅供教育和提升工作效率之用。AI 生成的保险文档在使用前必须经过持牌保险专业人士审查。作者对基于 AI 生成内容所做的决策不承担任何责任。

---

⭐ **给个 Star** 支持一下！为保险行业开源社区而建。

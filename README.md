# 🛡️ InsureAI — AI-Powered Insurance Document Processing Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

**InsureAI** is an open-source AI coworker for the insurance industry. It automates document-heavy work across the full policy lifecycle — from new business submissions through claims adjudication and renewals.

Inspired by [Kuse.ai](https://kuse.ai), built for the open-source community.

> 📖 [中文文档](README_CN.md)

---

## ✨ Features

- **6 Insurance Lifecycle Stages** — New Business → Underwriting → Policy Issuance → Servicing → Claims → Renewal
- **Multi-Model LLM Support** — OpenAI, DeepSeek, Qwen, Anthropic Claude — switch via Settings UI
- **Document Generation** — Auto-generate underwriting memos, claim adjudication reports, renewal proposals, COI templates
- **Structured Intake Pages** — Build web forms to replace unstructured email back-and-forth
- **Multi-Format Output** — Markdown, PDF, DOCX
- **One-Command Start** — `docker compose up` and you're ready

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Or: Python 3.11+ with pip

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/insure-ai.git
cd insure-ai

# Configure your LLM API keys
cp .env.example .env
# Edit .env with your API keys

# Start everything
docker compose up
```

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development

```bash
pip install -r backend/requirements.txt

# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py

# Terminal 3: Celery Worker (optional)
celery -A backend.app.tasks worker --loglevel=info
```

## 📖 Usage

### 3 Steps to Your First AI Insurance Document

1. **⚙️ Configure LLM** — Go to Settings page, enter your API key, select provider & model
2. **📤 Upload Document** — Pick an insurance stage, upload your document (PDF/DOCX/image/text)
3. **📥 Download Result** — AI analyzes & generates professional insurance documents

### Quick Demo: Claims Processing

```bash
# Using the sample data
# 1. Go to ⚠️ Claims page
# 2. Upload sample_data/fnol_sample.txt as the claim report
# 3. Upload sample_data/policy_sample.txt as the policy wording
# 4. Click "Analyze" → Get a complete claim adjudication memo
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit Frontend                 │
│  6 Insurance Stage Pages + Intake Builder + Settings│
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                     │
│  /api/v1/claims | underwriting | renewal | ...      │
│  LiteLLM Adapter → OpenAI / DeepSeek / Qwen / Claude│
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               AI Agents (LangGraph)                  │
│  ClaimsAgent | UwAgent | RenewalAgent | ...         │
│  System Prompts → LLM → Structured Output           │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│           Document Engine (Jinja2 + WeasyPrint)      │
│  Markdown → PDF / DOCX                              │
└─────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
insure-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # 6 AI agents (one per insurance stage)
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Config, LLM adapter
│   │   ├── utils/           # PDF parser, template engine
│   │   └── main.py          # FastAPI entry point
│   └── templates/           # Jinja2 document templates
├── frontend/
│   ├── app.py               # Streamlit main
│   └── pages/               # 8 pages (6 stages + intake + settings)
├── sample_data/             # Example documents for testing
├── docker-compose.yml
└── README.md
```

## 🎯 Available Agents

| Stage | Description | Key Output |
|---|---|---|
| 📋 **New Business** | ACORD form reading, risk extraction, underwriting worksheet | Submission Analysis |
| 🔍 **Underwriting** | Loss run analysis, carrier appetite, underwriting memo | UW Memo |
| 📄 **Policy Issuance** | Dec pages, endorsement schedules, COI templates | Policy Docs |
| 🔄 **Servicing** | Renewal letters, COI requests, mid-term endorsements | Correspondence |
| ⚠️ **Claims** ⭐ | FNOL summary, policy cross-reference, adjudication memo | Adjudication Report |
| 📈 **Renewal** | Prior-year loss runs, renewal apps, tailored proposals | Renewal Proposal |

## 🔧 Supported LLM Providers

| Provider | Models | Setup |
|---|---|---|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo | Set `OPENAI_API_KEY` |
| DeepSeek | deepseek-chat, deepseek-reasoner | Set `DEEPSEEK_API_KEY` |
| Qwen (通义千问) | qwen-max, qwen-plus, qwen-turbo | Set `QWEN_API_KEY` |
| Anthropic | claude-sonnet-5, claude-opus-4-8 | Set `ANTHROPIC_API_KEY` |

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**High-priority contributions:**
- [ ] More document templates (industry-specific)
- [ ] Additional LLM provider integrations
- [ ] Improved ACORD form parsing
- [ ] Email integration (Gmail/Outlook)
- [ ] Test coverage

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This software is provided for educational and productivity purposes. AI-generated insurance documents should always be reviewed by a licensed insurance professional before use. The authors assume no liability for decisions made based on AI-generated content.

---

⭐ **Star this repo** if you find it useful! Built for the insurance community, by the open-source community.

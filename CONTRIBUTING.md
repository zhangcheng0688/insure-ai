# Contributing to InsureAI

Thank you for your interest in contributing! 🎉

## How to Contribute

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest backend/tests/`
5. Commit with descriptive message
6. Push and create a Pull Request

## Development Setup

```bash
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload
# In another terminal:
streamlit run frontend/app.py
```

## Project Conventions

- **Python**: Type hints, docstrings, async where possible
- **Agents**: Extend `BaseInsuranceAgent`, define `system_prompt` and `build_user_prompt()`
- **Templates**: Jinja2 files in `backend/templates/`
- **API**: Follow existing pattern in `backend/app/api/`

## Priority Areas

1. **More document templates** — Industry-specific formats (marine, construction, cyber, etc.)
2. **Additional LLM providers** — Add to `PROVIDER_MODELS` in `core/llm.py`
3. **Frontend improvements** — Better UX, dark mode, mobile support
4. **Tests** — Unit tests for agents, integration tests for API
5. **Internationalization** — More language support beyond English/Chinese

## Questions?

Open an issue or start a discussion!

# Instructions — Python Backend

## Context
Python backend.

## Stack
- Language: Python 3.11+
- Framework: FastAPI (adapt: Django, Flask, etc.)
- Database: PostgreSQL (adapt to your project)
- ORM: SQLAlchemy / Django ORM
- Tests: pytest
- Linting: ruff
- Type checking: mypy

## Commands
- `uvicorn app.main:app --reload` — Start in development
- `pytest` — Run the tests
- `ruff check .` — Check linting
- `mypy .` — Check types

## Conventions
- Type hints on all public functions
- Google-style docstrings on public functions/classes
- Virtual env required (venv or poetry)
- Requirements pinned in `requirements.txt` or `pyproject.toml`
- Pydantic for data validation
- Async when relevant (I/O bound)
- No `print()` — use `logging`

## Security
- Never hardcode secrets — use environment variables
- Validate inputs with Pydantic
- Parameterized queries (SQLAlchemy, Django ORM — never SQL f-strings)
- Scan dependencies regularly (pip-audit)
- Log errors, never sensitive data

## Structure
```
src/
├── api/           # Routes/endpoints
├── models/        # Data models
├── services/      # Business logic
├── repositories/  # Data access
└── utils/         # Utilities
tests/
├── unit/
└── integration/
```

# to-do-list

Minimal task tracking API with planned MCP tool integration.

## Tech Stack

### Languages
- Python 3.12

### Frameworks & Core Libraries
- FastAPI (REST API)
- Pydantic v2 (validation & schemas)
- SQLAlchemy 2.0 (ORM / DB access)
- Alembic (migrations)
- httpx (HTTP client & tests)
- FastMCP (MCP tools integration)

### Database
- PostgreSQL (primary target)
- SQLite (local / initial development)

### Testing & Quality
- pytest
- coverage (pytest-cov)
- Ruff (lint)
- Black (format)

### Supporting
- Uvicorn (ASGI server)
- Poetry or Hatch (dependency management)
- Pre-commit (hooks)

## Project Structure
```text
to_do_list/
  pyproject.toml
  README.md
  .gitignore
  .env.example

  app/
    core/
      config.py
      logging.py
    db/
      base.py
      session.py
      models/
        task.py
      migrations/
    schemas/
      task.py
      common.py
      error.py
    services/
      tasks.py
    api/
      deps.py
      routers/
        tasks.py
      main.py
    mcp_tools/
      __init__.py
      list_tasks.py
      create_task.py
      client.py

  tests/
    conftest.py
    integration/
      test_tasks_api.py
    unit/
      test_tasks_service.py
      test_task_validation.py
    factories/
      task_factory.py

  scripts/
    seed_tasks.py
    generate_example_data.py
```

## MCP Tools (Planned)
- list_tasks (wraps GET /v1/tasks)
- create_task (wraps POST /v1/tasks)

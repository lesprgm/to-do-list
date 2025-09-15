# to-do-list

## MCP tools for Claude Desktop

This repo ships a minimal MCP server that exposes two tools over stdio so Claude Desktop (and the MCP CLI) can interact with your API:

- List Tasks → calls GET `/v1/tasks` with optional filters and returns structured JSON.
- Create Task → calls POST `/v1/tasks` and returns the created task JSON.

Server code is at `app/mcp_tools/server.py` using `from mcp.server.fastmcp import FastMCP`.

### Install (MCP CLI and runtime)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install "mcp[cli]" requests
```

Start your API in one terminal:

```bash
uvicorn app.api.main:app --reload
```

Run the MCP server in another terminal:

```bash
python app/mcp_tools/server.py
```

By default it targets `http://127.0.0.1:8000`; override with `TODO_API_BASE_URL`.

### Try via MCP CLI (optional)

List available tools:

```bash
mcp tools stdio -- python app/mcp_tools/server.py
```

Call Create Task:

```bash
mcp call stdio -- python app/mcp_tools/server.py \
  "Create Task" \
  '{"title":"Buy milk","priority":"high","due_date":"2025-09-15T12:00:00Z","tags":["groceries"]}'
```

Expected JSON (201):

```json
{
  "ok": true,
  "status": 201,
  "url": "http://127.0.0.1:8000/v1/tasks/",
  "data": {
    "id": 1,
    "title": "Buy milk",
    "description": null,
    "status": "todo",
    "priority": "high",
    "tags": ["groceries"],
    "due_date": "2025-09-15T12:00:00Z",
    "created_at": "2025-09-15T10:00:00Z",
    "updated_at": "2025-09-15T10:00:00Z"
  }
}
```

List Tasks:

```bash
mcp call stdio -- python app/mcp_tools/server.py "List Tasks"
```

### Claude Desktop config (mcpServers)

Add an entry for the MCP server in Claude Desktop’s config JSON.

macOS (~/Library/Application Support/Claude/claude_desktop_config.json):

```json
{
  "mcpServers": {
    "to-do-list": {
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/your/repo/app/mcp_tools/server.py"],
      "env": {
        "TODO_API_BASE_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

Windows (C:\\Users\\<you>\\AppData\\Roaming\\Claude\\claude_desktop_config.json):

```json
{
  "mcpServers": {
    "to-do-list": {
      "command": "C:\\\Python\\\python.exe",
      "args": ["C:\\\absolute\\\path\\\to\\\repo\\\app\\\mcp_tools\\\server.py"],
      "env": {
        "TODO_API_BASE_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

After saving, restart Claude Desktop and run “List available actions”. You should see both tools (List Tasks, Create Task). If your API isn’t running, the tools will return a 502/connection error.

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

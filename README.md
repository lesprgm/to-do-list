# to-do-list

Minimal FastAPI-based tasks API with SQLite and an MCP server so Claude Desktop or the MCP CLI can create/list/update/delete tasks.

## Quick start

1) Create and activate a virtualenv, then install deps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Run the API

```bash
uvicorn app.api.main:app --reload
```

The API will be available at http://127.0.0.1:8000.

3) Run the MCP server (optional, for tools)

```bash
# In a second terminal (API must be running)
source .venv/bin/activate
export TODO_API_BASE_URL="http://127.0.0.1:8000"
python app/mcp_tools/server.py
```

Or via MCP CLI:

```bash
pip install -U "mcp[cli]" requests
mcp tools stdio -- python app/mcp_tools/server.py
# or the dev inspector
mcp dev "$(pwd)/app/mcp_tools/server.py"
```

## How to run tests

From the project root (recommended):

```bash
source .venv/bin/activate
pytest -q
```

If you prefer not to rely on the current working directory, set PYTHONPATH to the repo root:

```bash
PYTHONPATH="$PWD" pytest -q
```

Run a single file or a single test:

```bash
pytest -q tests/unit/test_create_task.py
pytest -q tests/unit/test_create_task.py::test_create_task_happy_path
```

Tip: If `pytest -q` fails only when run from a subfolder, either run it from the repo root or add this to a `pytest.ini`:

```ini
[pytest]
addopts = -q --import-mode=prepend
testpaths = tests
```

## API overview

- POST `/v1/tasks/` → Create a task
- GET `/v1/tasks/` → List tasks
  - Optional filters: `task_id` (int), `status` (todo|in_progress|done), `priority` (low|med|high)
- PATCH `/v1/tasks/{task_id}` → Partial update
- DELETE `/v1/tasks/{task_id}` → Delete

Example create:

```bash
curl -sS -X POST http://127.0.0.1:8000/v1/tasks/ \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Buy milk",
    "priority": "high",
    "tags": ["groceries"],
    "due_date": "2025-09-15T12:00:00Z"
  }'
```

## MCP tools for Claude Desktop

The MCP server at `app/mcp_tools/server.py` exposes four tools over stdio:

- List Tasks → GET `/v1/tasks` with optional filters
- Create Task → POST `/v1/tasks`
- Update Task → PATCH `/v1/tasks/{task_id}`
- Delete Task → DELETE `/v1/tasks/{task_id}`

### Try via MCP CLI

```bash
export TODO_API_BASE_URL="http://127.0.0.1:8000"
mcp tools stdio -- python app/mcp_tools/server.py

# Create
mcp call stdio -- python app/mcp_tools/server.py \
  "Create Task" \
  '{"title":"Buy milk","priority":"high","due_date":"2025-09-15T12:00:00Z","tags":["groceries"]}'

# List
mcp call stdio -- python app/mcp_tools/server.py "List Tasks"
```

### Claude Desktop config (mcpServers)

macOS (~/.config path varies by version; common path shown):

```json
{
  "mcpServers": {
    "to-do-list": {
      "command": "/usr/bin/python3",
      "args": ["/absolute/path/to/repo/app/mcp_tools/server.py"],
      "env": { "TODO_API_BASE_URL": "http://127.0.0.1:8000" }
    }
  }
}
```

Restart Claude Desktop to pick up changes. Use “List available actions” to see the tools.

## Project structure

```text
.
├─ requirements.txt
├─ README.md
├─ app/
│  ├─ api/
│  │  ├─ main.py
│  │  ├─ deps.py
│  │  └─ routers/
│  │     └─ tasks.py
│  ├─ db/
│  │  ├─ __init__.py
│  │  └─ models/
│  │     ├─ __init__.py
│  │     └─ task.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ task.py
│  │  └─ error.py
│  ├─ services/
│  │  └─ tasks.py
│  └─ mcp_tools/
│     └─ server.py
├─ tests/
│  └─ unit/
│     ├─ test_create_task.py
│     ├─ test_list_task.py
│     ├─ test_update_task.py
│     └─ test_delete_task.py
└─ scripts/
```

## Troubleshooting

- `pytest -q` fails but `PYTHONPATH="$PWD" pytest -q` works:
  - Make sure you run from the repo root, or add the `pytest.ini` above to force root-prepend import mode.
- MCP CLI shows 5xx or connection errors:
  - Ensure the API is running and `TODO_API_BASE_URL` is set correctly.
- PATCH returns 405:
  - Confirm you’re calling `/v1/tasks/{id}` with JSON body (not query params).


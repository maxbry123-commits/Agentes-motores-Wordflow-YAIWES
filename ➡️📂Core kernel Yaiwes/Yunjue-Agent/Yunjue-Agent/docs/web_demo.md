# Web Demo Quick Guide

## Configuration

Ensure you have completed the repository **Quick Start** setup (virtualenv, dependencies, `.env`, and `conf.yaml`).

The `web_demo` depends on model settings in `conf.yaml`. At minimum, fill in these model blocks with valid `base_url`, `model`, and `api_key`:

- `BASIC_MODEL`
- `SUMMARIZE_MODEL`
- `TOOL_ANALYZE_MODEL`

If your workflow uses vision capabilities, also configure:

- `VISION_MODEL`

Optional fields (as needed): `temperature`, `token_limit`, `timeout`, `max_retries`.

## Run Web Demo

From the project root:

```bash
source .venv/bin/activate
uvicorn web_demo.app:app --app-dir . --port 8000
```

After startup:

- UI: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`

API endpoints:

- `POST /chat`
- `POST /chat/stream` (SSE streaming)

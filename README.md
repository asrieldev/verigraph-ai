# VeriGraph AI

VeriGraph AI is a context-aware software engineering review and verification MVP. It ingests a public GitHub repository, builds a file/function/import graph, coordinates specialized review stages, presents traceable findings and diffs, and records verification outcomes in a live dark dashboard.

The project is deliberately honest about capability: this MVP runs in **Demo Mode** using deterministic security rules and a bundled vulnerable sample. Supplying an API key does not relabel deterministic output as AI-generated, and simulated output is never presented as an external-tool result.

## Quick start

### Local development

Requirements: Node 20+, npm 10+, and Python 3.11–3.13.

```bash
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -e "apps/api[dev]"
npm install
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

In a second terminal:

```bash
npm run dev
```

Open <http://localhost:5173>, keep the bundled sample URL, and choose **Analyze**.

### Docker Compose

```bash
copy .env.example .env
docker compose up --build
```

Dashboard: <http://localhost:5173> · API docs: <http://localhost:8000/docs> · health: <http://localhost:8000/health>

## Verification commands

```bash
npm run lint
npm run typecheck
npm run build
pytest -q apps/api/tests
ruff check apps/api
mypy apps/api/app
docker compose config --quiet
```

## Configuration

See `.env.example`. `OPENAI_API_KEY` is optional and never sent to the browser. `DEMO_MODE=true` makes the deterministic mode explicit. Repository and file size limits are enforced during indexing.

## Demo flow

1. Analyze `https://github.com/verigraph-ai/demo` (a reserved identifier for the bundled fixture).
2. Watch the run status, four agent stages, context graph, traces, and metrics update.
3. Select the high-severity SQL injection finding to inspect exact evidence.
4. Review its unified diff, approve it, and observe the isolated deterministic verification result.
5. Download the Markdown report.

## What is implemented

- URL validation, shallow safe clone, bounded source indexing, and durable run history
- Python AST function graph plus cross-language import discovery
- Typed findings with severity, confidence, location, evidence, status, and optional unified diff
- Four visible agent stages and LangGraph-ready backend dependencies
- REST API, WebSocket run stream, responsive React Flow dashboard, filters, traces, and reports
- Explicit deterministic demo analysis, patch review/approval, and verification records
- PostgreSQL/pgvector and Redis/Celery infrastructure, restricted containers, CI, tests, and docs

## Current limitations

- The zero-configuration MVP persists runs in an atomic JSON store; the PostgreSQL schema is provisioned for the next persistence adapter.
- AI-backed model calls and embedding generation are not made automatically merely because a key exists; deterministic analysis remains the supported MVP path.
- Semgrep/pytest are included in the sandbox image but arbitrary repository execution is not exposed through the API until a hardened container runtime is configured.
- Import resolution is intentionally conservative and strongest for Python/TypeScript-style imports.
- Patch approval verifies and records the proposal but does not mutate or push the source repository.

See [architecture details](docs/architecture.md) for trust boundaries and production hardening priorities.


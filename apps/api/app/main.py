import asyncio

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .config import settings
from .models import CreateRun, Run
from .service import RunService
from .store import RunStore

app = FastAPI(title="VeriGraph AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
store = RunStore(settings.data_dir / "runs.json")
service = RunService(store)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "demo"}


@app.post("/api/runs", response_model=Run, status_code=202)
def create_run(data: CreateRun, tasks: BackgroundTasks) -> Run:
    try:
        run = service.create(data)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    tasks.add_task(service.execute, run.id)
    return run


@app.get("/api/runs", response_model=list[Run])
def list_runs() -> list[Run]:
    return store.list()


@app.get("/api/runs/{run_id}", response_model=Run)
def get_run(run_id: str) -> Run:
    run = store.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run


@app.post("/api/runs/{run_id}/findings/{finding_id}/approve", response_model=Run)
def approve_patch(run_id: str, finding_id: str) -> Run:
    try:
        return service.approve(run_id, finding_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/api/runs/{run_id}/report", response_class=PlainTextResponse)
def report(run_id: str) -> str:
    run = get_run(run_id)
    lines = [
        "# VeriGraph AI Analysis Report",
        f"Repository: {run.repository_url}",
        f"Status: {run.status}",
        f"Mode: {'Demo' if run.demo_mode else 'AI'}",
        "",
        "## Findings",
    ]
    lines += [
        f"- [{x.severity.upper()}] {x.title} — {x.file}:{x.line} ({x.status})\n  {x.explanation}\n  Evidence: `{x.evidence}`" for x in run.findings
    ]
    lines += ["", "## Verification"] + [f"- {'PASS' if x.passed else 'FAIL'} {x.name}: {x.output}" for x in run.verification]
    return "\n".join(lines)


@app.websocket("/ws/runs/{run_id}")
async def run_events(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            run = store.get(run_id)
            if not run:
                await websocket.send_json({"error": "not found"})
                return
            await websocket.send_json(run.model_dump(mode="json"))
            if run.status in {"completed", "failed"}:
                return
            await asyncio.sleep(0.7)
    except WebSocketDisconnect:
        return

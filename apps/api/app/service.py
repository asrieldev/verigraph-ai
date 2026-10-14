import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .analyzer import analyze, verify_patch_in_copy
from .config import settings
from .ingestion import clone_repository, index_repository, validate_repository_url
from .models import AgentState, CreateRun, Run, Trace
from .orchestration import AGENTS, agent_order
from .sample import create_sample
from .store import RunStore


class RunService:
    def __init__(self, store: RunStore):
        self.store = store

    def create(self, data: CreateRun) -> Run:
        validate_repository_url(data.repository_url)
        now = datetime.now(UTC)
        run = Run(
            id=str(uuid4()),
            repository_url=data.repository_url,
            demo_mode=not bool(settings.openai_api_key),
            created_at=now,
            updated_at=now,
            agents=[AgentState(name=x) for x in AGENTS],
            trace=[Trace(at=now, message="Analysis run accepted", kind="start")],
        )
        return self.store.save(run)

    def execute(self, run_id: str) -> None:
        run = self.store.get(run_id)
        if not run:
            return
        started = time.perf_counter()
        run.status = "running"
        run.trace.append(Trace(at=datetime.now(UTC), message="Repository ingestion started"))
        self.store.save(run)
        try:
            root = Path("workspace") / run.id
            if run.repository_url == "https://github.com/verigraph-ai/demo":
                create_sample(root)
            else:
                clone_repository(run.repository_url, root)
            files, nodes, edges = index_repository(root)
            run.graph = {"nodes": nodes, "edges": edges}
            run.metrics.files = len(files)
            run.metrics.nodes = len(nodes)
            run.trace.append(
                Trace(
                    at=datetime.now(UTC),
                    message=f"Indexed {len(files)} files and built dependency graph",
                    kind="graph",
                )
            )
            for index, agent_name in enumerate(agent_order()):
                agent = next(item for item in run.agents if item.name == agent_name)
                agent.status = "running"
                self.store.save(run)
                begin = time.perf_counter()
                if index == 0:
                    findings, checks = analyze(files, nodes, edges)
                    run.findings = findings
                    run.verification = checks
                agent.latency_ms = max(1, int((time.perf_counter() - begin) * 1000))
                agent.status = "completed"
                run.trace.append(Trace(at=datetime.now(UTC), message=f"{agent.name} completed", kind="agent"))
            run.status = "completed"
            run.metrics.findings = len(run.findings)
            run.metrics.latency_ms = int((time.perf_counter() - started) * 1000)
            run.metrics.tokens = 0
            run.updated_at = datetime.now(UTC)
            self.store.save(run)
        except Exception as exc:
            run.status = "failed"
            run.updated_at = datetime.now(UTC)
            run.trace.append(Trace(at=run.updated_at, message=str(exc), kind="error"))
            self.store.save(run)

    def approve(self, run_id: str, finding_id: str) -> Run:
        run = self.store.get(run_id)
        if not run:
            raise KeyError("Run not found")
        finding = next((x for x in run.findings if x.id == finding_id), None)
        if not finding:
            raise KeyError("Finding not found")
        if not finding.patch:
            raise ValueError("This finding has no proposed patch")
        result = verify_patch_in_copy(finding)
        finding.status = "fixed" if result.passed else "open"
        run.verification.append(result)
        run.trace.append(
            Trace(
                at=datetime.now(UTC),
                message=f"Patch approved and verified for {finding.file}",
                kind="verify",
            )
        )
        run.updated_at = datetime.now(UTC)
        return self.store.save(run)

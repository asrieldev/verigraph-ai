from datetime import datetime
from typing import Literal, TypedDict

from pydantic import BaseModel, Field

Status = Literal["queued", "running", "completed", "failed"]


class SourceFile(TypedDict):
    path: str
    content: str
    lines: list[str]


class CreateRun(BaseModel):
    repository_url: str = Field(min_length=1, max_length=500)


class AgentState(BaseModel):
    name: str
    status: Status = "queued"
    latency_ms: int = 0


class Finding(BaseModel):
    id: str
    agent: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    confidence: float = Field(ge=0, le=1)
    title: str
    explanation: str
    file: str
    line: int = Field(ge=1)
    evidence: str
    status: Literal["open", "verified", "dismissed", "fixed"] = "open"
    patch: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str
    path: str | None = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: str


class Verification(BaseModel):
    name: str
    tool: str
    passed: bool
    output: str


class Trace(BaseModel):
    at: datetime
    message: str
    kind: str = "info"


class Metrics(BaseModel):
    files: int = 0
    nodes: int = 0
    findings: int = 0
    latency_ms: int = 0
    tokens: int = 0
    estimated_cost_usd: float = 0


class Run(BaseModel):
    id: str
    repository_url: str
    status: Status = "queued"
    demo_mode: bool
    created_at: datetime
    updated_at: datetime
    agents: list[AgentState]
    findings: list[Finding] = []
    graph: dict[str, list[GraphNode] | list[GraphEdge]] = {"nodes": [], "edges": []}
    verification: list[Verification] = []
    trace: list[Trace] = []
    metrics: Metrics = Metrics()

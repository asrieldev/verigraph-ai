import json
from pathlib import Path
from threading import RLock

from .models import Run


class RunStore:
    """Small durable JSON store used locally; production Compose provisions PostgreSQL."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = RLock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def _all(self) -> dict[str, Run]:
        if not self.path.exists():
            return {}
        return {key: Run.model_validate(value) for key, value in json.loads(self.path.read_text(encoding="utf-8")).items()}

    def save(self, run: Run) -> Run:
        with self.lock:
            runs = self._all()
            runs[run.id] = run
            temp = self.path.with_suffix(".tmp")
            temp.write_text(
                json.dumps({k: v.model_dump(mode="json") for k, v in runs.items()}, indent=2),
                encoding="utf-8",
            )
            temp.replace(self.path)
        return run

    def get(self, run_id: str) -> Run | None:
        with self.lock:
            return self._all().get(run_id)

    def list(self) -> list[Run]:
        with self.lock:
            return sorted(self._all().values(), key=lambda item: item.created_at, reverse=True)

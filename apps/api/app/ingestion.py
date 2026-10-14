import ast
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .config import settings
from .models import GraphEdge, GraphNode, SourceFile

SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".cs", ".rs"}
IGNORED = {".git", "node_modules", "dist", "build", ".venv", "vendor"}


def validate_repository_url(url: str) -> tuple[str, str]:
    if url == "https://github.com/verigraph-ai/demo":
        return "verigraph-ai", "demo"
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in settings.allowed_github_hosts.split(","):
        raise ValueError("Only HTTPS URLs from an allowed GitHub host are accepted")
    pieces = [p for p in parsed.path.strip("/").split("/") if p]
    if len(pieces) != 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in pieces):
        raise ValueError("Expected a public GitHub URL in the form https://github.com/owner/repository")
    return pieces[0], pieces[1].removesuffix(".git")


def clone_repository(url: str, target: Path) -> Path:
    validate_repository_url(url)
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", url, str(target)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("Unable to clone this public repository")
    subprocess.run(
        ["git", "-C", str(target), "checkout", "HEAD", "--", "."],
        capture_output=True,
        timeout=60,
        check=True,
    )
    enforce_repository_size(target)
    return target


def enforce_repository_size(root: Path) -> None:
    maximum = settings.max_repository_mb * 1024 * 1024
    total = 0
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file() or ".git" in path.parts:
            continue
        total += path.stat().st_size
        if total > maximum:
            raise ValueError(f"Repository exceeds the {settings.max_repository_mb} MB limit")


def index_repository(
    root: Path,
) -> tuple[list[SourceFile], list[GraphNode], list[GraphEdge]]:
    files: list[SourceFile] = []
    nodes = []
    edges = []
    path_ids = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES or any(p in IGNORED for p in path.parts):
            continue
        if path.stat().st_size > settings.max_file_bytes:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        node_id = f"file:{rel}"
        path_ids[rel] = node_id
        files.append({"path": rel, "content": text, "lines": text.splitlines()})
        nodes.append(GraphNode(id=node_id, label=Path(rel).name, kind="file", path=rel))
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
                for item in ast.walk(tree):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fid = f"fn:{rel}:{item.name}"
                        nodes.append(GraphNode(id=fid, label=f"{item.name}()", kind="function", path=rel))
                        edges.append(GraphEdge(id=f"contains:{fid}", source=node_id, target=fid, kind="contains"))
            except SyntaxError:
                pass
    for file in files:
        rel = str(file["path"])
        text = str(file["content"])
        for match in re.findall(r"(?:from|import)\s+([\w.]+)|from\s+['\"]([^'\"]+)", text):
            raw = next((x for x in match if x), "").replace(".", "/")
            for candidate, node_id in path_ids.items():
                if candidate.removesuffix(Path(candidate).suffix).endswith(raw):
                    edges.append(
                        GraphEdge(
                            id=f"import:{rel}:{candidate}",
                            source=path_ids[rel],
                            target=node_id,
                            kind="imports",
                        )
                    )
                    break
    return files, nodes, edges

from fastapi.testclient import TestClient

from app.config import settings
from app.ingestion import enforce_repository_size, index_repository
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_rejects_unsafe_url():
    assert client.post("/api/runs", json={"repository_url": "file:///etc/passwd"}).status_code == 422


def test_demo_run_completes():
    response = client.post("/api/runs", json={"repository_url": "https://github.com/verigraph-ai/demo"})
    assert response.status_code == 202
    run = client.get(f"/api/runs/{response.json()['id']}").json()
    assert run["status"] == "completed"
    assert run["findings"][0]["evidence"]
    assert run["graph"]["nodes"]


def test_repository_size_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "max_repository_mb", 0)
    (tmp_path / "source.py").write_text("print('bounded')", encoding="utf-8")
    try:
        enforce_repository_size(tmp_path)
    except ValueError as exc:
        assert "0 MB limit" in str(exc)
    else:
        raise AssertionError("Oversized repository was accepted")


def test_indexer_skips_symlinks(tmp_path):
    source = tmp_path / "source.py"
    source.write_text("def safe():\n    return True\n", encoding="utf-8")
    link = tmp_path / "linked.py"
    try:
        link.symlink_to(source)
    except OSError:
        return
    files, _, _ = index_repository(tmp_path)
    assert [item["path"] for item in files] == ["source.py"]

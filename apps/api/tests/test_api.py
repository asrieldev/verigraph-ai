from fastapi.testclient import TestClient

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

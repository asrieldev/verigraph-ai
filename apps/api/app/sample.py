from pathlib import Path


def create_sample(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "app.py").write_text(
        "from auth import build_query\n\ndef get_user(name):\n    return build_query(name)\n",
        encoding="utf-8",
    )
    (root / "auth.py").write_text(
        'def build_query(name):\n    # demo fixture: unsafe query construction\n    return "SELECT * FROM users WHERE name = \'" + name + "\'"\n',
        encoding="utf-8",
    )
    (root / "test_app.py").write_text(
        'from app import get_user\n\ndef test_query_shape():\n    assert "SELECT" in get_user("Ada")\n',
        encoding="utf-8",
    )
    return root

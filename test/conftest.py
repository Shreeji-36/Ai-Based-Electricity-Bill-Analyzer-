import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ADMIN_EMAIL"] = "admin@test.com"
os.environ["ADMIN_PASSWORD"] = "AdminPass123"

for p in (ROOT / "backend", ROOT / "ai-engine", ROOT / "ocr"):
    sys.path.insert(0, str(p))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c
    Path("test.db").unlink(missing_ok=True)


@pytest.fixture(scope="session")
def token(client):
    r = client.post("/api/auth/login",
                    data={"username": "admin@test.com", "password": "AdminPass123"})
    return r.json()["access_token"]


@pytest.fixture
def auth(token):
    return {"Authorization": f"Bearer {token}"}
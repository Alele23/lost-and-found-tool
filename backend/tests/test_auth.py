"""Tests for the ``require_api_key`` dependency.

These build a throwaway FastAPI app with one protected route, rather than
importing the real app, so the auth gate is tested in isolation.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_api_key
from app.config import Settings, get_settings

TEST_KEY = "test-secret-key"


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_api_key)])
    def protected() -> dict[str, bool]:
        return {"ok": True}

    # Override settings so the test does not depend on the real .env value.
    app.dependency_overrides[get_settings] = lambda: Settings(
        api_secret_key=TEST_KEY,
        gemini_api_key="unused",
        sheet_id="unused",
    )
    return TestClient(app)


def test_missing_key_is_401(client: TestClient) -> None:
    resp = client.get("/protected")
    assert resp.status_code == 401


def test_wrong_key_is_401(client: TestClient) -> None:
    resp = client.get("/protected", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_correct_key_allows_request(client: TestClient) -> None:
    resp = client.get("/protected", headers={"X-API-Key": TEST_KEY})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

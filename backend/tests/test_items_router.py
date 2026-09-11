from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from gspread.exceptions import GSpreadException

from app.config import Settings, get_settings
from app.main import app
from app.models import Category, ItemExtraction
from app.services.gemini import GeminiExtractionError

TEST_KEY = "test-secret-key"


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_settings] = lambda: Settings(
        api_secret_key=TEST_KEY, gemini_api_key="unused", sheet_id="unused"
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def _upload(client: TestClient, key: str | None = TEST_KEY, content: bytes = b"fake-bytes"):
    headers = {"X-API-Key": key} if key else {}
    return client.post(
        "/upload", headers=headers, files={"photo": ("item.png", content, "image/png")}
    )


def test_upload_requires_api_key(client: TestClient) -> None:
    resp = _upload(client, key=None)
    assert resp.status_code == 401


def test_upload_rejects_empty_file(client: TestClient) -> None:
    resp = _upload(client, content=b"")
    assert resp.status_code == 400


def test_upload_returns_extracted_fields_with_defaults(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "app.routers.items.extract_item",
        lambda image_bytes, mime_type: ItemExtraction(
            item_description="A red backpack.", category=Category.ACCESSORIES
        ),
    )

    resp = _upload(client)

    assert resp.status_code == 200
    body = resp.json()
    assert body["item_description"] == "A red backpack."
    assert body["category"] == "Accessories"
    assert body["status"] == "Found"  # server default, not from Gemini


def test_upload_surfaces_gemini_failure_as_502(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(image_bytes: bytes, mime_type: str) -> ItemExtraction:
        raise GeminiExtractionError("Gemini was unavailable after 3 attempts")

    monkeypatch.setattr("app.routers.items.extract_item", _boom)

    resp = _upload(client)

    assert resp.status_code == 502


def test_create_item_requires_api_key(client: TestClient) -> None:
    resp = client.post("/items", json={"item_description": "x", "category": "Other"})
    assert resp.status_code == 401


def test_create_item_appends_and_returns_it(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    appended = []
    monkeypatch.setattr("app.routers.items.append_item", appended.append)

    payload = {
        "item_description": "Keys with a blue lanyard",
        "category": "Keys",
        "date_found": "2026-09-01",
        "reported_by": "Adam",
    }
    resp = client.post("/items", headers={"X-API-Key": TEST_KEY}, json=payload)

    assert resp.status_code == 201
    assert resp.json()["item_description"] == "Keys with a blue lanyard"
    assert len(appended) == 1
    assert appended[0].reported_by == "Adam"


def test_create_item_surfaces_sheets_failure_as_502(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(item):
        raise GSpreadException("permission denied")

    monkeypatch.setattr("app.routers.items.append_item", _boom)

    resp = client.post(
        "/items",
        headers={"X-API-Key": TEST_KEY},
        json={"item_description": "x", "category": "Other"},
    )

    assert resp.status_code == 502

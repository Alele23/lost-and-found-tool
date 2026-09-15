"""Tests for the Gemini service, using a fake client -- no network calls.

The fake mimics only the shape extract_item() actually uses:
client.models.generate_content(...) -> object with .parsed / .text.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from google.genai import errors

from app.config import Settings
from app.models import Category, ItemExtraction
from app.services.gemini import GeminiExtractionError, extract_item

TEST_SETTINGS = Settings(
    api_secret_key="unused",
    gemini_api_key="unused",
    sheet_id="unused",
    gemini_model="test-model",
)


class _FakeModels:
    """Returns each item in ``responses`` in order; an Exception is raised."""

    def __init__(self, responses: list) -> None:
        self._responses = iter(responses)
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        item = next(self._responses)
        if isinstance(item, Exception):
            raise item
        return item


class _FakeClient:
    def __init__(self, responses: list) -> None:
        self.models = _FakeModels(responses)


def _ok_response(description="A red backpack.", category=Category.OTHER):
    parsed = ItemExtraction(item_description=description, category=category)
    return SimpleNamespace(parsed=parsed, text="{...}")


def _server_error() -> errors.ServerError:
    return errors.ServerError(503, {"error": {"message": "busy", "status": "UNAVAILABLE"}})


def _client_error() -> errors.ClientError:
    return errors.ClientError(429, {"error": {"message": "quota exceeded", "status": "RESOURCE_EXHAUSTED"}})


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip the real backoff delay so retry tests run instantly."""
    monkeypatch.setattr("app.services.gemini.time.sleep", lambda _seconds: None)


def test_happy_path_returns_parsed_extraction() -> None:
    client = _FakeClient([_ok_response("A red backpack.", Category.ACCESSORIES)])

    result = extract_item(b"fake-bytes", "image/png", client=client, settings=TEST_SETTINGS)

    assert result == ItemExtraction(
        item_description="A red backpack.", category=Category.ACCESSORIES
    )
    assert len(client.models.calls) == 1
    assert client.models.calls[0]["model"] == "test-model"


def test_retries_on_transient_server_error_then_succeeds() -> None:
    client = _FakeClient([_server_error(), _ok_response()])

    result = extract_item(b"fake-bytes", "image/png", client=client, settings=TEST_SETTINGS)

    assert result.item_description == "A red backpack."
    assert len(client.models.calls) == 2  # one failure, one success


def test_gives_up_after_max_attempts() -> None:
    client = _FakeClient([_server_error(), _server_error(), _server_error()])

    with pytest.raises(GeminiExtractionError, match="unavailable"):
        extract_item(b"fake-bytes", "image/png", client=client, settings=TEST_SETTINGS)

    assert len(client.models.calls) == 3


def test_unparsable_response_raises() -> None:
    client = _FakeClient([SimpleNamespace(parsed=None, text="not json")])

    with pytest.raises(GeminiExtractionError, match="no parsable result"):
        extract_item(b"fake-bytes", "image/png", client=client, settings=TEST_SETTINGS)


def test_client_error_fails_immediately_without_retrying() -> None:
    # A 429/quota-exceeded won't succeed on retry, so it shouldn't burn more
    # attempts against the quota -- confirm it raises on the first try.
    client = _FakeClient([_client_error(), _ok_response()])

    with pytest.raises(GeminiExtractionError, match="rejected the request"):
        extract_item(b"fake-bytes", "image/png", client=client, settings=TEST_SETTINGS)

    assert len(client.models.calls) == 1

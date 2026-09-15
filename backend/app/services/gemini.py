"""Gemini vision service.

Sends a photo of a found item to Gemini and gets back the two fields it can
plausibly read from an image: a short description and a category. Everything
else on the record (date, location, status, ...) is filled in elsewhere with
server defaults or staff input -- see app/models.py.
"""

from __future__ import annotations

import time

from google import genai
from google.genai import errors, types

from app.config import Settings, get_settings
from app.models import ItemExtraction

PROMPT = (
    "You are helping a university lost-and-found desk log an item from a "
    "photo. Write a very concise description of the item -- what it is, "
    "its color, and any brand or distinguishing details visible in the "
    'photo (for example: Cream colored Bose Headphones). Then classify it into the best matching category. If nothing '
    'fits well, use "Other".'
)

# The API occasionally returns a transient 5xx ("high demand") that succeeds
# moments later -- worth a couple of automatic retries rather than failing
# a staff member's upload. 4xx errors (bad key, bad request) are not retried;
# they won't succeed the second time either.
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = 2.0


class GeminiExtractionError(RuntimeError):
    """Raised when Gemini's response can't be turned into an ItemExtraction."""


def _build_client(settings: Settings) -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def extract_item(
    image_bytes: bytes,
    mime_type: str,
    client: genai.Client | None = None,
    settings: Settings | None = None,
) -> ItemExtraction:
    """Return the description + category Gemini reads from a photo.

    ``client`` and ``settings`` are injectable so tests can supply fakes
    instead of hitting the real API / reading the real .env; production call
    sites omit both and they're built normally.
    """
    settings = settings or get_settings()
    client = client or _build_client(settings)

    contents = [types.Part.from_bytes(data=image_bytes, mime_type=mime_type), PROMPT]
    config = {"response_mime_type": "application/json", "response_schema": ItemExtraction}

    last_error: errors.ServerError | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model, contents=contents, config=config
            )
        except errors.ServerError as exc:
            last_error = exc
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_BACKOFF_SECONDS * (attempt + 1))
            continue
        except errors.ClientError as exc:
            raise GeminiExtractionError(f"Gemini rejected the request: {exc}") from exc

        if response.parsed is None:
            raise GeminiExtractionError(
                f"Gemini returned no parsable result: {response.text!r}"
            )
        return response.parsed

    raise GeminiExtractionError(
        f"Gemini was unavailable after {_MAX_ATTEMPTS} attempts"
    ) from last_error

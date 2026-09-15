from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ``backend/`` -- the directory that holds the ``app`` package, ``.env`` and
# (later) the service-account JSON. Resolved from this file's location so it
# works no matter which directory uvicorn is launched from.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Typed, validated view of the app's configuration.

    Field names are lower_snake_case. pydantic-settings matches them
    case-insensitively against environment variables, so ``api_secret_key`` is
    populated from ``API_SECRET_KEY``. A missing required value raises a
    ``ValidationError`` the moment ``Settings()`` is constructed, so the app
    fails loudly at startup instead of deep inside a request.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # tolerate unrelated vars in the environment / .env
    )

    # Shared secret that clients must send in the "X-API-Key" header (Step 3).
    api_secret_key: str

    # Google AI Studio key for the Gemini vision calls (Step 5).
    gemini_api_key: str

    # Gemini model handles the photo -> fields extraction.
    gemini_model: str = "gemini-3.5-flash-lite"

    # Filename (or absolute path) of the Google service-account JSON used for
    # the Sheets API (Step 6). Relative values are resolved against BASE_DIR.
    google_credentials_file: str = "service_account.json"

    # The target Google Sheet's ID -- the long token in the sheet's URL (Step 6).
    sheet_id: str

    @property
    def google_credentials_path(self) -> Path:
        """Absolute path to the service-account JSON file."""
        candidate = Path(self.google_credentials_file)
        return candidate if candidate.is_absolute() else BASE_DIR / candidate


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide ``Settings`` instance.

    ``@lru_cache`` makes this a lazy singleton: the ``.env`` file is read once,
    on first call, and the same object is reused afterwards. It is also the seam
    FastAPI's dependency-injection overrides in tests.
    """
    return Settings()

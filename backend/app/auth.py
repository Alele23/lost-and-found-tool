"""API-key authentication.

A single shared secret (``API_SECRET_KEY`` in the environment) gates every
protected route. Clients send it in the ``X-API-Key`` request header. This is
deliberately simple: it keeps casual traffic out of an internal staff tool, and
is not a substitute for per-user auth.

Attach it to a route or an entire router as a dependency::

    from fastapi import Depends
    from app.auth import require_api_key

    @router.post("/upload", dependencies=[Depends(require_api_key)])
    def upload(...): ...
"""

from __future__ import annotations

import secrets

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    """Reject the request unless the ``X-API-Key`` header matches the secret.

    Raises ``401`` for a missing *or* incorrect key. Returns ``None`` on
    success: this is a gate, not a value provider.

    ``settings`` is injected via ``Depends`` (rather than calling
    ``get_settings()`` directly) so tests can override it.
    ``secrets.compare_digest`` compares in constant time, so response timing
    does not leak how much of the key was correct.
    """
    if x_api_key is None or not secrets.compare_digest(
        x_api_key, settings.api_secret_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

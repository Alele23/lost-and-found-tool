"""FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Lost & Found Intake API")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check. No auth — used by scripts and load balancers."""
    return {"status": "ok"}

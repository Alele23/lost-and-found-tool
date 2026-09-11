"""FastAPI application entry point.

Run locally with:
    uvicorn app.main:app --reload --port 8001
"""

from __future__ import annotations

from fastapi import FastAPI

from app.routers.items import router as items_router

app = FastAPI(title="Lost & Found Intake API")
app.include_router(items_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check. No auth — used by scripts and load balancers."""
    return {"status": "ok"}

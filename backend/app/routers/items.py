from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from gspread.exceptions import GSpreadException

from app.auth import require_api_key
from app.models import ItemFields
from app.services.gemini import GeminiExtractionError, extract_item
from app.services.sheets import append_item

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/upload", response_model=ItemFields)
async def upload_photo(photo: UploadFile = File(...)) -> ItemFields:
    image_bytes = await photo.read()
    if not image_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    try:
        extraction = await run_in_threadpool(
            extract_item, image_bytes, photo.content_type or "image/jpeg"
        )
    except GeminiExtractionError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ItemFields(**extraction.model_dump())


@router.post("/items", response_model=ItemFields, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemFields) -> ItemFields:
    try:
        append_item(item)
    except GSpreadException as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, detail="Could not save to spreadsheet"
        ) from exc
    return item

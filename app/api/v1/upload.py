import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.core.responses import ApiResponse

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["Upload"]
)

UPLOAD_DIR = os.path.join(settings.UPLOAD_FOLDER, "pitchdeck")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/pitch-deck")
async def upload_pitch_deck(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    content = await file.read()

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 10 MB."
        )

    filename = f"{uuid.uuid4().hex}.pdf"

    filepath = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(filepath, "wb") as f:
        f.write(content)

    return ApiResponse.success(
        message="Pitch deck uploaded successfully.",
        data={
            "filename": filename,
            "path": filepath
        },
        status_code=201
    )

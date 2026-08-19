from pathlib import Path
from uuid import uuid4
import logging

from fastapi import UploadFile

from app.config import settings

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = settings.MAX_PDF_SIZE_MB * 1024 * 1024
BASE_UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
PITCHDECK_DIR = BASE_UPLOAD_DIR / "pitchdeck"
IMAGES_DIR = BASE_UPLOAD_DIR / "images"

PITCHDECK_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/gif": ".gif",
}


class UploadService:

    @staticmethod
    async def save_pitch_deck(file: UploadFile) -> dict:
        """
        Secure PDF upload.
        """
        if not file.filename:
            raise ValueError("File name is required.")

        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed.")

        # Read first bytes to verify actual PDF signature.
        header = await file.read(5)

        if header != b"%PDF-":
            raise ValueError("Invalid PDF file.")

        await file.seek(0)

        filename = f"{uuid4().hex}.pdf"
        destination = PITCHDECK_DIR / filename

        total_size = 0

        try:
            with destination.open("wb") as output:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        raise ValueError(
                            f"Maximum file size is {settings.MAX_PDF_SIZE_MB} MB."
                        )
                    output.write(chunk)
        except Exception:
            if destination.exists():
                destination.unlink()
            raise

        return {
            "filename": filename,
            "originalFilename": file.filename,
            "size": total_size,
            "contentType": "application/pdf",
            "url": f"/uploads/pitchdeck/{filename}",
        }

    @staticmethod
    async def save_image(file: UploadFile) -> dict:
        """
        Secure Image upload for certificates (logos, signatures, seals, event banners).
        """
        if not file.filename:
            raise ValueError("Image file name is required.")

        c_type = (file.content_type or "").lower()
        if c_type not in ALLOWED_IMAGE_TYPES:
            # Fallback by extension
            ext = Path(file.filename).suffix.lower()
            if ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"]:
                suffix = ext
            else:
                raise ValueError("Allowed image types: PNG, JPEG, JPG, WEBP, SVG, GIF.")
        else:
            suffix = ALLOWED_IMAGE_TYPES[c_type]

        filename = f"{uuid4().hex}{suffix}"
        destination = IMAGES_DIR / filename

        total_size = 0

        try:
            with destination.open("wb") as output:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        raise ValueError(
                            f"Maximum file size is {settings.MAX_PDF_SIZE_MB} MB."
                        )
                    output.write(chunk)
        except Exception:
            if destination.exists():
                destination.unlink()
            raise

        return {
            "filename": filename,
            "originalFilename": file.filename,
            "size": total_size,
            "contentType": c_type or "image/png",
            "url": f"/uploads/images/{filename}",
        }
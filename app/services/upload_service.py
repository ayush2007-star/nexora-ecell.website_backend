from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings


MAX_FILE_SIZE = settings.MAX_PDF_SIZE_MB * 1024 * 1024
UPLOAD_DIR = Path(settings.UPLOAD_FOLDER) / "pitchdeck"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadService:

    @staticmethod
    async def save_pitch_deck(file: UploadFile) -> dict:
        """
        Secure PDF upload.

        - PDF content-type validation
        - PDF magic-header validation
        - 10 MB size limit
        - Random filename
        - No user-controlled path
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
        destination = UPLOAD_DIR / filename

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
                            f"Maximum file size is "
                            f"{settings.MAX_PDF_SIZE_MB} MB."
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
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document


router = APIRouter(
    prefix="/api/documents",
    tags=["documents"]
)


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # Generate unique filename
    unique_name = f"{uuid.uuid4()}_{file.filename}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    # Save PDF
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not save PDF."
        )

    # Get file size
    file_size = os.path.getsize(file_path)

    # Save metadata to PostgreSQL
    document = Document(
        filename=file.filename,
        file_path=file_path,
        content_type=file.content_type,
        file_size=file_size,
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "file_size": document.file_size,
        "status": document.status
    }
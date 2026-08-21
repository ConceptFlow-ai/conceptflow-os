import os
import sys
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, DocumentChunk

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONCEPT_EXTRACTION_DIR = PROJECT_ROOT / "concept-extraction"
if str(CONCEPT_EXTRACTION_DIR) not in sys.path:
    sys.path.insert(0, str(CONCEPT_EXTRACTION_DIR))

from pipeline import extract_pdf_chunks  # noqa: E402

router = APIRouter(prefix="/api/documents", tags=["documents"])
UPLOAD_DIR = PROJECT_ROOT / "backend" / "uploads"
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
DEFAULT_CHUNK_LIMIT = 50
MAX_CHUNK_LIMIT = 200
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
    document = None
    try:
        size = 0
        with file_path.open("wb") as buffer:
            while part := await file.read(1024 * 1024):
                size += len(part)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="PDF must be 25 MB or smaller.")
                buffer.write(part)

        with file_path.open("rb") as uploaded_file:
            if uploaded_file.read(5) != b"%PDF-":
                raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF.")

        document = Document(
            filename=filename,
            file_path=str(file_path),
            content_type="application/pdf",
            file_size=size,
            status="extracting_chunks",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        result = extract_pdf_chunks(file_path)
        db.add_all(
            DocumentChunk(document_id=document.id, **chunk)
            for chunk in result["chunks"]
        )
        document.status = "chunks_extracted"
        db.commit()

        return {
            "message": "Document uploaded and chunked successfully",
            "document_id": document.id,
            "filename": document.filename,
            "file_size": document.file_size,
            "page_count": result["page_count"],
            "chunk_count": result["chunk_count"],
            "status": document.status,
        }
    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as error:
        db.rollback()
        if document is not None:
            document = db.get(Document, document.id)
            if document is not None:
                document.status = "failed"
                db.commit()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=422, detail=f"Could not extract chunks: {error}") from error
    finally:
        await file.close()


@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    offset: int = 0,
    limit: int = DEFAULT_CHUNK_LIMIT,
    db: Session = Depends(get_db),
):
    if offset < 0 or not 1 <= limit <= MAX_CHUNK_LIMIT:
        raise HTTPException(status_code=422, detail=f"Use offset >= 0 and limit between 1 and {MAX_CHUNK_LIMIT}.")

    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "document_id": document_id,
        "status": document.status,
        "offset": offset,
        "limit": limit,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "word_count": chunk.word_count,
            }
            for chunk in chunks
        ],
    }

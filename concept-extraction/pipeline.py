"""Reusable PDF-to-chunks pipeline for the application backend."""

from pathlib import Path

from data_org.chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_lines
from extract_data.extract import analyze_font_sizes, extract_document
from extract_data.preprocessor import simplify_document


def extract_pdf_chunks(
    pdf_path: str | Path,
    *,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> dict:
    """Extract an uploaded PDF into source-traceable text chunks."""
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    document = extract_document(str(path))
    font_analysis = analyze_font_sizes(document)
    lines = simplify_document(document, font_analysis)
    chunks = chunk_lines(lines, chunk_size=chunk_size, overlap=chunk_overlap)

    return {
        "page_count": len(document),
        "line_count": len(lines),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }

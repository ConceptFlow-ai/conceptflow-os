"""
Entry point for the whole pipeline. Run this from inside FP/:

    cd FP
    python main.py

This is the ONLY file that should be run directly -- everything under
extract_data/ and data_org/ is meant to be imported as part of its package,
not executed on its own.
"""

from pathlib import Path

from extract_data.extract import extract_document, analyze_font_sizes
from extract_data.preprocessor import simplify_document
from data_org.chunking import chunk_lines
from data_org.extract_concepts import extract_concepts_from_chunks, apply_parent_inheritance, DEFAULT_MODEL

BASE_DIR = Path(__file__).resolve().parent
BOOK_PATH = BASE_DIR / "book.pdf"


def main():
    document = extract_document(str(BOOK_PATH))
    analysis = analyze_font_sizes(document)
    simple_lines = simplify_document(document, analysis)
    chunks = chunk_lines(simple_lines)

    elements = extract_concepts_from_chunks(chunks, model_name=DEFAULT_MODEL)
    elements = apply_parent_inheritance(elements)

    for el in elements[:10]:
        print("=" * 80)
        print(f"[{el['concept']}] ({el['content_type']}, importance={el['importance']})")
        print(f"start={el['start_concept']} end={el['end_concept']} parent={el['parent']}")
        print(el["text"][:200])

    return elements


if __name__ == "__main__":
    main()

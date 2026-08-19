from collections import Counter

import pymupdf

MIN_SIZE_COUNT = 10  # sizes occurring fewer times than this are dropped as noise


def decode_style(flags: int) -> dict:
    """Decode PyMuPDF span flags into readable style information."""
    return {
        "bold": bool(flags & (1 << 4)),
        "italic": bool(flags & (1 << 1)),
        "monospaced": bool(flags & (1 << 3)),
        "serif": bool(flags & (1 << 2)),
    }


def extract_document(pdf_path: str) -> list:
    pages = []
    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            raw = page.get_text("dict")
            page_data = {
                "page": page_number,
                "width": raw["width"],
                "height": raw["height"],
                "blocks": [],
            }
            for block in raw["blocks"]:
                if block["type"] != 0:  # ignore images / non-text blocks
                    continue
                block_data = {"type": block["type"], "number": block["number"], "lines": []}
                for line in block["lines"]:
                    line_data = {"spans": []}
                    for span in line["spans"]:
                        flags = span["flags"]
                        line_data["spans"].append(
                            {
                                "text": span["text"],
                                "font": span["font"],
                                "size": span["size"],
                                "flags": flags,
                                "style": decode_style(flags),
                                "origin": span.get("origin"),
                                "bbox": span.get("bbox"),
                            }
                        )
                    block_data["lines"].append(line_data)
                page_data["blocks"].append(block_data)
            pages.append(page_data)
    return pages


def count_font_sizes(document: list) -> Counter:
    """Count how many spans use each font size across the whole document."""
    counts = Counter()
    for page in document:
        for block in page["blocks"]:
            for line in block["lines"]:
                for span in line["spans"]:
                    counts[span["size"]] += 1
    return counts


def analyze_font_sizes(document: list, min_count: int = MIN_SIZE_COUNT) -> dict:
    """
    Analyze font-size usage across the document:
      - drop sizes that occur fewer than `min_count` times (noise: stray spans,
        superscripts, extraction artifacts, etc.)
      - sort the remaining sizes descending
      - assign level 1 to the largest size, level 2 to the next, and so on
      - name the size with the highest occurrence count as the "body" size

    Returns:
        {
            "counts": {size: count, ...},       # all sizes kept after filtering
            "levels": {size: level, ...},        # size -> level (1 = largest)
            "body_size": float,                  # most frequent size among those kept
        }
    """
    counts = count_font_sizes(document)

    # Drop sizes that occur too rarely to be meaningful
    filtered = {size: count for size, count in counts.items() if count >= min_count}

    # Sort remaining sizes descending, largest = level 1
    sorted_sizes = sorted(filtered.keys(), reverse=True)
    levels = {size: level for level, size in enumerate(sorted_sizes, start=1)}

    # Body size = whichever kept size occurs most often
    body_size = max(filtered, key=filtered.get) if filtered else None

    return {
        "counts": filtered,
        "levels": levels,
        "body_size": body_size,
    }

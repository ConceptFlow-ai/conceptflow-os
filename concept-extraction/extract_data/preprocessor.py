def _line_size(line: dict) -> float:
    """Representative size for a line = the span contributing the most characters,
    so one stray bold word doesn't decide the whole line's size."""
    spans = line["spans"]
    dominant = max(spans, key=lambda s: len(s["text"]))
    return dominant["size"]


def _category_for_size(size: float, analysis: dict) -> str:
    """Map a font size to "body", "level_n", or "other" (sizes filtered out
    for occurring too rarely to be a reliable heading/body signal)."""
    if size == analysis["body_size"]:
        return "body"
    if size in analysis["levels"]:
        return f"level_{analysis['levels'][size]}"
    return "other"


def simplify_document(document: list, analysis: dict) -> list:
    """
    Flatten the raw extracted document dict into a simple, flat list of lines:
        {
            "text": "...",
            "category": "level_1" | "body" | "other",
            "page": 42,
            "bbox": (x0, y0, x1, y1),
        }
    """
    simplified = []

    for page in document:
        page_number = page["page"]

        for block in page["blocks"]:
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue

                text = "".join(span["text"] for span in spans).strip()
                if not text:
                    continue

                category = _category_for_size(_line_size(line), analysis)
                bbox = spans[0].get("bbox")

                simplified.append(
                    {
                        "text": text,
                        "category": category,
                        "page": page_number,
                        "bbox": bbox,
                    }
                )

    return simplified

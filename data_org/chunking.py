CHUNK_SIZE = 1000
CHUNK_OVERLAP = 50


def chunk_lines(lines: list, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """
    Chunk the simplified line dicts (each {"text", "category", "page", "bbox"})
    into overlapping word windows.

    Word count is taken from each line's "text" value. Windows are `chunk_size`
    words wide and advance by (chunk_size - overlap) words each step, so
    consecutive chunks share `overlap` words.

    Returns a list of:
        {
            "chunk_id": 0,
            "text": "...",
            "page_start": 1,
            "page_end": 3,
            "word_count": 1000,
        }
    """
    # Flatten every line's words, remembering which line (and therefore which
    # page) each word came from.
    words = []  # list of (word, line_index)
    for idx, line in enumerate(lines):
        for w in line["text"].split():
            words.append((w, idx))

    if not words:
        return []

    step = max(chunk_size - overlap, 1)
    chunks = []
    chunk_id = 0
    i = 0
    n = len(words)

    while i < n:
        window = words[i : i + chunk_size]
        if not window:
            break

        line_indices = {idx for _, idx in window}
        pages = [lines[idx]["page"] for idx in line_indices]

        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": " ".join(w for w, _ in window),
                "page_start": min(pages),
                "page_end": max(pages),
                "word_count": len(window),
            }
        )
        chunk_id += 1

        if i + chunk_size >= n:
            break
        i += step

    return chunks

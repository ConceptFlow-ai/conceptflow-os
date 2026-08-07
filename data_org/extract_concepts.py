"""
Turn text chunks into structured "concept" segments using a local Ollama
model, then patch up missing `parent` fields with the inheritance rule:

    if current.parent is not None:
        use current.parent
    elif (
        current.concept == previous.concept
        and not current.start_concept
        and not previous.end_concept
    ):
        current.parent = previous.parent

NOTE: this module is part of the `data_org` package (it's imported as
`data_org.extract_concepts`, never run directly), which is why its imports
below are relative (`from . import ...`, `from .prompts import ...`).
Running `python extract_concepts.py` directly from inside data_org/ will
fail with "attempted relative import with no known parent package" --
that's expected. Use FP/main.py as the entry point instead.
"""

import json
import re

from . import ollama_client as ollama
from .prompts import SYS_PROMPT, build_user_prompt

DEFAULT_MODEL = "mistral-openorca"  # swap for whatever model you've pulled

REQUIRED_KEYS = {
    "concept": "",
    "content_type": "other",
    "importance": 3,
    "text": "",
    "start_concept": True,
    "end_concept": True,
    "heading_path": [],
    "parent": None,
    "pre_req": [],
    "cross_ref": [],
}


def _clean_json_block(raw: str) -> str:
    """Strip markdown code fences and any leading/trailing chatter so we're
    left with the JSON array itself."""
    text = raw.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text


def _coerce_element(obj: dict) -> dict:
    """Fill in any missing keys with sane defaults so downstream code never
    has to guard against KeyError."""
    out = dict(REQUIRED_KEYS)
    out.update({k: v for k, v in obj.items() if k in REQUIRED_KEYS})
    return out


def extract_concepts_from_text(
    chunk_text: str,
    model_name: str = DEFAULT_MODEL,
    heading_context=None,
) -> list:
    """Call the local Ollama model on one chunk and return a list of
    concept-segment dicts (schema described in prompts.SYS_PROMPT)."""
    prompt = build_user_prompt(chunk_text, heading_context=heading_context)

    response_text, _ = ollama.generate(
        model_name=model_name,
        prompt=prompt,
        system=SYS_PROMPT,
        options={"temperature": 0.0},
    )

    if not response_text:
        return []

    cleaned = _clean_json_block(response_text)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        print("Warning: could not parse model output as JSON, skipping chunk.")
        print(response_text[:500])
        return []

    if not isinstance(parsed, list):
        return []

    return [_coerce_element(item) for item in parsed if isinstance(item, dict)]


def extract_concepts_from_chunks(chunks: list, model_name: str = DEFAULT_MODEL) -> list:
    """
    Run extraction over every chunk produced by chunk_lines(), tagging each
    resulting segment with the chunk/page metadata it came from.
    """
    all_elements = []
    heading_context = None

    for chunk in chunks:
        segments = extract_concepts_from_text(
            chunk["text"], model_name=model_name, heading_context=heading_context
        )

        for seg in segments:
            seg["chunk_id"] = chunk["chunk_id"]
            seg["page_start"] = chunk["page_start"]
            seg["page_end"] = chunk["page_end"]
            all_elements.append(seg)

        if segments and segments[-1]["heading_path"]:
            heading_context = segments[-1]["heading_path"]

    return all_elements


def apply_parent_inheritance(elements: list) -> list:
    """
    Fill in `parent` for elements that didn't get one from the model, by
    inheriting from the previous element when it's clearly a continuation of
    the same concept (same concept name, current isn't a fresh start, and
    the previous segment hadn't already wrapped up).
    """
    previous = None

    for current in elements:
        if current.get("parent") is not None:
            pass  # keep the model's own answer
        elif (
            previous is not None
            and current["concept"] == previous["concept"]
            and not current["start_concept"]
            and not previous["end_concept"]
        ):
            current["parent"] = previous["parent"]

        previous = current

    return elements

"""
Prompt templates for extracting structured "concept" objects from text chunks.

Modeled on the extraction-prompt pattern used in rahulnyk/knowledge_graph
(https://github.com/rahulnyk/knowledge_graph): a strict system prompt that
forces the model to return ONLY a JSON array, plus a worked example, fed
through Ollama's /api/generate.
"""

SYS_PROMPT = """You are a network graph maker who extracts structured "concept" \
segments out of a given text chunk from a technical document or textbook. \
You will output a list of JSON objects, each representing one segment of the \
text that discusses a single concept.

Follow these rules exactly:

1. Read through the text chunk and split it into segments, where each segment \
covers ONE concept being taught or discussed. A single concept can span \
multiple sentences or paragraphs; keep it as one segment as long as it is the \
same concept.
2. For each segment, output an object with EXACTLY these keys:
   - "concept": short name of the concept discussed (e.g. "Gradient Descent").
   - "content_type": one of "definition", "explanation", "example", "formula",
     "list", "code", "proof", "summary", "other".
   - "importance": integer 1-5, how central this segment is to understanding
     the concept (5 = core definition, 1 = passing mention).
   - "text": the excerpt of the chunk that this segment covers, copied
     verbatim from the input (do not paraphrase).
   - "start_concept": true if this segment is where the concept FIRST begins
     being discussed within this chunk, false if it is a continuation of a
     concept that was already being discussed.
   - "end_concept": true if the discussion of this concept concludes within
     this chunk (nothing more about it follows before another concept
     starts), false if it likely continues into the next chunk.
   - "heading_path": a list of strings, the heading hierarchy this text falls
     under, from broadest to narrowest (e.g. ["Machine Learning",
     "Supervised Learning", "Regression"]). Infer this from any headings
     visible in the chunk or from context; use an empty list if unknown.
   - "parent": either null, or an object {"concept": "...", "confidence": 0-1}
     naming the broader concept this segment's concept is a sub-topic of.
     Only set this if you are actually confident; otherwise use null.
   - "pre_req": a list of {"concept": "...", "confidence": 0-1} objects for
     concepts the reader should already know before this segment makes
     sense. Use an empty list if none are evident.
   - "cross_ref": a list of {"concept": "...", "confidence": 0-1} objects for
     related concepts this segment references or relates to, that are not
     prerequisites or the parent. Use an empty list if none are evident.

3. "confidence" values are floats between 0 and 1 reflecting how sure you are
   of that relationship.
4. Output ONLY a valid JSON array of these objects. No markdown fences, no
   commentary, no keys other than the ones listed above.

Example output for a chunk about regression:
[
  {
    "concept": "Regression",
    "content_type": "definition",
    "importance": 5,
    "text": "Regression is a supervised learning technique used to predict a continuous value.",
    "start_concept": true,
    "end_concept": false,
    "heading_path": ["Machine Learning", "Supervised Learning", "Regression"],
    "parent": {"concept": "Supervised Learning", "confidence": 0.95},
    "pre_req": [{"concept": "Statistics", "confidence": 0.8}],
    "cross_ref": [{"concept": "Classification", "confidence": 0.6}]
  }
]
"""


def build_user_prompt(chunk_text: str, heading_context=None) -> str:
    """
    Build the user-turn prompt for a single chunk.

    heading_context: optional list of strings representing the heading path
    known to be active as of the start of this chunk (carried over from the
    previous chunk), so the model has continuity across chunk boundaries.
    """
    context_block = ""
    if heading_context:
        context_block = (
            "The heading path active at the start of this chunk (from a "
            "previous chunk) is: " + " > ".join(heading_context) + "\n"
            "Use this as a hint for heading_path continuity if the chunk "
            "does not introduce new headings.\n\n"
        )

    return (
        f"{context_block}"
        "Extract concept segments from the following text chunk.\n"
        "Text chunk:\n"
        "```\n"
        f"{chunk_text}\n"
        "```\n"
        "Return only the JSON array."
    )

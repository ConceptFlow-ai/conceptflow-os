# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Concept Extraction Pipeline
The main entry point for the concept extraction pipeline:
```bash
# From the repository root
cd concept-extraction
python main.py
```

This will process the `book.pdf` file and output the first 10 extracted concepts to stdout.

### Development Workflow
1. **Modify core components**: Changes to PDF processing go in `extract_data/`, concept extraction logic in `data_org/`
2. **Test modifications**: Run the main pipeline to see effects on concept extraction
3. **Ollama dependency**: Ensure Ollama is running with the mistral-openorca model (or update DEFAULT_MODEL in data_org/extract_concepts.py)

### Debugging
- Individual modules can be tested by importing them in Python interactive sessions
- The pipeline is designed to be modular: each module in extract_data/ and data_org/ can be imported and tested independently
- Main.py shows the exact data flow between components

## Code Architecture & Structure

### High-Level Pipeline
The concept extraction pipeline consists of four main stages:

1. **PDF Processing** (`extract_data/extract.py`):
   - Extracts text, formatting, and structural information from PDFs using PyMuPDF
   - Outputs hierarchical document structure (pages → blocks → lines → spans)
   - Analyzes font usage to identify heading levels vs body text

2. **Text Preprocessing** (`extract_data/preprocessor.py`):
   - Simplifies document structure based on font analysis
   - Groups text by detected heading levels
   - Prepares clean text chunks for concept extraction

3. **Chunking** (`data_org/chunking.py`):
   - Splits preprocessed text into manageable chunks
   - Preserves page boundaries and heading context
   - Outputs chunks with metadata (chunk_id, page_start, page_end)

4. **Concept Extraction** (`data_org/extract_concepts.py` + `data_org/prompts.py`):
   - Sends chunks to local Ollama model for structured concept extraction
   - Uses carefully crafted prompts to extract concept segments with metadata
   - Applies parent inheritance to improve concept hierarchy detection

### Key Modules
- `extract_data/extract.py`: Core PDF text and style extraction
- `extract_data/preprocessor.py`: Transforms raw PDF output into structured text
- `data_org/chunking.py`: Text chunking with metadata preservation  
- `data_org/prompts.py`: Prompt engineering for concept extraction
- `data_org/ollama_client.py`: Wrapper for Ollama API interactions
- `data_org/extract_concepts.py`: Main concept extraction logic with inheritance
- `main.py`: Orchestrates the full pipeline as the entry point

### Data Flow
```
PDF → extract_document() → analyze_font_sizes() → simplify_document() 
    → chunk_lines() → extract_concepts_from_chunks() → apply_parent_inheritance()
```

### Extensibility Points
- To change the LLM model: Modify `DEFAULT_MODEL` in data_org/extract_concepts.py
- To adjust chunking strategy: Modify `data_org/chunking.py`
- To refine concept extraction prompts: Edit `data_org/prompts.py`
- To change PDF processing logic: Update functions in `extract_data/`

### Dependencies
- Python packages: pymupdf, requests (for Ollama), collections
- External service: Ollama running locally (default: http://localhost:11434)
- Model: mistral-openorca (configurable)

### Important Notes
- The pipeline is designed to be run from the concept-extraction directory
- All modules use relative imports and should not be executed directly
- Error handling is minimal - failures in Ollama communication will halt the pipeline
- Output is currently limited to printing first 10 concepts for quick verification
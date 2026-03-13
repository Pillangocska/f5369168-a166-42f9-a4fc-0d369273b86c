# Resume Extractor

A Python CLI tool that processes a directory of resume PDFs and extracts structured data using an LLM.

## Architecture

```
task_4_llm/
├── client/
│   ├── __init__.py            # Re-exports + create_client() factory
│   ├── base_llm_client.py     # ABC, shared prompt, parse_llm_response()
│   ├── anthropic_client.py    # Claude API implementation
│   └── gemini_client.py       # Google Gemini implementation
├── model/
│   ├── __init__.py            # Re-exports all models
│   ├── education.py           # Education schema
│   ├── work_experience.py     # WorkExperience schema
│   └── resume_data.py         # Top-level ResumeData schema
├── cli.py                     # CLI entry point (argparse)
├── pdf_reader.py              # PDF text extraction (PyMuPDF)
└── processor.py               # Async batch orchestrator
```

**Adding a new provider:** Create a new file in `client/`, subclass `BaseLLMClient` from `base_llm_client.py`, implement the `extract()` method, and register it in the `create_client()` factory in `client/__init__.py`.

## Installation

```bash
pip install -e .

# For Gemini support:
pip install -e ".[gemini]"
```

## Usage

### Linux / macOS

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
resume-extractor ./resumes/ -o ./output/

# Using Gemini
export GOOGLE_API_KEY="..."
resume-extractor ./resumes/ -p gemini

# Custom concurrency and model
resume-extractor ./resumes/ -c 10 --model claude-sonnet-4-20250514 -v
```

### Windows (PowerShell)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Run as a module via uv (no install needed)
uv run python -m task_4_llm .\resumes\ -o .\output\

# Using Gemini
$env:GOOGLE_API_KEY = "..."
uv run python -m task_4_llm .\resumes\ -p gemini

# Custom concurrency and model
uv run python -m task_4_llm .\resumes\ -c 10 --model claude-sonnet-4-20250514 -v
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `input_dir` | *(required)* | Path to folder containing PDF files |
| `-o, --output-dir` | `<input_dir>/output` | Where to write JSON files |
| `-p, --provider` | `anthropic` | LLM provider (`anthropic` or `gemini`) |
| `--api-key` | env variable | Override API key |
| `--model` | provider default | Override model name |
| `-c, --concurrency` | `5` | Max parallel API calls |
| `-v, --verbose` | off | DEBUG-level logging |

## Output Format

Each resume produces a JSON file like:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1 555-123-4567",
  "education": [
    {
      "institution": "MIT",
      "degree": "M.Sc.",
      "field_of_study": "Computer Science",
      "start_date": "2018",
      "end_date": "2020"
    }
  ],
  "work_experience": [
    {
      "company": "Acme Corp",
      "title": "Senior Engineer",
      "start_date": "Jan 2021",
      "end_date": "Present",
      "description": "Led backend architecture for payments platform."
    }
  ],
  "skills": ["Python", "AWS", "PostgreSQL", "Docker"]
}
```

---

## Task Questions & Answers

### 1. How can we ensure extracted data accuracy?

- **Strict schema validation** — Pydantic validates every LLM response against the `ResumeData` model. Malformed or missing-field responses raise immediately.
- **Zero temperature** — All API calls use `temperature=0.0` for deterministic output.
- **Explicit prompt constraints** — The system prompt instructs the model to use `null` for missing fields and never fabricate data.
- **Shared response parsing** — `parse_llm_response()` in `base_llm_client.py` centralizes JSON parsing, markdown fence stripping, and Pydantic validation so every provider goes through the same validation path.
- **Post-validation hooks** (extension point) — Regex checks on emails/phones, or a second cheaper LLM pass to flag low-confidence extractions.
- **Error logging** — Every failure is captured in `ProcessingResult` with the specific error for human review.

### 2. What is the median processing time per resume? How could we optimize it?

- **Expected median:** ~9 seconds per resume (PDF extraction <0.5s, LLM round-trip 3–6s depending on model and provider).
- **Optimizations already in place:**
  - Async concurrency with configurable semaphore (default 5 parallel calls).
  - PDF extraction runs in a thread pool to avoid blocking the event loop.
- **Further optimizations:**
  - Increase concurrency if the API rate limit allows.
  - Use a faster/smaller model (e.g., `claude-haiku-4-5-20251001` or `gemini-2.0-flash`).
  - Cache results by PDF hash to skip reprocessing unchanged files.
  - Truncate irrelevant PDF content (headers/footers) before sending.

### 3. What is the median API cost per resume? How could we reduce it?

- **Estimated cost per resume:**
  - Input: ~800–1,500 tokens (resume text + system prompt).
  - Output: ~300–700 tokens (JSON).
  - **Claude Sonnet:** ~$0.003–$0.008 per resume.
  - **Gemini Flash:** ~$0.0001–$0.0003 per resume.
- **Cost reduction strategies:**
  - Use cheaper models (Haiku, Gemini Flash) when accuracy is sufficient.
  - Keep prompts concise — our system prompt is minimal by design.
  - Cache by file hash to never reprocess the same PDF.
  - Use batch APIs (Anthropic Batch API is 50% cheaper) for non-time-sensitive workloads.
- **We can also use our own LLM on bare metal / or local for this use case.

### 4. What tools did you use to solve this task?

| Tool | Purpose |
|------|---------|
| **PyMuPDF (fitz)** | Solid PDF text extraction |
| **Pydantic v2** | Schema definition and response validation |
| **Anthropic SDK** | Native Claude API client (default provider) |
| **google-genai** | Google Gemini client (optional provider) |
| **asyncio** | Concurrent processing with semaphore-based rate limiting |
| **argparse** | CLI argument parsing (stdlib, zero dependencies) |

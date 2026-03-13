"""Abstract base class for LLM provider clients.

To add a new provider, subclass ``BaseLLMClient``, implement the
``extract`` method, and register it in the ``create_client`` factory
in ``__init__.py``.
"""

from abc import ABC, abstractmethod

from task_4_llm.model.resume_data import ResumeData

# Shared system prompt used by all providers.
SYSTEM_PROMPT: str = """\
You are a precise resume data extractor. Given the raw text of a resume,
extract structured information and return it as valid JSON matching the
schema below. Follow these rules strictly:

1. Extract ONLY information explicitly present in the text.
2. Use null for any field not found — never guess or fabricate.
3. For dates, preserve the format as written in the resume.
4. For skills, extract individual skills as separate list items.
5. Order work experience with the most recent position first.
6. Keep descriptions concise — summarize, do not copy paragraphs verbatim.

JSON Schema:
{
  "name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "education": [
    {
      "institution": "string",
      "degree": "string or null",
      "field_of_study": "string or null",
      "start_date": "string or null",
      "end_date": "string or null"
    }
  ],
  "work_experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "string or null",
      "end_date": "string or null",
      "description": "string or null"
    }
  ],
  "skills": ["string"]
}

Respond with ONLY the JSON object. No markdown, no explanation."""


def parse_llm_response(raw_text: str) -> ResumeData:
    """Parse and validate raw LLM text into a ResumeData instance.

    Handles markdown fence stripping and JSON decoding.

    Args:
        raw_text: Raw text response from the LLM.

    Returns:
        Validated ResumeData instance.

    Raises:
        RuntimeError: If JSON parsing or validation fails.
    """
    import json

    text: str = raw_text.strip()

    # Strip markdown fences if the model wraps output.
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()

    try:
        data: dict = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Failed to parse LLM response as JSON: {exc}\n"
            f"Raw response:\n{text[:500]}"
        ) from exc

    return ResumeData.model_validate(data)


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients."""

    @abstractmethod
    async def extract(self, resume_text: str) -> ResumeData:
        """Send resume text to the LLM and return structured data.

        Args:
            resume_text: Raw text extracted from a resume PDF.

        Returns:
            Validated ResumeData instance.

        Raises:
            RuntimeError: If the API call fails or response is invalid.
        """

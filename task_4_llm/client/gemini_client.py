"""Google Gemini API client."""

from typing import Optional
import asyncio

from task_4_llm.client.base_llm_client import (
    BaseLLMClient,
    SYSTEM_PROMPT,
    parse_llm_response,
)
from task_4_llm.model.resume_data import ResumeData


class GeminiClient(BaseLLMClient):
    """Google Gemini API client.

    Args:
        api_key: Google AI API key. Falls back to
            ``GOOGLE_API_KEY`` environment variable.
        model: Model identifier to use.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
    ) -> None:
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError(
                "Install the google-genai package: "
                "pip install google-genai"
            ) from exc

        self._client = genai.Client(api_key=api_key)
        self._model: str = model

    async def extract(self, resume_text: str) -> ResumeData:
        """Extract resume data using the Gemini API.

        Args:
            resume_text: Raw text extracted from a resume PDF.

        Returns:
            Validated ResumeData instance.

        Raises:
            RuntimeError: If the API call or JSON parsing fails.
        """
        prompt: str = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Extract structured data from this resume:\n\n"
            f"{resume_text}"
        )

        try:
            # google-genai's generate_content is synchronous,
            # so we run it in a thread to keep the event loop free.
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model=self._model,
                contents=prompt,
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc

        return parse_llm_response(response.text)

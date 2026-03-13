"""Claude API client using the Anthropic SDK."""

from typing import Optional

from task_4_llm.client.base_llm_client import (
    BaseLLMClient,
    SYSTEM_PROMPT,
    parse_llm_response,
)
from task_4_llm.model.resume_data import ResumeData


class AnthropicClient(BaseLLMClient):
    """Claude API client using the Anthropic SDK.

    Args:
        api_key: Anthropic API key. Falls back to
            ``ANTHROPIC_API_KEY`` environment variable.
        model: Model identifier to use.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise ImportError(
                "Install the anthropic package: pip install anthropic"
            ) from exc

        self._client: AsyncAnthropic = AsyncAnthropic(api_key=api_key)
        self._model: str = model

    async def extract(self, resume_text: str) -> ResumeData:
        """Extract resume data using the Claude API.

        Args:
            resume_text: Raw text extracted from a resume PDF.

        Returns:
            Validated ResumeData instance.

        Raises:
            RuntimeError: If the API call or JSON parsing fails.
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                temperature=0.0,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Extract structured data from this resume:\n\n"
                            f"{resume_text}"
                        ),
                    }
                ],
            )
        except Exception as exc:
            raise RuntimeError(f"Anthropic API call failed: {exc}") from exc

        return parse_llm_response(response.content[0].text)

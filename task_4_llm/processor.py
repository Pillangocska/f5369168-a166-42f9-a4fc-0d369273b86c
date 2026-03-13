"""Core processing pipeline — PDF to structured JSON via LLM."""

from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
import asyncio
import logging

from task_4_llm.client.base_llm_client import BaseLLMClient
from task_4_llm.model.resume_data import ResumeData
from task_4_llm.pdf_reader import extract_text_from_pdf

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single resume.

    Attributes:
        pdf_path: Path to the source PDF.
        success: Whether extraction succeeded.
        output_path: Path to the written JSON file, if successful.
        elapsed_seconds: Wall-clock time for this resume.
        error: Error message if extraction failed.
    """

    pdf_path: Path
    success: bool
    output_path: Optional[Path] = None
    elapsed_seconds: float = 0.0
    error: Optional[str] = None


@dataclass
class BatchStats:
    """Aggregate statistics for a batch processing run.

    Attributes:
        total: Total number of PDFs attempted.
        succeeded: Number of successful extractions.
        failed: Number of failed extractions.
        results: Individual results per resume.
        total_elapsed_seconds: Total wall-clock time for the batch.
    """

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    results: list[ProcessingResult] = field(default_factory=list)
    total_elapsed_seconds: float = 0.0

    @property
    def median_time(self) -> Optional[float]:
        """Compute median processing time across successful results.

        Returns:
            Median time in seconds, or ``None`` if no results.
        """
        times: list[float] = sorted(
            r.elapsed_seconds for r in self.results if r.success
        )
        if not times:
            return None
        mid: int = len(times) // 2
        if len(times) % 2 == 0:
            return (times[mid - 1] + times[mid]) / 2
        return times[mid]


async def process_single_resume(
    pdf_path: Path,
    output_dir: Path,
    client: BaseLLMClient,
) -> ProcessingResult:
    """Process one resume PDF and write the result as JSON.

    Args:
        pdf_path: Path to the resume PDF file.
        output_dir: Directory to write the output JSON file.
        client: LLM client instance for extraction.

    Returns:
        A ``ProcessingResult`` describing the outcome.
    """
    start: float = perf_counter()

    try:
        logger.info("Extracting text from %s", pdf_path.name)
        text: str = await asyncio.to_thread(
            extract_text_from_pdf, pdf_path
        )

        logger.info(
            "Sending %s to LLM (%d chars)", pdf_path.name, len(text)
        )
        resume_data: ResumeData = await client.extract(text)

        output_path: Path = output_dir / f"{pdf_path.stem}.json"
        json_str: str = resume_data.model_dump_json(indent=2)
        output_path.write_text(json_str, encoding="utf-8")

        elapsed: float = perf_counter() - start
        logger.info(
            "Completed %s in %.2fs -> %s",
            pdf_path.name,
            elapsed,
            output_path.name,
        )

        return ProcessingResult(
            pdf_path=pdf_path,
            success=True,
            output_path=output_path,
            elapsed_seconds=elapsed,
        )

    except Exception as exc:
        elapsed = perf_counter() - start
        logger.error("Failed %s: %s", pdf_path.name, exc)

        return ProcessingResult(
            pdf_path=pdf_path,
            success=False,
            elapsed_seconds=elapsed,
            error=str(exc),
        )


async def process_batch(
    input_dir: Path,
    output_dir: Path,
    client: BaseLLMClient,
    concurrency: int = 5,
) -> BatchStats:
    """Process all PDF files in a directory concurrently.

    Args:
        input_dir: Directory containing resume PDF files.
        output_dir: Directory to write output JSON files.
        client: LLM client instance for extraction.
        concurrency: Maximum number of concurrent API calls.

    Returns:
        A ``BatchStats`` summarizing the run.

    Raises:
        FileNotFoundError: If input_dir does not exist.
        ValueError: If no PDF files are found.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    pdf_files: list[Path] = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Processing %d PDFs with concurrency=%d",
        len(pdf_files),
        concurrency,
    )

    batch_start: float = perf_counter()
    semaphore: asyncio.Semaphore = asyncio.Semaphore(concurrency)

    async def _limited(pdf_path: Path) -> ProcessingResult:
        """Wrap a single resume task behind the semaphore."""
        async with semaphore:
            return await process_single_resume(
                pdf_path, output_dir, client
            )

    tasks: list[asyncio.Task[ProcessingResult]] = [
        asyncio.create_task(_limited(pdf)) for pdf in pdf_files
    ]
    results: list[ProcessingResult] = await asyncio.gather(*tasks)

    stats: BatchStats = BatchStats(
        total=len(results),
        succeeded=sum(1 for r in results if r.success),
        failed=sum(1 for r in results if not r.success),
        results=results,
        total_elapsed_seconds=perf_counter() - batch_start,
    )

    return stats

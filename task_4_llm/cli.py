"""Command-line interface for the resume extractor."""

from pathlib import Path
import argparse
import asyncio
import logging
import sys

from task_4_llm.client import create_client, BaseLLMClient
from task_4_llm.processor import BatchStats, process_batch


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser.

    Returns:
        Configured ``ArgumentParser`` instance.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="resume-extractor",
        description=(
            "Extract structured data from resume PDFs using an LLM. "
            "Reads all .pdf files from the input directory and writes "
            "individual .json files to the output directory."
        ),
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Path to directory containing resume PDF files.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Output directory for JSON files. "
            "Defaults to <input_dir>/output."
        ),
    )
    parser.add_argument(
        "-p",
        "--provider",
        choices=["anthropic", "gemini"],
        default="anthropic",
        help="LLM provider to use (default: anthropic).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "API key for the provider. If omitted, reads from "
            "ANTHROPIC_API_KEY or GOOGLE_API_KEY env variable."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the default model for the chosen provider.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=5,
        help="Max concurrent API calls (default: 5).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging.",
    )
    return parser


def print_summary(stats: BatchStats) -> None:
    """Print a human-readable summary of the batch run.

    Args:
        stats: Aggregate statistics from the processing run.
    """
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    print(f"  Total resumes:   {stats.total}")
    print(f"  Succeeded:       {stats.succeeded}")
    print(f"  Failed:          {stats.failed}")
    print(f"  Total time:      {stats.total_elapsed_seconds:.2f}s")

    median: float | None = stats.median_time
    if median is not None:
        print(f"  Median time:     {median:.2f}s per resume")

    if stats.failed > 0:
        print("\nFailed files:")
        for result in stats.results:
            if not result.success:
                print(f"  - {result.pdf_path.name}: {result.error}")

    print()


async def async_main(args: argparse.Namespace) -> int:
    """Async entry point that runs the batch processor.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Exit code — 0 on success, 1 on failure.
    """
    output_dir: Path = args.output_dir or (args.input_dir / "output")

    try:
        client: BaseLLMClient = create_client(
            provider=args.provider,
            api_key=args.api_key,
            model=args.model,
        )
    except (ValueError, ImportError) as exc:
        print(f"Error initializing LLM client: {exc}", file=sys.stderr)
        return 1

    try:
        stats: BatchStats = await process_batch(
            input_dir=args.input_dir,
            output_dir=output_dir,
            client=client,
            concurrency=args.concurrency,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print_summary(stats)

    return 0 if stats.failed == 0 else 1


def main() -> None:
    """CLI entry point."""
    parser: argparse.ArgumentParser = build_parser()
    args: argparse.Namespace = parser.parse_args()

    log_level: int = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    exit_code: int = asyncio.run(async_main(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

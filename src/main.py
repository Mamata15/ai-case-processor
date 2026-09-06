"""Main workflow entry point."""

from src.batch_processor import process_batch
from src.config import settings
from src.llm_client import LLMClient
from src.logging_config import configure_logging


def main() -> None:
    """Run one configured batch and report its output location."""
    configure_logging(settings.log_level, settings.output_dir / "processing.log")
    report_path = process_batch(settings, LLMClient(settings))
    print(f"Batch complete. Report: {report_path}")
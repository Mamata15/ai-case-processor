"""Logging setup for command-line runs."""

import logging
from pathlib import Path
from typing import Optional


def configure_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Configure console logging and optionally a file handler."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
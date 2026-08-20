"""Logging setup — console + rotating file in %APPDATA%\\zzluxora\\logs.

Kept tiny and side-effect-free at import time; call setup_logging() once
from the app entry point.
"""
from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from zzluxora.config import default_data_dir

_LOGGER = logging.getLogger("zzluxora")


def setup_logging(level: int = logging.INFO, log_dir: Path | None = None) -> Path:
    """Configure root zzluxora logger. Returns the log file path."""
    root = logging.getLogger("zzluxora")
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    # Rotating file in AppData
    log_dir = log_dir or (default_data_dir() / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # Default for unhandled modules
    logging.getLogger("zzluxora.core").setLevel(level)
    logging.getLogger("zzluxora.services").setLevel(level)
    logging.getLogger("zzluxora.ui").setLevel(level)

    return log_file


def get_logger(name: str) -> logging.Logger:
    """Get a namespaced child logger: zzluxora.<name>."""
    return logging.getLogger(f"zzluxora.{name}")

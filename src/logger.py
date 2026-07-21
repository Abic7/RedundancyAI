"""Structured logging for RedundancyAI."""

import logging
import sys
from typing import Optional
from src.config import LOG_LEVEL

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Configure a logger with structured format.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level or LOG_LEVEL)

    # Only add handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Module-level logger
logger = setup_logger(__name__)

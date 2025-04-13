"""
Centralized logging configuration for the MLB Stats MCP project.
"""

import logging
import os
from typing import Optional


def setup_logging(logger_name: Optional[str] = None) -> logging.Logger:
    """
    Configure logging based on environment variables.

    Args:
        logger_name: Optional name for the logger. If None, returns root logger.

    Returns:
        Configured logger instance
    """
    # Get logging configuration from environment variables
    log_level = os.environ.get("MLB_STATS_LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("MLB_STATS_LOG_FILE", None)

    # Get the logger - either named or root
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()

    # Set the log level
    level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)8s - %(name)s - %(message)s"
    )

    # Clear existing handlers to avoid duplicate logs
    logger.handlers = []

    # Add handlers based on configuration
    if log_file:
        # File handler if log file is specified
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging configured at {log_level} level, writing to {log_file}")
    else:
        # Stream handler if no log file is specified
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        logger.info(
            f"MLB Stats API logging configured at {log_level} level, writing to stdout"
        )

    return logger

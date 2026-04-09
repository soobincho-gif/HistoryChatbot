"""Logging helper functions."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a module logger with a simple default configuration."""

    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

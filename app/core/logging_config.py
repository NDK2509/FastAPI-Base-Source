import logging
from logging import Formatter

from core.context import request_id


class ContextFilter(logging.Filter):
    """ "Provides request id parameter for the logger"""

    def filter(self, record):
        record.request_id = request_id.get()
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger configured for a specific module.
    Example: get_logger("jwt_handler") -> logs/jwt_handler.log
    """
    logger = logging.getLogger(name)

    if logger.handlers:  # Avoid duplicate handlers if called multiple times
        return logger

    # common formatter
    formatter = Formatter(
        "%(asctime)-15s - %(request_id)s - %(name)-5s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)s() ] - %(message)s"
    )

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addFilter(ContextFilter())

    return logger

import sys

from loguru import logger

from app.config import get_settings


def configure_logging() -> None:
    s = get_settings()
    logger.remove()
    logger.add(sys.stdout, level=s.log_level.upper(), backtrace=False, diagnose=False)

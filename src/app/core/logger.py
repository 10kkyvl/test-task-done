from pathlib import Path
from loguru import logger
import sys

BASE_DIR = Path(__file__).resolve().parents[3]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
)
logger.add(
    LOG_DIR / "app.log",
    level="DEBUG",
    rotation="50 MB",
    retention="30 days",
    compression="gz",
    enqueue=True,
)

logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    backtrace=True,
    diagnose=True,
)

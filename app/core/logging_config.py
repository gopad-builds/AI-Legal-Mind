import logging
import sys
from app.core.config import Settings

settings = Settings()


def setup_logging() -> None:
    # 1. Level: Show detailed logs in debug mode, otherwise only general info
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # 2. Format: Timestamp | Severity Level | File Name | Message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 3. Handlers: Print logs to the terminal (stdout) with the specified format.A handler decides where logs go. 
    # StreamHandler(sys.stdout) sends logs to your terminal console (you could later add a FileHandler to save them to a file).
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))

    # Apply configuration to the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate log lines
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)

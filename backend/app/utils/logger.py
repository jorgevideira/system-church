import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """Create and configure a named logger with a StreamHandler."""
    log = logging.getLogger(name)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.INFO)
    return log


logger = setup_logger("church-system")

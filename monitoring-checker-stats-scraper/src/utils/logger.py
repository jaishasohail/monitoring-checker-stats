import logging
import sys
from pathlib import Path
from typing import Union

def setup_logging(
    log_dir: Union[str, Path],
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure and return the root logger for the monitoring checker application.

    Logs go to both stdout and a rotating file under the given directory.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("monitoring_checker")
    if logger.handlers:
        # Logger already configured; just return it.
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_path / "app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized with directory %s", log_path)
    return logger
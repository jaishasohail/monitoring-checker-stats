import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from logging import Logger

def format_and_persist_metrics(
    metrics: List[Dict[str, Any]],
    output_path: Path,
    logger: Optional[Logger] = None,
    pretty: bool = True,
) -> None:
    """
    Serialize metrics to JSON and write them to the given output path.
    """
    if logger is None:
        class _Dummy:
            def debug(self, *_, **__): ...
            def info(self, *_, **__): ...
            def warning(self, *_, **__): ...
            def error(self, *_, **__): ...
        logger = _Dummy()  # type: ignore[assignment]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug("Writing %d metric records to %s", len(metrics), output_path)
    with output_path.open("w", encoding="utf-8") as f:
        if pretty:
            json.dump(metrics, f, indent=4, sort_keys=False)
        else:
            json.dump(metrics, f, separators=(",", ":"))

    logger.info("Successfully wrote metrics to %s", output_path)
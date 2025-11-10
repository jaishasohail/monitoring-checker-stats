from typing import Any, Dict, List, Optional
from logging import Logger

STATUS_ACTIVE = "active"
STATUS_WARNING = "warning"
STATUS_DOWN = "down"

def _determine_status(
    ok: bool,
    response_time_ms: Optional[int],
    warning_threshold_ms: int,
) -> str:
    if not ok:
        return STATUS_DOWN
    if response_time_ms is None:
        return STATUS_WARNING
    if response_time_ms >= warning_threshold_ms:
        return STATUS_WARNING
    return STATUS_ACTIVE

def parse_metrics(
    raw_results: List[Dict[str, Any]],
    warning_threshold_ms: int,
    logger: Optional[Logger] = None,
) -> List[Dict[str, Any]]:
    """
    Convert low-level collector output into structured monitoring metrics.

    Output schema:
      - resource_id
      - response_time           (int ms)
      - uptime_percentage       (float)
      - last_checked            (ISO timestamp)
      - status                  ("active" | "warning" | "down")
      - error_count             (int)
    """
    if logger is None:
        class _Dummy:
            def debug(self, *_, **__): ...
            def info(self, *_, **__): ...
            def warning(self, *_, **__): ...
            def error(self, *_, **__): ...
        logger = _Dummy()  # type: ignore[assignment]

    metrics: List[Dict[str, Any]] = []

    for result in raw_results:
        resource_id = result.get("resource_id")
        if not resource_id:
            logger.error("Skipping raw result without resource_id: %s", result)
            continue

        response_time_ms = result.get("response_time_ms")
        ok = bool(result.get("ok", False))
        last_checked = result.get("checked_at")
        error_message = result.get("error")
        error_count = 1 if error_message or not ok else 0

        status = _determine_status(ok, response_time_ms, warning_threshold_ms)
        uptime_percentage = 100.0 if ok else 0.0

        metric = {
            "resource_id": resource_id,
            "response_time": int(response_time_ms) if response_time_ms is not None else None,
            "uptime_percentage": float(uptime_percentage),
            "last_checked": last_checked,
            "status": status,
            "error_count": int(error_count),
        }

        logger.debug("Parsed metrics for '%s': %s", resource_id, metric)
        metrics.append(metric)

    return metrics
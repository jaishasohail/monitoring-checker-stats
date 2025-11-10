import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from requests import RequestException
from logging import Logger

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def collect_resource_stats(
    resources: List[Dict[str, Any]],
    timeout_seconds: int,
    logger: Optional[Logger] = None,
) -> List[Dict[str, Any]]:
    """
    Perform HTTP checks for each configured resource and collect low-level metrics.

    Each resource is expected to be a dict with at least:
      - id: unique identifier
      - url: HTTP/HTTPS endpoint to call
    """
    if logger is None:
        class _Dummy:
            def debug(self, *_, **__): ...
            def info(self, *_, **__): ...
            def warning(self, *_, **__): ...
            def error(self, *_, **__): ...
        logger = _Dummy()  # type: ignore[assignment]

    results: List[Dict[str, Any]] = []

    for resource in resources:
        resource_id = resource.get("id") or resource.get("resource_id")
        url = resource.get("url")
        if not resource_id or not url:
            logger.error("Skipping invalid resource definition: %s", resource)
            continue

        logger.info("Checking resource '%s' at %s", resource_id, url)
        started_at = time.monotonic()
        checked_at = _utc_now_iso()
        status_code: Optional[int] = None
        error_message: Optional[str] = None
        ok = False

        try:
            response = requests.get(url, timeout=timeout_seconds)
            elapsed_ms = int((time.monotonic() - started_at) * 1000)
            status_code = response.status_code
            ok = 200 <= status_code < 400
            logger.debug(
                "Resource '%s' responded with %s in %dms",
                resource_id,
                status_code,
                elapsed_ms,
            )
        except RequestException as exc:
            elapsed_ms = int((time.monotonic() - started_at) * 1000)
            error_message = str(exc)
            logger.warning(
                "Error while checking resource '%s': %s (elapsed %dms)",
                resource_id,
                error_message,
                elapsed_ms,
            )

        result: Dict[str, Any] = {
            "resource_id": resource_id,
            "url": url,
            "response_time_ms": elapsed_ms,
            "status_code": status_code,
            "ok": ok,
            "error": error_message,
            "checked_at": checked_at,
        }
        results.append(result)

    return results
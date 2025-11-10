import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from collectors.metrics_parser import (  # noqa: E402
    STATUS_ACTIVE,
    STATUS_DOWN,
    STATUS_WARNING,
    parse_metrics,
)

class DummyLogger:
    def __init__(self) -> None:
        self.messages: List[str] = []

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(msg % args if args else msg)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(msg % args if args else msg)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(msg % args if args else msg)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(msg % args if args else msg)

def test_parse_metrics_status_and_uptime() -> None:
    raw_results = [
        {
            "resource_id": "fast_ok",
            "response_time_ms": 100,
            "ok": True,
            "checked_at": "2025-11-10T08:45:00Z",
            "error": None,
        },
        {
            "resource_id": "slow_ok",
            "response_time_ms": 500,
            "ok": True,
            "checked_at": "2025-11-10T08:46:00Z",
            "error": None,
        },
        {
            "resource_id": "down",
            "response_time_ms": 900,
            "ok": False,
            "checked_at": "2025-11-10T08:47:00Z",
            "error": "Timeout",
        },
    ]

    logger = DummyLogger()
    metrics = parse_metrics(raw_results, warning_threshold_ms=300, logger=logger)

    assert len(metrics) == 3

    fast_ok = next(m for m in metrics if m["resource_id"] == "fast_ok")
    slow_ok = next(m for m in metrics if m["resource_id"] == "slow_ok")
    down = next(m for m in metrics if m["resource_id"] == "down")

    assert fast_ok["status"] == STATUS_ACTIVE
    assert fast_ok["uptime_percentage"] == 100.0
    assert fast_ok["error_count"] == 0

    assert slow_ok["status"] == STATUS_WARNING
    assert slow_ok["uptime_percentage"] == 100.0
    assert slow_ok["error_count"] == 0

    assert down["status"] == STATUS_DOWN
    assert down["uptime_percentage"] == 0.0
    assert down["error_count"] == 1
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from collectors.resource_collector import collect_resource_stats  # noqa: E402

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

@patch("collectors.resource_collector.requests.get")
def test_collect_resource_stats_success(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    resources = [
        {"id": "test_resource", "url": "https://example.com/health"},
    ]

    logger = DummyLogger()
    results = collect_resource_stats(resources=resources, timeout_seconds=2, logger=logger)

    assert len(results) == 1
    result: Dict[str, Any] = results[0]
    assert result["resource_id"] == "test_resource"
    assert result["url"] == "https://example.com/health"
    assert result["status_code"] == 200
    assert result["ok"] is True
    assert result["error"] is None
    assert isinstance(result["response_time_ms"], int)
    assert result["response_time_ms"] >= 0
    assert isinstance(result["checked_at"], str)

@patch("collectors.resource_collector.requests.get")
def test_collect_resource_stats_failure(mock_get: MagicMock) -> None:
    mock_get.side_effect = Exception("Network error")

    resources = [
        {"id": "failing_resource", "url": "https://example.com/down"},
    ]

    logger = DummyLogger()
    results = collect_resource_stats(resources=resources, timeout_seconds=1, logger=logger)

    assert len(results) == 1
    result: Dict[str, Any] = results[0]
    assert result["resource_id"] == "failing_resource"
    assert result["status_code"] is None
    assert result["ok"] is False
    assert result["error"] is not None
    assert isinstance(result["response_time_ms"], int)
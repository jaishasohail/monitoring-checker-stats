import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from collectors.resource_collector import collect_resource_stats
from collectors.metrics_parser import parse_metrics
from utils.logger import setup_logging
from utils.data_formatter import format_and_persist_metrics

def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def resolve_paths(config: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    resolved = dict(config)

    output_path = config.get("output_path", "data/sample_output.json")
    resolved["output_path"] = (project_root / output_path).resolve()

    log_dir = config.get("log_dir", "data/logs")
    resolved["log_dir"] = (project_root / log_dir).resolve()

    return resolved

def run_monitor(config_path: Path) -> int:
    project_root = Path(__file__).resolve().parents[1]
    config = load_config(config_path)
    config = resolve_paths(config, project_root)

    logger = setup_logging(config["log_dir"])

    resources = config.get("resources", [])
    if not resources:
        logger.error("No resources defined in configuration. Exiting.")
        return 1

    timeout = config.get("timeout_seconds", 5)
    warning_threshold_ms = config.get("warning_response_time_ms", 300)

    logger.info("Starting monitoring checker stats scraper")
    logger.debug("Loaded configuration: %s", config)

    raw_results = collect_resource_stats(
        resources=resources,
        timeout_seconds=timeout,
        logger=logger,
    )

    if not raw_results:
        logger.error("No metrics collected from resources.")
        return 1

    metrics = parse_metrics(
        raw_results=raw_results,
        warning_threshold_ms=warning_threshold_ms,
        logger=logger,
    )

    output_path = Path(config["output_path"])
    format_and_persist_metrics(
        metrics=metrics,
        output_path=output_path,
        logger=logger,
    )

    logger.info("Monitoring run completed successfully. Output saved to %s", output_path)
    return 0

def parse_args() -> argparse.Namespace:
    default_config = Path(__file__).resolve().parent / "config" / "settings.json"
    parser = argparse.ArgumentParser(
        description="Monitoring Checker Stats Scraper",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=default_config,
        help=f"Path to settings JSON file (default: {default_config})",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    try:
        exit_code = run_monitor(args.config)
    except Exception as exc:  # noqa: BLE001
        # Fallback logger in case setup_logging failed
        print(f"Fatal error running monitoring checker: {exc}")
        raise
    else:
        if exit_code != 0:
            raise SystemExit(exit_code)

if __name__ == "__main__":
    main()
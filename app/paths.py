from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


APP_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TZ = "Asia/Shanghai"


def runtime_date() -> str:
    explicit = os.environ.get("RUN_DATE")
    if explicit:
        return explicit
    tz = ZoneInfo(os.environ.get("TZ", DEFAULT_TZ))
    return datetime.now(tz).strftime("%Y-%m-%d")


def output_root() -> Path:
    return Path(os.environ.get("OUTPUT_ROOT", APP_ROOT / "output")).expanduser().resolve()


def log_root() -> Path:
    return Path(os.environ.get("LOG_ROOT", APP_ROOT / "logs")).expanduser().resolve()


def tmp_root() -> Path:
    return Path(os.environ.get("TMP_ROOT", APP_ROOT / "tmp")).expanduser().resolve()


def state_root() -> Path:
    return Path(os.environ.get("STATE_ROOT", APP_ROOT / "state")).expanduser().resolve()


def ensure_runtime_dirs() -> None:
    for path in (output_root(), log_root(), tmp_root(), state_root()):
        path.mkdir(parents=True, exist_ok=True)


def brief_stem(run_date: str) -> str:
    return f"ai-tech-daily-brief-{run_date}"


def brief_json_path(run_date: str) -> Path:
    return output_root() / f"{brief_stem(run_date)}.json"


def brief_html_path(run_date: str) -> Path:
    return output_root() / f"{brief_stem(run_date)}.html"


def brief_pdf_path(run_date: str) -> Path:
    return output_root() / f"{brief_stem(run_date)}.pdf"


def metadata_path(run_date: str) -> Path:
    return log_root() / f"summary-model-{run_date}.json"


def push_sent_marker_path(run_date: str) -> Path:
    return state_root() / f"{run_date}.push.sent"


def push_failed_marker_path(run_date: str) -> Path:
    return state_root() / f"{run_date}.push.failed"

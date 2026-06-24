#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SUMMARY_MODEL = "Pro/moonshotai/Kimi-K2.6"
SUMMARY_PROVIDER = "moonshotai"
SUMMARY_API_URL = "https://api.siliconflow.cn/v1/chat/completions"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read_runtime_env() -> dict[str, str]:
    model = os.environ.get("SUMMARY_MODEL", SUMMARY_MODEL)
    provider = os.environ.get("SUMMARY_MODEL_PROVIDER", SUMMARY_PROVIDER)
    api_key = os.environ.get("SUMMARY_MODEL_API_KEY", "")
    api_url = os.environ.get("SUMMARY_MODEL_API_URL", "")
    base_url = os.environ.get("SUMMARY_MODEL_BASE_URL", "")

    if model != SUMMARY_MODEL:
        fail(f"summary model must be {SUMMARY_MODEL}")
    if provider != SUMMARY_PROVIDER:
        fail(f"summary model provider must be {SUMMARY_PROVIDER}")
    if not api_key:
        fail("summary model api key missing")
    if not api_url and not base_url:
        fail("summary model api url missing")

    env_map = {
        "SUMMARY_MODEL": model,
        "SUMMARY_MODEL_PROVIDER": provider,
        "SUMMARY_MODEL_API_KEY": api_key,
        "SUMMARY_MODEL_API_URL": api_url,
        "SUMMARY_MODEL_BASE_URL": base_url,
    }
    summary_model_endpoint(env_map)
    return env_map


def summary_model_endpoint(env_map: dict[str, str]) -> str:
    api_url = env_map.get("SUMMARY_MODEL_API_URL", "").strip()
    if api_url:
        endpoint = api_url.rstrip("/")
        if endpoint != SUMMARY_API_URL:
            fail(f"summary model api url must be {SUMMARY_API_URL}")
        return endpoint

    base_url = env_map.get("SUMMARY_MODEL_BASE_URL", "").strip()
    if not base_url:
        fail("summary model api url missing")
    if base_url.rstrip("/").endswith("/chat/completions"):
        endpoint = base_url.rstrip("/")
    else:
        endpoint = urllib.parse.urljoin(base_url.rstrip("/") + "/", "chat/completions")
    if endpoint != SUMMARY_API_URL:
        fail(f"summary model api url must be {SUMMARY_API_URL}")
    return endpoint


def write_metadata(output_path: Path, env_map: dict[str, str]) -> None:
    payload = {
        "summary_model": env_map["SUMMARY_MODEL"],
        "summary_model_provider": env_map["SUMMARY_MODEL_PROVIDER"],
        "summary_model_api_url_configured": bool(env_map["SUMMARY_MODEL_API_URL"]),
        "summary_model_base_url_configured": bool(env_map["SUMMARY_MODEL_BASE_URL"]),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def connectivity_check(env_map: dict[str, str]) -> None:
    endpoint = summary_model_endpoint(env_map)
    payload = {
        "model": env_map["SUMMARY_MODEL"],
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "temperature": 0,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {env_map['SUMMARY_MODEL_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status >= 400:
                fail(f"summary model connectivity check failed with status {response.status}")
    except urllib.error.HTTPError as exc:
        fail(f"summary model connectivity check failed with status {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"summary model connectivity check failed: {exc.reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate summary model env for ai-tech-daily-brief.")
    parser.add_argument("--write-metadata", help="Optional JSON file path for model metadata")
    parser.add_argument(
        "--check-connectivity",
        action="store_true",
        help="Run a minimal OpenAI-compatible API call against SUMMARY_MODEL_API_URL or SUMMARY_MODEL_BASE_URL",
    )
    args = parser.parse_args()

    env_map = read_runtime_env()

    if args.write_metadata:
        write_metadata(Path(args.write_metadata), env_map)

    if args.check_connectivity:
        connectivity_check(env_map)

    print("summary model validation ok")


if __name__ == "__main__":
    main()

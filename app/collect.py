from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.build_digest import main as build_digest_main
from app.paths import (
    brief_html_path,
    brief_json_path,
    brief_pdf_path,
    ensure_runtime_dirs,
    metadata_path,
    runtime_date,
)
from app.validate_summary_model import read_runtime_env, write_metadata


AI_KEYWORDS = [
    "openai",
    "chatgpt",
    "gpt",
    "anthropic",
    "claude",
    "gemini",
    "deepmind",
    "deepseek",
    "qwen",
    "通义",
    "zhipu",
    "glm",
    "doubao",
    "seed",
    "llm",
    "agent",
    "rag",
    "inference",
    "model",
    "benchmark",
]

FRONTIER_VENDOR_KEYWORDS = [
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepmind",
    "deepseek",
    "qwen",
    "alibaba",
    "zhipu",
    "glm",
    "doubao",
    "bytedance",
    "meta ai",
]


def fetch_json(url: str, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ai-tech-daily-brief/1.0",
            **(headers or {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def clamp_score(value: float) -> int:
    return max(1, min(5, int(round(value))))


def freshness_score(dt: datetime) -> int:
    age_hours = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if age_hours <= 6:
        return 5
    if age_hours <= 12:
        return 4
    if age_hours <= 18:
        return 3
    return 2


def keyword_score(text: str) -> int:
    text_l = text.lower()
    hits = sum(1 for keyword in AI_KEYWORDS if keyword in text_l)
    return clamp_score(1 + min(hits, 4))


def vendor_score(text: str) -> int:
    text_l = text.lower()
    if any(keyword in text_l for keyword in FRONTIER_VENDOR_KEYWORDS):
        return 5
    if any(keyword in text_l for keyword in ["model", "llm", "agent", "inference"]):
        return 4
    return 3


def clean_title(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def org_from_repo(full_name: str) -> str:
    if "/" not in full_name:
        return "GitHub"
    return full_name.split("/", 1)[0]


def hn_items(start_ts: int) -> list[dict]:
    query = urllib.parse.quote("AI OR OpenAI OR Anthropic OR Gemini OR LLM OR agent")
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        f"?query={query}&tags=story&numericFilters=created_at_i>{start_ts}&hitsPerPage=50"
    )
    payload = fetch_json(url)
    items: list[dict] = []
    for hit in payload.get("hits", []):
        title = clean_title(hit.get("title") or hit.get("story_title") or "")
        if not title:
            continue
        created = datetime.fromtimestamp(int(hit["created_at_i"]), timezone.utc)
        text = f"{title} {hit.get('url') or ''}"
        if keyword_score(text) < 2:
            continue
        points = float(hit.get("points") or 0)
        comments = float(hit.get("num_comments") or 0)
        heat = clamp_score(1 + points / 80 + comments / 50)
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        items.append(
            {
                "title": title,
                "date": created.date().isoformat(),
                "organization": "Hacker News",
                "type": "discussion",
                "summary": f"Hacker News 在过去 24 小时出现相关讨论：{title}",
                "why_it_matters": "HN 讨论通常能较早暴露开发者采用、质疑点和工程影响。",
                "heat_reason": f"HN points={int(points)}，comments={int(comments)}。",
                "primary_link": url,
                "discovery_channel": "Hacker News",
                "heat": heat,
                "freshness": freshness_score(created),
                "strategic_value": keyword_score(text),
                "source_quality": 3 if hit.get("url") else 2,
                "platform_signal": heat,
                "frontier_vendor_fit": vendor_score(text),
            }
        )
    return items


def github_items(start_date: str) -> list[dict]:
    query = urllib.parse.quote(f"llm OR ai OR agent OR inference OR rag created:>{start_date}")
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=30"
    headers = {}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    payload = fetch_json(url, headers)
    items: list[dict] = []
    for repo in payload.get("items", []):
        full_name = repo.get("full_name") or repo.get("name") or "GitHub repository"
        title = clean_title(full_name)
        description = clean_title(repo.get("description") or "")
        created = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
        stars = float(repo.get("stargazers_count") or 0)
        forks = float(repo.get("forks_count") or 0)
        text = f"{title} {description}"
        if keyword_score(text) < 2:
            continue
        heat = clamp_score(1 + stars / 250 + forks / 100)
        items.append(
            {
                "title": title,
                "date": created.date().isoformat(),
                "organization": org_from_repo(full_name),
                "type": "repository",
                "summary": description or f"{full_name} 是过去 24 小时内新出现的 AI 相关 GitHub 仓库。",
                "why_it_matters": "新仓库的 star/fork 增长可作为开发者兴趣和工具采用的早期信号。",
                "heat_reason": f"GitHub stars={int(stars)}，forks={int(forks)}。",
                "primary_link": repo.get("html_url"),
                "discovery_channel": "GitHub",
                "heat": heat,
                "freshness": freshness_score(created),
                "strategic_value": keyword_score(text),
                "source_quality": 4,
                "platform_signal": heat,
                "frontier_vendor_fit": vendor_score(text),
            }
        )
    return items


def x_items() -> list[dict]:
    # X needs an approved API credential and endpoint policy. Keep it explicit instead
    # of pretending the public web can reliably supply a production feed.
    if not os.environ.get("X_BEARER_TOKEN"):
        return []
    raise NotImplementedError("X source is not implemented; configure a dedicated source adapter before enabling it")


def dedupe(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = (item.get("primary_link") or item["title"]).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def collect_items() -> list[dict]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    start_ts = int(start.timestamp())
    start_date = start.date().isoformat()

    collected: list[dict] = []
    errors: list[str] = []
    for name, getter in (
        ("hacker-news", lambda: hn_items(start_ts)),
        ("github", lambda: github_items(start_date)),
        ("x", x_items),
    ):
        try:
            collected.extend(getter())
        except NotImplementedError as exc:
            errors.append(f"{name}: {exc}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            errors.append(f"{name}: {exc}")

    if errors:
        print("source warnings:", "; ".join(errors), file=sys.stderr)

    return dedupe(collected)


def write_json(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    ensure_runtime_dirs()
    run_date = runtime_date()
    env_map = read_runtime_env()
    write_metadata(metadata_path(run_date), env_map)

    items = collect_items()
    json_path = brief_json_path(run_date)
    html_path = brief_html_path(run_date)
    pdf_path = brief_pdf_path(run_date)
    write_json(json_path, items)

    old_argv = sys.argv[:]
    try:
        sys.argv = [
            "build_digest.py",
            str(json_path),
            "--date",
            run_date,
            "--output-html",
            str(html_path),
            "--output-pdf",
            str(pdf_path),
        ]
        build_digest_main()
    finally:
        sys.argv = old_argv

    print(f"brief json: {json_path}")
    print(f"brief html: {html_path}")
    print(f"brief pdf: {pdf_path}")
    print(f"items: {len(items)}")


if __name__ == "__main__":
    main()

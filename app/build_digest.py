#!/usr/bin/env python3
"""
根据标准化 AI 新闻条目生成 Top 10 HTML 简报，并可转换为 PDF。

输入 JSON 结构：
[
  {
    "title": "...",
    "date": "2026-05-20",
    "organization": "OpenAI",
    "type": "model",
    "summary": "...",
    "content_intro": "...",
    "primary_link": "https://...",
    "discovery_channel": "GitHub",
    "stars": 0,
    "forks": 0,
    "heat": 5,
    "freshness": 5,
    "strategic_value": 4,
    "source_quality": 5,
    "platform_signal": 5,
    "frontier_vendor_fit": 5
  }
]
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import tempfile
from pathlib import Path


def weighted_score(item: dict) -> float:
    return (
        float(item["heat"]) * 0.20
        + float(item["freshness"]) * 0.20
        + float(item["strategic_value"]) * 0.25
        + float(item["source_quality"]) * 0.15
        + float(item["platform_signal"]) * 0.10
        + float(item.get("frontier_vendor_fit", 3)) * 0.10
    )


def priority(score: float) -> str:
    if score >= 4.2:
        return "P1"
    if score >= 3.4:
        return "P2"
    return "P3"


def ranked_top_items(items: list[dict], limit: int = 10) -> list[dict]:
    ranked = sorted(
        items,
        key=lambda item: (
            float(item.get("stars") or 0),
            float(item.get("forks") or 0),
            float(item["heat"]),
            weighted_score(item),
            float(item["platform_signal"]),
            float(item.get("frontier_vendor_fit", 3)),
            float(item["source_quality"]),
            float(item["freshness"]),
            item["date"],
        ),
        reverse=True,
    )
    return ranked[:limit]


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def render_card(index: int, item: dict) -> str:
    title = esc(item["title"])
    org = esc(item.get("organization", "AI"))
    item_type = esc(item.get("type", "news"))
    date = esc(item["date"])
    channel = esc(item["discovery_channel"])
    source = esc(item["primary_link"])
    summary = esc(item["summary"])
    repo_description = esc(item.get("repo_description") or item.get("content_intro") or item.get("summary") or "")
    stars = int(item.get("stars") or 0)
    forks = int(item.get("forks") or 0)

    return f"""
      <article class="card">
        <div class="card-glow"></div>
        <header class="card-head">
          <div class="rank">#{index:02d}</div>
          <div>
            <div class="meta-row">
              <span>{org}</span>
              <span>{item_type}</span>
              <span>{date}</span>
            </div>
            <h2>{title}</h2>
          </div>
        </header>
        <p class="summary">{summary}</p>
        <div class="insight">
          <strong>仓库描述</strong>
          <p>{repo_description}</p>
        </div>
        <div class="repo-stats"><span>Stars {stars}</span><span>Forks {forks}</span></div>
        <footer>
          <span class="channel">{channel}</span>
          <a href="{source}">{source}</a>
        </footer>
      </article>
    """


def build_html(items: list[dict], digest_date: str) -> str:
    top_items = ranked_top_items(items, 10)
    cards = "\n".join(render_card(index, item) for index, item in enumerate(top_items, start=1))
    count_note = ""
    if len(top_items) < 10:
        count_note = f"<p class=\"shortfall\">可信候选不足 10 条，本期仅纳入 {len(top_items)} 条；未使用旧闻补位。</p>"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI 技术每日简报 {esc(digest_date)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #000;
      --panel: rgba(15, 23, 42, 0.88);
      --panel-2: rgba(2, 6, 23, 0.92);
      --line: rgba(148, 163, 184, 0.22);
      --text: #f8fafc;
      --muted: #94a3b8;
      --blue: #1d9bf0;
      --cyan: #22d3ee;
      --green: #34d399;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 20% 0%, rgba(29, 155, 240, 0.20), transparent 30%),
        linear-gradient(180deg, #000 0%, #05080f 45%, #020617 100%);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    .phone {{
      width: min(430px, 100%);
      margin: 0 auto;
      padding: 18px 14px 28px;
    }}
    .hero {{
      padding: 16px 4px 14px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      color: var(--cyan);
      font-size: 12px;
      letter-spacing: 0;
      font-weight: 700;
    }}
    h1 {{
      margin: 8px 0 8px;
      font-size: 30px;
      line-height: 1.08;
      letter-spacing: 0;
    }}
    .subtitle, .shortfall {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }}
    .card {{
      position: relative;
      overflow: hidden;
      margin: 10px 0;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(180deg, var(--panel), var(--panel-2));
      page-break-inside: auto;
      break-inside: auto;
      box-shadow: 0 16px 48px rgba(0, 0, 0, 0.32);
    }}
    .card-glow {{
      position: absolute;
      inset: -80px -80px auto auto;
      width: 150px;
      height: 150px;
      background: radial-gradient(circle, rgba(34, 211, 238, 0.22), transparent 62%);
      pointer-events: none;
    }}
    .card-head {{
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: 52px 1fr;
      gap: 12px;
      align-items: start;
    }}
    .rank {{
      display: grid;
      place-items: center;
      width: 48px;
      height: 48px;
      border-radius: 16px;
      background: linear-gradient(135deg, var(--blue), var(--cyan));
      color: white;
      font-weight: 800;
      font-size: 15px;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.3;
    }}
    .badge, .channel {{
      color: #e0f2fe;
      border: 1px solid rgba(56, 189, 248, 0.35);
      background: rgba(29, 155, 240, 0.16);
      border-radius: 999px;
      padding: 2px 7px;
      font-weight: 700;
    }}
    h2 {{
      margin: 7px 0 0;
      font-size: 18px;
      line-height: 1.32;
      letter-spacing: 0;
    }}
    .summary {{
      margin: 10px 0 9px;
      font-size: 14px;
      line-height: 1.55;
    }}
    .insight, .heat {{
      border-left: 3px solid var(--blue);
      padding-left: 10px;
      margin: 8px 0;
    }}
    .heat {{ border-left-color: var(--green); }}
    strong {{
      display: block;
      margin-bottom: 4px;
      color: #e2e8f0;
      font-size: 12px;
    }}
    .insight p, .heat p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}
    .repo-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 8px 0;
      color: #e2e8f0;
      font-size: 12px;
      font-weight: 700;
    }}
    .repo-stats span {{
      border: 1px solid rgba(148, 163, 184, 0.24);
      border-radius: 999px;
      padding: 3px 8px;
      background: rgba(15, 23, 42, 0.72);
    }}
    footer {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
      font-size: 12px;
    }}
    a {{
      color: #7dd3fc;
      overflow-wrap: anywhere;
      text-decoration: none;
    }}
    @media print {{
      body {{ background: #000; }}
      .phone {{ width: 430px; }}
      .card {{
        box-shadow: none;
        margin: 10px 0;
        page-break-inside: auto;
        break-inside: auto;
      }}
    }}
  </style>
</head>
<body>
  <main class="phone">
    <section class="hero">
      <div class="eyebrow">PAST 24 HOURS · TOP 10</div>
      <h1>AI 技术每日简报</h1>
      <p class="subtitle">{esc(digest_date)}｜按 Stars / Forks 从高到低排序｜GitHub · Hacker News</p>
      <p class="subtitle">热度依据：GitHub 展示 Stars 与 Forks；Hacker News 条目按 points 与 comments 参与排序。</p>
      {count_note}
    </section>
    {cards}
  </main>
</body>
</html>
"""


def write_pdf_with_playwright(html_path: Path, pdf_path: Path) -> None:
    script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const page = await browser.newPage({{ viewport: {{ width: 430, height: 1200 }}, deviceScaleFactor: 2 }});
  await page.goto('file://{html_path.resolve()}', {{ waitUntil: 'networkidle' }});
  await page.pdf({{
    path: '{pdf_path.resolve()}',
    width: '430px',
    height: '1800px',
    printBackground: true,
    margin: {{ top: '0px', right: '0px', bottom: '0px', left: '0px' }}
  }});
  await browser.close();
}})().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["node", str(script_path)], check=True)
    finally:
        script_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 AI 每日 Top 10 HTML/PDF 简报。")
    parser.add_argument("input_json", help="标准化条目 JSON 文件路径")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD 格式的简报日期")
    parser.add_argument("--output-html", required=True, help="输出 HTML 路径")
    parser.add_argument("--output-pdf", help="可选输出 PDF 路径，需要本机可用 Playwright")
    args = parser.parse_args()

    items = json.loads(Path(args.input_json).read_text())
    html_doc = build_html(items, args.date)
    html_path = Path(args.output_html)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_doc)

    if args.output_pdf:
        pdf_path = Path(args.output_pdf)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        write_pdf_with_playwright(html_path, pdf_path)


if __name__ == "__main__":
    main()

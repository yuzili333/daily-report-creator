from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.paths import (
    DEFAULT_TZ,
    brief_pdf_path,
    ensure_runtime_dirs,
    push_failed_marker_path,
    push_sent_marker_path,
    runtime_date,
)
from app.smtp_delivery import build_message, send_message


def marker_payload(status: str, run_date: str, detail: str = "") -> str:
    now = datetime.now(ZoneInfo(DEFAULT_TZ)).isoformat(timespec="seconds")
    lines = [
        f"status={status}",
        f"date={run_date}",
        f"timestamp={now}",
    ]
    if detail:
        lines.append(f"detail={detail}")
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_runtime_dirs()
    run_date = runtime_date()
    pdf_path = brief_pdf_path(run_date)

    sent_marker = push_sent_marker_path(run_date)
    failed_marker = push_failed_marker_path(run_date)
    if sent_marker.exists():
        print(f"push already sent for {run_date}: {sent_marker}")
        return

    if not pdf_path.is_file():
        failed_marker.write_text(marker_payload("failed", run_date, f"today brief pdf missing: {pdf_path}"))
        raise SystemExit(f"today brief pdf missing: {pdf_path}")
    if pdf_path.stat().st_size == 0:
        failed_marker.write_text(marker_payload("failed", run_date, f"today brief pdf is empty: {pdf_path}"))
        raise SystemExit(f"today brief pdf is empty: {pdf_path}")

    subject = f"AI 技术每日简报 | {run_date} | Top 10 热点"
    body = "\n".join(
        [
            "今日 AI 技术每日简报已生成，附件为 PDF。",
            "",
            "范围：过去 24 小时",
            "内容：按热度排序的 Top 10 AI 资讯",
            "",
        ]
    )
    try:
        send_message(build_message(subject, body, pdf_path))
    except Exception as exc:
        failed_marker.write_text(marker_payload("failed", run_date, f"{type(exc).__name__}: {exc}"))
        raise

    failed_marker.unlink(missing_ok=True)
    sent_marker.write_text(marker_payload("sent", run_date, f"pdf={pdf_path}"))
    print(f"sent {pdf_path} to configured recipient")


if __name__ == "__main__":
    main()

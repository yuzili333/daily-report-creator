from __future__ import annotations

from app.paths import brief_pdf_path, ensure_runtime_dirs, runtime_date
from app.smtp_delivery import build_message, send_message


def main() -> None:
    ensure_runtime_dirs()
    run_date = runtime_date()
    pdf_path = brief_pdf_path(run_date)
    if not pdf_path.is_file():
        raise SystemExit(f"today brief pdf missing: {pdf_path}")

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
    send_message(build_message(subject, body, pdf_path))
    print(f"sent {pdf_path} to configured recipient")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path


def smtp_config() -> dict[str, str]:
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.163.com"),
        "port": os.environ.get("SMTP_PORT", "465"),
        "use_tls": os.environ.get("SMTP_USE_TLS", "true").lower(),
        "username": os.environ["SMTP_USERNAME"],
        "password": os.environ["SMTP_PASSWORD"],
        "mail_from": os.environ["MAIL_FROM"],
        "mail_to": os.environ["MAIL_TO"],
    }


def smtp_login() -> smtplib.SMTP:
    cfg = smtp_config()
    port = int(cfg["port"])
    context = ssl.create_default_context()

    if port == 465 or cfg["use_tls"] in {"ssl", "true"}:
        server: smtplib.SMTP = smtplib.SMTP_SSL(cfg["host"], port, timeout=30, context=context)
    else:
        server = smtplib.SMTP(cfg["host"], port, timeout=30)
        if cfg["use_tls"] in {"starttls", "true", "1", "yes"}:
            server.starttls(context=context)

    server.login(cfg["username"], cfg["password"])
    return server


def build_message(subject: str, body: str, attachment: Path | None = None) -> EmailMessage:
    cfg = smtp_config()
    msg = EmailMessage(policy=SMTP)
    msg["From"] = cfg["mail_from"]
    msg["To"] = cfg["mail_to"]
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment:
        attachment = attachment.resolve()
        ctype, _ = mimetypes.guess_type(str(attachment))
        maintype, subtype = (ctype or "application/pdf").split("/", 1)
        msg.add_attachment(
            attachment.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=attachment.name,
        )

    return msg


def send_message(msg: EmailMessage) -> None:
    cfg = smtp_config()
    with smtp_login() as server:
        server.send_message(msg, from_addr=cfg["mail_from"], to_addrs=[cfg["mail_to"]])


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate 163 SMTP or send test messages.")
    parser.add_argument("--test-plain", action="store_true", help="Send a plain-text test email")
    parser.add_argument("--test-attachment", help="Send a test email with this PDF attached")
    args = parser.parse_args()

    if args.test_attachment:
        attachment = Path(args.test_attachment)
        if not attachment.is_file():
            raise SystemExit(f"attachment not found: {attachment}")
        msg = build_message(
            "AI 技术每日简报 SMTP 附件测试",
            "这是一封 163 SMTP PDF 附件发送测试邮件。",
            attachment,
        )
        send_message(msg)
        print("smtp attachment test sent")
        return

    if args.test_plain:
        msg = build_message("AI 技术每日简报 SMTP 测试", "这是一封 163 SMTP 纯文本测试邮件。")
        send_message(msg)
        print("smtp plain test sent")
        return

    with smtp_login():
        print("smtp validation ok")


if __name__ == "__main__":
    main()

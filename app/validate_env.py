from __future__ import annotations

import os
import sys

from app.validate_summary_model import summary_model_endpoint


REQUIRED_ENV = [
    "SUMMARY_MODEL",
    "SUMMARY_MODEL_PROVIDER",
    "SUMMARY_MODEL_API_KEY",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "MAIL_FROM",
    "MAIL_TO",
]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def validate_env() -> None:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        fail("missing required env vars: " + ", ".join(missing))

    if os.environ["SUMMARY_MODEL"] != "Pro/moonshotai/Kimi-K2.6":
        fail("SUMMARY_MODEL must be Pro/moonshotai/Kimi-K2.6")

    if os.environ["SUMMARY_MODEL_PROVIDER"] != "moonshotai":
        fail("SUMMARY_MODEL_PROVIDER must be moonshotai")

    if not os.environ.get("SUMMARY_MODEL_API_URL") and not os.environ.get("SUMMARY_MODEL_BASE_URL"):
        fail("SUMMARY_MODEL_API_URL or SUMMARY_MODEL_BASE_URL is required")
    summary_model_endpoint(
        {
            "SUMMARY_MODEL_API_URL": os.environ.get("SUMMARY_MODEL_API_URL", ""),
            "SUMMARY_MODEL_BASE_URL": os.environ.get("SUMMARY_MODEL_BASE_URL", ""),
        }
    )

    if os.environ["SMTP_HOST"] != "smtp.163.com":
        fail("SMTP_HOST must be smtp.163.com")

    if os.environ["MAIL_FROM"] != os.environ["SMTP_USERNAME"]:
        fail("MAIL_FROM must match SMTP_USERNAME for 163 SMTP")

    port = os.environ["SMTP_PORT"]
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower()
    if port == "465" and use_tls not in {"true", "ssl", "1", "yes"}:
        fail("SMTP_PORT=465 requires SMTP_USE_TLS=true or ssl")
    if port == "587" and use_tls not in {"starttls", "true", "1", "yes"}:
        fail("SMTP_PORT=587 requires SMTP_USE_TLS=starttls")

    print("environment validation ok")


def main() -> None:
    validate_env()


if __name__ == "__main__":
    main()

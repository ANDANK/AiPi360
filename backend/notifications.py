"""Notification dispatch — Email (SMTP) + ntfy.sh push.
Channels are pluggable: add Discord/Telegram by extending _DISPATCHERS.
"""
import smtplib
import requests
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ── Email ─────────────────────────────────────────────────────────────────────

def _send_email(subject: str, body: str) -> None:
    cfg = st.secrets.get("email", {})
    msg = MIMEMultipart("alternative")
    msg["From"]    = cfg["sender"]
    msg["To"]      = cfg["recipient"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(cfg.get("smtp_host", "smtp.gmail.com"),
                      int(cfg.get("smtp_port", 587))) as s:
        s.ehlo()
        s.starttls()
        s.login(cfg["sender"], cfg["app_password"])
        s.sendmail(cfg["sender"], cfg["recipient"], msg.as_string())


# ── ntfy.sh push ──────────────────────────────────────────────────────────────

_PRIORITY_MAP = {"low": "low", "default": "default", "high": "high", "urgent": "urgent"}

def _send_push(title: str, message: str, priority: str = "default",
               tags: list[str] | None = None) -> None:
    cfg   = st.secrets.get("ntfy", {})
    topic = cfg.get("topic", "aipi360")
    server = cfg.get("server", "https://ntfy.sh")
    headers: dict = {
        "Title":    title,
        "Priority": _PRIORITY_MAP.get(priority, "default"),
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    requests.post(f"{server}/{topic}", data=message.encode("utf-8"),
                  headers=headers, timeout=10)


# ── Public API ────────────────────────────────────────────────────────────────

def notify(
    title: str,
    message: str,
    channels: list[str] | None = None,
    priority: str = "default",
    tags: list[str] | None = None,
) -> dict[str, str]:
    """
    Send a notification on one or more channels.
    channels: list of "email", "push"  (default: ["push"])
    Returns dict of {channel: "ok" | error_message}
    """
    channels = channels or ["push"]
    results: dict[str, str] = {}

    if "email" in channels:
        try:
            _send_email(title, message)
            results["email"] = "ok"
        except Exception as exc:
            results["email"] = str(exc)

    if "push" in channels:
        try:
            _send_push(title, message, priority=priority, tags=tags)
            results["push"] = "ok"
        except Exception as exc:
            results["push"] = str(exc)

    return results


def test_notifications() -> dict[str, str]:
    return notify(
        "AiPi360 Test 🎉",
        "Notifications are working correctly.",
        channels=["email", "push"],
        tags=["white_check_mark"],
    )

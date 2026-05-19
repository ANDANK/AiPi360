"""Notification dispatch — Resend (email) + ntfy.sh push.
Channels are pluggable: add more by extending _DISPATCHERS.
"""
import requests
import streamlit as st


# ── Resend email ──────────────────────────────────────────────────────────────

def _send_email(subject: str, body: str) -> None:
    import resend
    cfg = st.secrets.get("resend", {})
    resend.api_key = cfg.get("api_key", "")
    resend.Emails.send({
        "from":    cfg.get("from_address", "AiPi360 <notifications@yourdomain.com>"),
        "to":      [cfg.get("recipient", "")],
        "subject": subject,
        "html":    body,
    })


# ── ntfy.sh push ──────────────────────────────────────────────────────────────

_PRIORITY_MAP = {"low": "low", "default": "default", "high": "high", "urgent": "urgent"}


def _send_push(title: str, message: str, priority: str = "default",
               tags: list[str] | None = None) -> None:
    cfg    = st.secrets.get("ntfy", {})
    topic  = cfg.get("topic", "aipi360")
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
        "<p>Notifications are working correctly.</p>",
        channels=["email", "push"],
        tags=["white_check_mark"],
    )

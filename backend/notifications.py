"""Notification dispatch — Resend (email) + ntfy.sh push.
Channels are pluggable: add more by extending _DISPATCHERS.
"""
import requests
import streamlit as st


# ── Resend email ──────────────────────────────────────────────────────────────

def _send_email(subject: str, body: str) -> None:
    import re, resend
    cfg        = st.secrets.get("resend", {})
    resend.api_key = cfg.get("api_key", "")
    from_addr  = cfg.get("from_address", "").strip()
    if not from_addr:
        raise ValueError(
            "resend.from_address is not set in Streamlit secrets.\n"
            "Add it as: from_address = \"Your Name <you@yourdomain.com>\""
        )
    if not re.match(r'^[^<>]+<[^@\s]+@[^@\s]+\.[^@\s]+>$|^[^@\s]+@[^@\s]+\.[^@\s]+$', from_addr):
        raise ValueError(
            f"resend.from_address is not a valid email: {from_addr!r}\n"
            "Expected: 'you@yourdomain.com' or 'Your Name <you@yourdomain.com>'"
        )
    resend.Emails.send({
        "from":    from_addr,
        "to":      [cfg.get("recipient", "")],
        "subject": subject,
        "html":    body,
    })


# ── ntfy.sh push ──────────────────────────────────────────────────────────────

_PRIORITY_MAP = {"low": 2, "default": 3, "high": 4, "urgent": 5}


def _send_push(title: str, message: str, priority: str = "default",
               tags: list[str] | None = None) -> None:
    cfg    = st.secrets.get("ntfy", {})
    topic  = cfg.get("topic", "aipi360")
    server = cfg.get("server", "https://ntfy.sh").rstrip("/")
    # Use JSON body — HTTP headers are latin-1 encoded by requests,
    # which crashes on any emoji in title. JSON body is UTF-8.
    payload: dict = {
        "topic":    topic,
        "title":    title,
        "message":  message,
        "priority": _PRIORITY_MAP.get(priority, 3),
    }
    if tags:
        payload["tags"] = tags
    requests.post(f"{server}/", json=payload, timeout=10)


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

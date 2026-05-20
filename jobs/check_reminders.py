"""
Nightly job — check reminders due soon and send notifications.
Run via GitHub Actions. Uses environment variables for secrets.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from datetime import date, timedelta


def _gsheet_client():
    import gspread
    from google.oauth2.service_account import Credentials
    creds_dict = json.loads(os.environ.get("GSHEET_CREDENTIALS", "{}"))
    scopes     = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_due_reminders(days_ahead: int = 7):
    import pandas as pd
    client = _gsheet_client()
    sh     = client.open_by_key(os.environ["SPREADSHEET_ID"])
    try:
        ws = sh.worksheet("reminders")
    except Exception:
        return []
    data = ws.get_all_records()
    if not data:
        return []
    df = pd.DataFrame(data)
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    today  = date.today()
    cutoff = today + timedelta(days=days_ahead)
    active = df[
        (df["status"].str.upper() != "DONE") &
        (df["due_date"].notna()) &
        (df["due_date"] <= cutoff)
    ]
    return active.to_dict("records")


def _send_push(title: str, message: str) -> None:
    topic = os.environ.get("NTFY_TOPIC", "")
    if not topic:
        return
    # Use JSON body so emoji/Unicode in title and message are handled as UTF-8
    requests.post(
        "https://ntfy.sh/",
        json={
            "topic":    topic,
            "title":    title,
            "message":  message,
            "priority": 4,
            "tags":     ["bell"],
        },
        timeout=10,
    )


def _send_email(subject: str, html_body: str) -> None:
    import re, resend
    resend.api_key  = os.environ.get("RESEND_API_KEY", "")
    from_raw        = os.environ.get("RESEND_FROM", "AiPi360 <onboarding@resend.dev>")
    # Validate: must be email@domain or Name <email@domain>
    _valid = re.match(r'^[^<>]+<[^@\s]+@[^@\s]+\.[^@\s]+>$|^[^@\s]+@[^@\s]+\.[^@\s]+$', from_raw.strip())
    if not _valid:
        raise ValueError(
            f"RESEND_FROM env var is not a valid email address: {from_raw!r}\n"
            "Expected format: 'you@yourdomain.com' or 'Your Name <you@yourdomain.com>'"
        )
    resend.Emails.send({
        "from":    from_raw.strip(),
        "to":      [os.environ.get("RESEND_RECIPIENT", "")],
        "subject": subject,
        "html":    html_body,
    })


def main():
    print(f"Checking reminders for {date.today()}…")
    due = _get_due_reminders(days_ahead=7)
    if not due:
        print("No reminders due.")
        return

    today   = date.today()
    urgent  = [r for r in due if isinstance(r.get("due_date"), date) and (r["due_date"] - today).days <= 1]
    upcoming = [r for r in due if isinstance(r.get("due_date"), date) and 1 < (r["due_date"] - today).days <= 7]

    lines = ["<h2 style='color:#1e3a5f'>AiPi360 Reminders</h2>"]
    if urgent:
        lines.append("<h3 style='color:#dc2626'>🚨 Due Today / Tomorrow</h3><ul>")
        for r in urgent:
            lines.append(f"<li><b>{r['title']}</b> — {str(r.get('section','')).upper()} ({r['due_date']})<br><span style='color:#64748b'>{r.get('message','')}</span></li>")
        lines.append("</ul>")
    if upcoming:
        lines.append("<h3 style='color:#2563eb'>📅 Upcoming This Week</h3><ul>")
        for r in upcoming:
            delta = (r["due_date"] - today).days
            lines.append(f"<li><b>{r['title']}</b> — in {delta} days ({r['due_date']})</li>")
        lines.append("</ul>")

    subject = f"AiPi360 — {len(urgent)} urgent, {len(upcoming)} upcoming reminder(s)"

    try:
        _send_email(subject, "".join(lines))
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

    for r in urgent:
        try:
            _send_push(f"🔔 {r['title']}", r.get("message", "Due soon"))
        except Exception as e:
            print(f"Push failed: {e}")


if __name__ == "__main__":
    main()

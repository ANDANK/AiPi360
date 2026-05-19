"""
Nightly job — check reminders due soon and send notifications.
Run via GitHub Actions. Uses environment variables for secrets.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import smtplib
import requests
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _gsheet_client():
    import gspread
    from google.oauth2.service_account import Credentials
    creds_json = os.environ.get("GSHEET_CREDENTIALS", "{}")
    creds_dict = json.loads(creds_json)
    scopes     = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_due_reminders(days_ahead: int = 1):
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
    today   = date.today()
    cutoff  = today + timedelta(days=days_ahead)
    active  = df[
        (df["status"].str.upper() != "DONE") &
        (df["due_date"].notna()) &
        (df["due_date"] <= cutoff)
    ]
    return active.to_dict("records")


def _send_push(title, message):
    topic = os.environ.get("NTFY_TOPIC", "")
    if not topic:
        return
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode(),
        headers={"Title": title, "Priority": "high", "Tags": "bell"},
        timeout=10,
    )


def _send_email(subject, body):
    sender   = os.environ.get("EMAIL_SENDER", "")
    password = os.environ.get("EMAIL_APP_PASSWORD", "")
    recip    = os.environ.get("EMAIL_RECIPIENT", sender)
    if not sender or not password:
        return
    msg = MIMEMultipart("alternative")
    msg["From"]    = sender
    msg["To"]      = recip
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.ehlo(); s.starttls()
        s.login(sender, password)
        s.sendmail(sender, recip, msg.as_string())


def main():
    print(f"Checking reminders for {date.today()}…")
    due = _get_due_reminders(days_ahead=7)
    if not due:
        print("No reminders due.")
        return

    today = date.today()
    urgent = [r for r in due if r.get("due_date") and (r["due_date"] - today).days <= 1]
    upcoming = [r for r in due if r.get("due_date") and 1 < (r["due_date"] - today).days <= 7]

    lines = []
    if urgent:
        lines.append("<h3>🚨 Due Today / Tomorrow</h3><ul>")
        for r in urgent:
            lines.append(f"<li><b>{r['title']}</b> — {r.get('section','').upper()} ({r['due_date']})<br>{r.get('message','')}</li>")
        lines.append("</ul>")
    if upcoming:
        lines.append("<h3>📅 Upcoming This Week</h3><ul>")
        for r in upcoming:
            delta = (r["due_date"] - today).days
            lines.append(f"<li><b>{r['title']}</b> — in {delta} days ({r['due_date']})</li>")
        lines.append("</ul>")

    body = "".join(lines)
    subject = f"AiPi360 Reminders — {len(urgent)} urgent, {len(upcoming)} upcoming"

    try:
        _send_email(subject, body)
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

    for r in urgent:
        try:
            _send_push(f"🔔 {r['title']}", r.get("message", "Due soon"))
            print(f"Push sent: {r['title']}")
        except Exception as e:
            print(f"Push failed: {e}")


if __name__ == "__main__":
    main()

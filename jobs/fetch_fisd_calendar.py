"""
Nightly job — fetch FISD calendar events using Claude AI and update GSheet.
Runs via GitHub Actions. Falls back gracefully if FISD site structure changes.
"""
import os, sys, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
from datetime import datetime, date

FISD_CALENDAR_URL = "https://www.friscoisd.org/calendar/frisco-isd-calendar"
WORTHAM_URL       = "https://schools.friscoisd.org/campus/middle-school/wortham/home"
SCHOOL_YEAR       = "2026-2027"


def _gsheet_client():
    import gspread
    from google.oauth2.service_account import Credentials
    creds_dict = json.loads(os.environ.get("GSHEET_CREDENTIALS", "{}"))
    # Fix Streamlit/env double-escape on private_key
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_or_create_ws(tab: str):
    import gspread
    client = _gsheet_client()
    sh     = client.open_by_key(os.environ["SPREADSHEET_ID"])
    try:
        return sh.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows=1000, cols=10)
        ws.append_row(["date","event","type","source","school_year","fetched_at"])
        return ws


def _fetch_page(url: str) -> str:
    """Fetch HTML content of a page."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AiPi360-bot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    # Strip script/style tags to reduce tokens
    html = resp.text
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>',  '', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html).strip()
    return html[:12000]  # Keep within Claude token budget


def _extract_events_with_claude(page_text: str, source_url: str) -> list[dict]:
    """Use Claude to extract calendar events from page text."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    prompt = f"""Extract school calendar events from this FISD webpage text.
Return a JSON array of events with this exact schema:
[{{"date": "YYYY-MM-DD", "event": "event name", "type": "one of: Holiday|No School|Early Release|Break|First Day|Last Day|STAAR|Event|Other"}}]

Rules:
- Only include events with specific dates
- Focus on: no-school days, holidays, breaks, early release, STAAR tests, first/last day
- For date ranges (e.g. Spring Break Mar 15-19), create one entry per day
- If year is ambiguous use school year 2026-2027 (Aug 2026 - May 2027)
- Return [] if no events found

Webpage text:
{page_text}"""

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    m   = re.search(r"\[[\s\S]*\]", raw)
    if m:
        try:
            events = json.loads(m.group())
            for e in events:
                e["source"] = source_url
            return events
        except json.JSONDecodeError:
            pass
    return []


def _upsert_events(ws, events: list[dict]) -> int:
    """Write new events to GSheet, skip duplicates. Returns count added."""
    existing = ws.get_all_records()
    existing_keys = {(r.get("date",""), r.get("event","")) for r in existing}
    now   = datetime.now().isoformat()
    added = 0
    for e in events:
        key = (e.get("date",""), e.get("event",""))
        if key not in existing_keys:
            ws.append_row([
                e.get("date",""),
                e.get("event",""),
                e.get("type","Other"),
                e.get("source",""),
                SCHOOL_YEAR,
                now,
            ], value_input_option="USER_ENTERED")
            existing_keys.add(key)
            added += 1
    return added


def _seed_baseline_if_empty(ws) -> int:
    """Seed with known dates if sheet is empty."""
    from services.fisd_calendar import BASELINE_2026_27
    existing = ws.get_all_records()
    if existing:
        return 0
    now  = datetime.now().isoformat()
    rows = [[dt, ev, et, src, SCHOOL_YEAR, now]
            for dt, ev, et, src in BASELINE_2026_27]
    for row in rows:
        ws.append_row(row, value_input_option="USER_ENTERED")
    print(f"  Seeded {len(rows)} baseline dates.")
    return len(rows)


def main():
    print(f"FISD Calendar fetch — {date.today()}")

    ws    = _get_or_create_ws("fisd_calendar")
    total = 0

    # Always seed baseline first if sheet is empty
    seeded = _seed_baseline_if_empty(ws)
    if seeded:
        total += seeded

    # Fetch and parse FISD main calendar
    sources = [
        (FISD_CALENDAR_URL, "friscoisd.org/calendar"),
        (WORTHAM_URL,       "wortham.friscoisd.org"),
    ]
    for url, label in sources:
        print(f"  Fetching {label}…")
        try:
            html  = _fetch_page(url)
            events = _extract_events_with_claude(html, label)
            added  = _upsert_events(ws, events)
            print(f"  {label}: {len(events)} events found, {added} new")
            total += added
        except Exception as e:
            print(f"  {label} failed: {e}")

    print(f"Done. Total new events added: {total}")


if __name__ == "__main__":
    main()

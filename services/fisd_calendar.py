"""FISD calendar service — read/write from GSheet, baseline known dates."""
import pandas as pd
from datetime import date, datetime, timedelta
from backend.gsheet import read_sheet, overwrite_sheet, append_row

TAB = "fisd_calendar"

# ── Event type colours for UI ─────────────────────────────────────────────────
TYPE_STYLE = {
    "Holiday":      ("#fef2f2", "#dc2626", "🔴"),
    "No School":    ("#fef2f2", "#dc2626", "🔴"),
    "Early Release":("#fff7ed", "#ea580c", "🟠"),
    "Break":        ("#fef9c3", "#ca8a04", "🟡"),
    "First Day":    ("#f0fdf4", "#16a34a", "🟢"),
    "Last Day":     ("#f0fdf4", "#16a34a", "🟢"),
    "STAAR":        ("#eff6ff", "#2563eb", "🔵"),
    "Event":        ("#f5f3ff", "#7c3aed", "🟣"),
    "Other":        ("#f8fafc", "#64748b", "⚪"),
}

# ── Baseline 2026-2027 dates (confirmed + estimated) ─────────────────────────
# Confirmed from FISD website: First Day Aug 12 2026, Last Day May 2027
# Holidays follow standard FISD pattern — update via nightly job or manual entry
BASELINE_2026_27 = [
    # Confirmed
    ("2026-08-12", "First Day of School",               "First Day",    "friscoisd.org"),
    # Standard federal/FISD holidays
    ("2026-09-07", "Labor Day — No School",              "Holiday",      "friscoisd.org"),
    ("2026-10-12", "Fall Break — No School (Est.)",      "Break",        "estimated"),
    ("2026-10-13", "Fall Break — No School (Est.)",      "Break",        "estimated"),
    ("2026-10-14", "Fall Break — No School (Est.)",      "Break",        "estimated"),
    ("2026-10-15", "Fall Break — No School (Est.)",      "Break",        "estimated"),
    ("2026-10-16", "Fall Break — No School (Est.)",      "Break",        "estimated"),
    ("2026-11-11", "Veterans Day — No School (Est.)",    "Holiday",      "estimated"),
    ("2026-11-23", "Thanksgiving Break",                 "Break",        "estimated"),
    ("2026-11-24", "Thanksgiving Break",                 "Break",        "estimated"),
    ("2026-11-25", "Thanksgiving Break",                 "Break",        "estimated"),
    ("2026-11-26", "Thanksgiving Day",                   "Holiday",      "estimated"),
    ("2026-11-27", "Thanksgiving Break",                 "Break",        "estimated"),
    ("2026-12-21", "Winter Break Begins (Est.)",         "Break",        "estimated"),
    ("2026-12-22", "Winter Break",                       "Break",        "estimated"),
    ("2026-12-23", "Winter Break",                       "Break",        "estimated"),
    ("2026-12-24", "Christmas Eve",                      "Holiday",      "estimated"),
    ("2026-12-25", "Christmas Day",                      "Holiday",      "estimated"),
    ("2026-12-28", "Winter Break",                       "Break",        "estimated"),
    ("2026-12-29", "Winter Break",                       "Break",        "estimated"),
    ("2026-12-30", "Winter Break",                       "Break",        "estimated"),
    ("2026-12-31", "New Year's Eve",                     "Holiday",      "estimated"),
    ("2027-01-01", "New Year's Day",                     "Holiday",      "estimated"),
    ("2027-01-04", "School Resumes (Est.)",              "First Day",    "estimated"),
    ("2027-01-19", "MLK Day — No School",                "Holiday",      "estimated"),
    ("2027-02-15", "Presidents Day — No School (Est.)",  "Holiday",      "estimated"),
    ("2027-03-15", "Spring Break (Est.)",                "Break",        "estimated"),
    ("2027-03-16", "Spring Break (Est.)",                "Break",        "estimated"),
    ("2027-03-17", "Spring Break (Est.)",                "Break",        "estimated"),
    ("2027-03-18", "Spring Break (Est.)",                "Break",        "estimated"),
    ("2027-03-19", "Spring Break (Est.)",                "Break",        "estimated"),
    ("2027-04-02", "Good Friday — No School (Est.)",     "Holiday",      "estimated"),
    # STAAR Grade 6 (typical April window)
    ("2027-04-06", "STAAR Grade 6 Reading (Est.)",       "STAAR",        "tea.texas.gov"),
    ("2027-04-08", "STAAR Grade 6 Math (Est.)",          "STAAR",        "tea.texas.gov"),
    ("2027-05-31", "Memorial Day — No School",           "Holiday",      "estimated"),
    ("2027-05-28", "Last Day of School (Est.)",          "Last Day",     "estimated"),
]


def get_events(school_year: str = "2026-2027") -> pd.DataFrame:
    """Return all events for a given school year, sorted by date."""
    df = read_sheet(TAB)
    if df.empty:
        return df
    return df[df["school_year"] == school_year].copy()


def seed_baseline(school_year: str = "2026-2027", force: bool = False) -> int:
    """
    Seed GSheet with baseline dates if empty (or force=True).
    Returns number of rows added.
    """
    existing = get_events(school_year)
    if not existing.empty and not force:
        return 0

    now = datetime.now().isoformat()
    rows = [
        [dt, event, etype, source, school_year, now]
        for dt, event, etype, source in BASELINE_2026_27
    ]
    if force and not existing.empty:
        # Remove old entries for this year then re-seed
        df = read_sheet(TAB)
        df = df[df["school_year"] != school_year]
        overwrite_sheet(TAB, df)

    for row in rows:
        append_row(TAB, row)
    return len(rows)


def upsert_event(event_date: str, event: str, etype: str,
                 source: str, school_year: str = "2026-2027") -> None:
    """Add or update a single event (matched by date + event name)."""
    df = read_sheet(TAB)
    now = datetime.now().isoformat()
    mask = (df["date"] == event_date) & (df["event"] == event) if not df.empty else None
    if df.empty or not mask.any():
        append_row(TAB, [event_date, event, etype, source, school_year, now])
    else:
        df.loc[mask, ["type", "source", "fetched_at"]] = [etype, source, now]
        overwrite_sheet(TAB, df)


def upcoming_events(days: int = 30, school_year: str = "2026-2027") -> pd.DataFrame:
    df = get_events(school_year)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    today  = date.today()
    cutoff = today + timedelta(days=days)
    return df[
        (df["date"] >= today) & (df["date"] <= cutoff)
    ].sort_values("date")


def no_school_days(school_year: str = "2026-2027") -> pd.DataFrame:
    df = get_events(school_year)
    if df.empty:
        return df
    return df[df["type"].isin(["Holiday","No School","Break"])].sort_values("date")

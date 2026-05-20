"""Reminder CRUD service backed by Google Sheets."""
import uuid
import pandas as pd
from datetime import date, datetime
from backend.gsheet import read_sheet, append_row, overwrite_sheet

TAB = "reminders"


def get_all() -> pd.DataFrame:
    return read_sheet(TAB)


def get_active(section: str | None = None) -> pd.DataFrame:
    df = get_all()
    if df.empty:
        return df
    df = df[df["status"].str.upper() != "DONE"]
    if section:
        df = df[df["section"].str.lower() == section.lower()]
    return df


def add(
    section: str,
    title: str,
    message: str,
    due_date: date,
    remind_days: int = 1,
    frequency: str = "once",
    channels: str = "push",
    due_time: str = "",          # "9:30 AM" or "" for all-day
) -> str:
    rid = str(uuid.uuid4())[:8]
    full_msg = (f"⏰ {due_time} — " + message) if due_time else message
    append_row(TAB, [
        rid, section, title, full_msg,
        due_date.isoformat(), remind_days, frequency,
        channels, "active", datetime.now().isoformat(),
    ])
    return rid


def mark_done(reminder_id: str) -> None:
    df = get_all()
    if df.empty:
        return
    df.loc[df["id"] == reminder_id, "status"] = "DONE"
    overwrite_sheet(TAB, df)


def delete(reminder_id: str) -> None:
    df = get_all()
    if df.empty:
        return
    df = df[df["id"] != reminder_id]
    overwrite_sheet(TAB, df)


def due_today(section: str | None = None) -> pd.DataFrame:
    df = get_active(section)
    if df.empty:
        return df
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    return df[df["due_date"] == date.today()]

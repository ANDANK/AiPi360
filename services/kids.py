"""Kids/classes service."""
import uuid
import pandas as pd
from datetime import date, timedelta
from backend.gsheet import read_sheet, append_row, overwrite_sheet

CLASSES_TAB = "classes"

CHILDREN     = ["Son", "Daughter"]
FREQUENCIES  = ["Weekly", "Bi-Weekly", "Monthly", "One-Time", "Annual", "Free"]
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

_DAY_NUM = {d: i for i, d in enumerate(DAYS_OF_WEEK)}


def list_classes(child: str | None = None, active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(CLASSES_TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
    if child:
        df = df[df["child"].str.lower() == child.lower()]
    return df


def add_class(child: str, name: str, provider: str, cost: float,
              frequency: str, start_date: date,
              end_date: date | None = None,
              days: str = "",
              time_start: str = "",
              time_end: str = "",
              location: str = "") -> str:
    cid = str(uuid.uuid4())[:8]
    append_row(CLASSES_TAB, [
        cid, child, name, provider, cost, frequency,
        start_date.isoformat(),
        end_date.isoformat() if end_date else "",
        "TRUE",
        days,
        time_start,
        time_end,
        location,
    ])
    return cid


def update_class(class_id: str, **kwargs) -> None:
    df = list_classes(active_only=False)
    for k, v in kwargs.items():
        if k in df.columns:
            df.loc[df["id"] == class_id, k] = v
    overwrite_sheet(CLASSES_TAB, df)


def delete_class(class_id: str) -> None:
    df = list_classes(active_only=False)
    df.loc[df["id"] == class_id, "active"] = "FALSE"
    overwrite_sheet(CLASSES_TAB, df)


def monthly_cost(child: str | None = None) -> float:
    df = list_classes(child=child)
    if df.empty:
        return 0.0
    monthly_mult = {
        "weekly": 4.33, "bi-weekly": 2.17, "monthly": 1,
        "one-time": 0, "annual": 1/12, "free": 0,
    }
    total = 0.0
    for _, r in df.iterrows():
        m = monthly_mult.get(str(r.get("frequency","")).lower(), 1)
        total += float(r.get("cost", 0) or 0) * m
    return total


def upcoming_sessions(child: str | None = None, days_ahead: int = 14) -> list[dict]:
    """Return upcoming class occurrences within the next `days_ahead` days.

    Only classes with at least one day-of-week set are included.
    Bi-Weekly classes alternate weeks starting from start_date.
    """
    df = list_classes(child=child)
    if df.empty:
        return []

    today  = date.today()
    cutoff = today + timedelta(days=days_ahead)
    sessions: list[dict] = []

    for _, cls in df.iterrows():
        raw_days = str(cls.get("days", "")).strip()
        if not raw_days:
            continue
        class_days = [d.strip() for d in raw_days.split(",") if d.strip() in _DAY_NUM]
        if not class_days:
            continue

        freq = str(cls.get("frequency", "weekly")).lower()

        # Resolve start date for bi-weekly alternation
        try:
            cls_start = date.fromisoformat(str(cls.get("start_date", today.isoformat())))
        except ValueError:
            cls_start = today

        check = today
        week_0 = (cls_start - date(cls_start.year, 1, 1)).days // 7  # ISO week anchor

        while check <= cutoff:
            day_name = check.strftime("%A")
            if day_name in class_days:
                if freq == "bi-weekly":
                    week_n = (check - date(check.year, 1, 1)).days // 7
                    if (week_n - week_0) % 2 != 0:
                        check += timedelta(days=1)
                        continue
                sessions.append({
                    "date":       check,
                    "day":        day_name,
                    "class":      cls.get("name", ""),
                    "child":      cls.get("child", ""),
                    "provider":   cls.get("provider", ""),
                    "time_start": str(cls.get("time_start", "") or ""),
                    "time_end":   str(cls.get("time_end", "") or ""),
                    "location":   str(cls.get("location", "") or ""),
                    "frequency":  freq,
                })
            check += timedelta(days=1)

    sessions.sort(key=lambda x: (x["date"], x.get("time_start", "")))
    return sessions

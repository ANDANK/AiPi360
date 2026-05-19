"""Insurance policy service."""
import uuid
import pandas as pd
from datetime import date
from backend.gsheet import read_sheet, append_row, overwrite_sheet

TAB = "insurance_policies"

POLICY_TYPES = ["Life", "Term Life", "Auto", "Home", "Umbrella",
                "Medical", "Dental", "Vision", "Other"]
FREQUENCIES  = ["Monthly", "Quarterly", "Semi-Annual", "Annual"]

ICONS = {
    "life":      "❤️", "term life": "💙", "auto":      "🚗",
    "home":      "🏠", "umbrella":  "☂️", "medical":   "🏥",
    "dental":    "🦷", "vision":    "👁️", "other":     "📋",
}


def icon(ptype: str) -> str:
    return ICONS.get(ptype.lower(), "📋")


def list_policies(active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
    return df


def add_policy(ptype: str, provider: str, policy_number: str,
               premium: float, frequency: str, due_date: date,
               notes: str = "") -> str:
    pid = str(uuid.uuid4())[:8]
    append_row(TAB, [pid, ptype, provider, policy_number,
                     premium, frequency, due_date.isoformat(), notes, "TRUE"])
    return pid


def update_policy(policy_id: str, **kwargs) -> None:
    df = list_policies(active_only=False)
    for k, v in kwargs.items():
        if k in df.columns:
            df.loc[df["id"] == policy_id, k] = v
    overwrite_sheet(TAB, df)


def delete_policy(policy_id: str) -> None:
    df = list_policies(active_only=False)
    df.loc[df["id"] == policy_id, "active"] = "FALSE"
    overwrite_sheet(TAB, df)


def annual_total(df: pd.DataFrame | None = None) -> float:
    if df is None:
        df = list_policies()
    if df.empty:
        return 0.0
    multiplier = {"Monthly": 12, "Quarterly": 4, "Semi-Annual": 2, "Annual": 1}
    total = 0.0
    for _, r in df.iterrows():
        m = multiplier.get(r.get("frequency", "Annual"), 1)
        total += float(r.get("premium", 0) or 0) * m
    return total


def due_soon(days: int = 30, df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = list_policies()
    if df.empty:
        return df
    df = df.copy()
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    cutoff = date.today() + pd.Timedelta(days=days)
    return df[df["due_date"] <= cutoff.date() if hasattr(cutoff, "date") else cutoff]

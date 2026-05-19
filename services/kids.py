"""Kids/classes service."""
import uuid
import pandas as pd
from datetime import date
from backend.gsheet import read_sheet, append_row, overwrite_sheet

CLASSES_TAB = "classes"

CHILDREN     = ["Son", "Daughter"]
FREQUENCIES  = ["Weekly", "Bi-Weekly", "Monthly", "One-Time", "Annual", "Free"]


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
              end_date: date | None = None) -> str:
    cid = str(uuid.uuid4())[:8]
    append_row(CLASSES_TAB, [
        cid, child, name, provider, cost, frequency,
        start_date.isoformat(),
        end_date.isoformat() if end_date else "",
        "TRUE",
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

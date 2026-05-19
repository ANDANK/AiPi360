"""Credit card & points service."""
import uuid
import pandas as pd
from datetime import date
from backend.gsheet import read_sheet, append_row, overwrite_sheet

TAB = "cc_cards"

BANK_ICONS = {
    "chase": "🔵", "amex": "🟦", "citi": "🔴", "capital one": "💜",
    "discover": "🟠", "bank of america": "🔴", "wells fargo": "🟡",
    "other": "💳",
}


def icon(bank: str) -> str:
    return BANK_ICONS.get(bank.lower(), "💳")


def list_cards(active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
    return df


def add_card(name: str, bank: str, last4: str, annual_fee: float,
             fee_due_date: date, credit_limit: float, perks: str = "") -> str:
    cid = str(uuid.uuid4())[:8]
    append_row(TAB, [cid, name, bank, last4, annual_fee,
                     fee_due_date.isoformat(), credit_limit, perks, "TRUE"])
    return cid


def update_card(card_id: str, **kwargs) -> None:
    df = list_cards(active_only=False)
    for k, v in kwargs.items():
        if k in df.columns:
            df.loc[df["id"] == card_id, k] = v
    overwrite_sheet(TAB, df)


def delete_card(card_id: str) -> None:
    df = list_cards(active_only=False)
    df.loc[df["id"] == card_id, "active"] = "FALSE"
    overwrite_sheet(TAB, df)


def total_annual_fees(df: pd.DataFrame | None = None) -> float:
    if df is None:
        df = list_cards()
    if df.empty:
        return 0.0
    return float(df["annual_fee"].apply(pd.to_numeric, errors="coerce").fillna(0).sum())


def fees_due_soon(days: int = 30, df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = list_cards()
    if df.empty:
        return df
    df = df.copy()
    df["fee_due_date"] = pd.to_datetime(df["fee_due_date"], errors="coerce").dt.date
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=days)
    return df[df["fee_due_date"] <= cutoff]

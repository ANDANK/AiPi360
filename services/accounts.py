"""Account and balance service — ported from NetWorth Tracker."""
import uuid
import pandas as pd
from datetime import date, datetime
from backend.gsheet import read_sheet, append_row, overwrite_sheet

ACCOUNTS_TAB  = "accounts"
BALANCES_TAB  = "account_balances"
ALERTS_TAB    = "market_alerts"

ACCOUNT_TYPES = {
    "brokerage":       ("📈", "Brokerage"),
    "roth_ira":        ("🌱", "Roth IRA"),
    "traditional_ira": ("🏛️", "Traditional IRA"),
    "401k":            ("💼", "401(k)"),
    "roth_401k":       ("🔵", "Roth 401(k)"),
    "hsa":             ("🏥", "HSA"),
    "savings":         ("🏦", "Savings"),
    "checking":        ("💳", "Checking"),
    "crypto":          ("🪙", "Crypto"),
    "treasury":        ("🇺🇸", "Treasury"),
    "cd":              ("🔒", "CD"),
    "real_estate":     ("🏠", "Real Estate"),
    "auto":            ("🚗", "Auto"),
    "mortgage":        ("🏡", "Mortgage"),
}

RETIREMENT_TYPES = {"roth_ira","traditional_ira","401k","roth_401k","hsa","sep_ira","solo_401k"}


def icon(atype: str) -> str:
    return ACCOUNT_TYPES.get(atype, ("💰", ""))[0]

def label(atype: str) -> str:
    return ACCOUNT_TYPES.get(atype, ("", atype.replace("_"," ").title()))[1]

def is_retirement(atype: str) -> bool:
    return atype.lower() in RETIREMENT_TYPES


# ── Accounts ──────────────────────────────────────────────────────────────────

def list_accounts(active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(ACCOUNTS_TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
    return df


def add_account(name: str, atype: str, owner: str) -> str:
    aid = str(uuid.uuid4())[:8]
    append_row(ACCOUNTS_TAB, [aid, name, atype, owner, "TRUE"])
    return aid


def deactivate_account(account_id: str) -> None:
    df = read_sheet(ACCOUNTS_TAB)
    df.loc[df["account_id"] == account_id, "active"] = "FALSE"
    overwrite_sheet(ACCOUNTS_TAB, df)


# ── Balances ──────────────────────────────────────────────────────────────────

def save_balances(entries: list[dict], snap_date: date) -> None:
    """entries: list of {account_id, account_name, balance}"""
    for e in entries:
        append_row(BALANCES_TAB, [
            snap_date.isoformat(),
            e["account_id"],
            e.get("account_name", ""),
            float(e["balance"]),
        ])


def load_balances() -> pd.DataFrame:
    df = read_sheet(BALANCES_TAB)
    if df.empty:
        return df
    df["date"]    = pd.to_datetime(df["date"], errors="coerce")
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0)
    return df.sort_values("date")


def latest_balances(df: pd.DataFrame | None = None) -> dict[str, float]:
    if df is None:
        df = load_balances()
    if df.empty:
        return {}
    latest: dict[str, float] = {}
    for _, r in df.sort_values("date").iterrows():
        latest[r["account_id"]] = float(r["balance"])
    return latest


# ── Market Alerts ─────────────────────────────────────────────────────────────

def list_alerts() -> pd.DataFrame:
    return read_sheet(ALERTS_TAB)


def add_alert(ticker: str, condition: str, threshold: float, channels: str = "push") -> None:
    aid = str(uuid.uuid4())[:8]
    append_row(ALERTS_TAB, [aid, ticker, condition, threshold, channels, "TRUE"])


def delete_alert(alert_id: str) -> None:
    df = list_alerts()
    df = df[df["id"] != alert_id]
    overwrite_sheet(ALERTS_TAB, df)

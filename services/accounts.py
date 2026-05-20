"""Account and balance service — ported from NetWorth Tracker."""
import uuid
from datetime import date, datetime
from typing import Optional

import pandas as pd

from backend.gsheet import read_sheet, append_row, overwrite_sheet

ACCOUNTS_TAB = "accounts"
BALANCES_TAB = "account_balances"
ALERTS_TAB   = "market_alerts"
BROKERS_TAB  = "brokers"
MANUAL_TAB   = "manual_accounts"

ACCOUNT_TYPES = {
    "brokerage":       ("📈", "Brokerage"),
    "roth_ira":        ("🌱", "Roth IRA"),
    "traditional_ira": ("🏛️", "Traditional IRA"),
    "401k":            ("💼", "401(k)"),
    "roth_401k":       ("🔵", "Roth 401(k)"),
    "solo_401k":       ("🧑‍💼", "Solo 401(k)"),
    "sep_ira":         ("📋", "SEP IRA"),
    "hsa":             ("🏥", "HSA"),
    "fsa":             ("🩺", "FSA"),
    "savings":         ("🏦", "Savings"),
    "checking":        ("💳", "Checking"),
    "crypto":          ("🪙", "Crypto"),
    "treasury":        ("🇺🇸", "Treasury"),
    "cd":              ("🔒", "CD"),
    "real_estate":     ("🏠", "Real Estate"),
    "auto":            ("🚗", "Auto"),
    "mortgage":        ("🏡", "Mortgage"),
}

RETIREMENT_TYPES = frozenset({
    "roth_ira", "traditional_ira", "401k", "roth_401k",
    "hsa", "sep_ira", "solo_401k",
})
RETIREMENT_ACCOUNT_TYPES = RETIREMENT_TYPES   # alias used in the page

_TAX_STATUS_MAP: dict[str, str] = {
    "roth_ira": "tax_free",     "roth_401k": "tax_free",
    "hsa": "tax_free",          "fsa": "tax_free",
    "traditional_ira": "tax_deferred", "401k": "tax_deferred",
    "sep_ira": "tax_deferred",  "solo_401k": "tax_deferred",
    "brokerage": "taxable",     "savings": "taxable",
    "checking": "taxable",      "crypto": "taxable",
    "treasury": "taxable",      "cd": "taxable",
    "real_estate": "taxable",   "auto": "taxable",  "mortgage": "taxable",
}

TAX_STATUS_LABELS: dict[str, tuple[str, str]] = {
    "tax_free":     ("🟢", "Tax-Free"),
    "tax_deferred": ("🟡", "Tax-Deferred"),
    "taxable":      ("🔵", "Taxable"),
}

_DEFAULT_BROKERS = ["Schwab", "Fidelity", "Robinhood", "Vanguard", "Webull", "E*Trade"]


def auto_tax_status(atype: str) -> str:
    return _TAX_STATUS_MAP.get(str(atype).lower(), "taxable")


PROJECTION_END_YEAR = 2040
DEFAULT_SELF_DOB    = date(1975, 1,  1)
DEFAULT_SPOUSE_DOB  = date(1980, 10, 1)

# ── IRS contribution limits 2024–2040 ────────────────────────────────────────
# 2024–2025 confirmed; 2026+ estimated at ~3% COLA rounded to $500 increments
IRS_LIMITS: dict[int, dict] = {
    2024: dict(confirmed=True,  irs_401k=23_000, irs_401k_cu=7_500,  ira=7_000, ira_cu=1_000, hsa_self=4_150, hsa_fam=8_300),
    2025: dict(confirmed=True,  irs_401k=23_500, irs_401k_cu=7_500,  ira=7_000, ira_cu=1_000, hsa_self=4_300, hsa_fam=8_550),
    2026: dict(confirmed=False, irs_401k=24_000, irs_401k_cu=7_500,  ira=7_500, ira_cu=1_000, hsa_self=4_450, hsa_fam=8_900),
    2027: dict(confirmed=False, irs_401k=24_000, irs_401k_cu=8_000,  ira=7_500, ira_cu=1_000, hsa_self=4_600, hsa_fam=9_200),
    2028: dict(confirmed=False, irs_401k=24_500, irs_401k_cu=8_000,  ira=7_500, ira_cu=1_000, hsa_self=4_750, hsa_fam=9_500),
    2029: dict(confirmed=False, irs_401k=25_000, irs_401k_cu=8_000,  ira=8_000, ira_cu=1_000, hsa_self=4_900, hsa_fam=9_800),
    2030: dict(confirmed=False, irs_401k=25_000, irs_401k_cu=8_500,  ira=8_000, ira_cu=1_000, hsa_self=5_050, hsa_fam=10_100),
    2031: dict(confirmed=False, irs_401k=25_500, irs_401k_cu=8_500,  ira=8_000, ira_cu=1_000, hsa_self=5_200, hsa_fam=10_400),
    2032: dict(confirmed=False, irs_401k=26_000, irs_401k_cu=9_000,  ira=8_500, ira_cu=1_000, hsa_self=5_350, hsa_fam=10_700),
    2033: dict(confirmed=False, irs_401k=26_000, irs_401k_cu=9_000,  ira=8_500, ira_cu=1_000, hsa_self=5_500, hsa_fam=11_000),
    2034: dict(confirmed=False, irs_401k=26_500, irs_401k_cu=9_500,  ira=9_000, ira_cu=1_000, hsa_self=5_650, hsa_fam=11_300),
    2035: dict(confirmed=False, irs_401k=27_000, irs_401k_cu=9_500,  ira=9_000, ira_cu=1_000, hsa_self=5_800, hsa_fam=11_600),
    2036: dict(confirmed=False, irs_401k=27_000, irs_401k_cu=10_000, ira=9_000, ira_cu=1_000, hsa_self=5_950, hsa_fam=11_900),
    2037: dict(confirmed=False, irs_401k=27_500, irs_401k_cu=10_000, ira=9_500, ira_cu=1_000, hsa_self=6_100, hsa_fam=12_200),
    2038: dict(confirmed=False, irs_401k=28_000, irs_401k_cu=10_000, ira=9_500, ira_cu=1_000, hsa_self=6_250, hsa_fam=12_500),
    2039: dict(confirmed=False, irs_401k=28_000, irs_401k_cu=10_500, ira=10_000, ira_cu=1_000, hsa_self=6_400, hsa_fam=12_800),
    2040: dict(confirmed=False, irs_401k=28_500, irs_401k_cu=10_500, ira=10_000, ira_cu=1_000, hsa_self=6_550, hsa_fam=13_100),
}


def icon(atype: str) -> str:
    return ACCOUNT_TYPES.get(atype, ("💰", ""))[0]

def label(atype: str) -> str:
    return ACCOUNT_TYPES.get(atype, ("", atype.replace("_", " ").title()))[1]

def is_retirement(atype: str) -> bool:
    return str(atype).lower() in RETIREMENT_TYPES


# ── Account CRUD ──────────────────────────────────────────────────────────────

def list_accounts(active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(ACCOUNTS_TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
    return df


def add_account(name: str, atype: str, owner: str, broker: str = "", tax_stat: str = "") -> str:
    aid = str(uuid.uuid4())[:8]
    if not tax_stat:
        tax_stat = auto_tax_status(atype)
    append_row(ACCOUNTS_TAB, [aid, name, atype, owner, "TRUE", broker, tax_stat])
    return aid


def deactivate_account(account_id: str) -> None:
    df = read_sheet(ACCOUNTS_TAB)
    df.loc[df["account_id"] == account_id, "active"] = "FALSE"
    overwrite_sheet(ACCOUNTS_TAB, df)


# ── Broker CRUD ───────────────────────────────────────────────────────────────

def list_brokers(active_only: bool = False) -> pd.DataFrame:
    df = read_sheet(BROKERS_TAB)
    if df.empty or "broker_name" not in df.columns:
        return pd.DataFrame(columns=["broker_id", "broker_name", "active"])
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
    return df


def add_broker(name: str) -> str:
    bid = str(uuid.uuid4())[:8]
    append_row(BROKERS_TAB, [bid, name, "TRUE"])
    return bid


def toggle_broker(broker_id: str) -> None:
    df = read_sheet(BROKERS_TAB)
    if df.empty:
        return
    mask    = df["broker_id"] == broker_id
    current = df.loc[mask, "active"].values[0] if mask.any() else "TRUE"
    new_val = "FALSE" if str(current).upper() in ("TRUE", "1", "YES") else "TRUE"
    df.loc[mask, "active"] = new_val
    overwrite_sheet(BROKERS_TAB, df)


def seed_brokers() -> None:
    df = read_sheet(BROKERS_TAB)
    if not df.empty and "broker_name" in df.columns:
        return
    rows = [{"broker_id": str(uuid.uuid4())[:8], "broker_name": name, "active": "TRUE"}
            for name in _DEFAULT_BROKERS]
    overwrite_sheet(BROKERS_TAB, pd.DataFrame(rows, columns=["broker_id", "broker_name", "active"]))


# ── Manual entries ────────────────────────────────────────────────────────────

def save_manual_entry(
    account_name: str,
    owner: str,
    category: str,
    value: float,
    notes: str = "",
    entry_date: Optional[date] = None,
) -> None:
    if entry_date is None:
        entry_date = date.today()
    append_row(MANUAL_TAB, [
        entry_date.isoformat(), account_name, owner, category,
        float(value), notes, datetime.now().isoformat(),
    ])


def list_manual_entries() -> pd.DataFrame:
    return read_sheet(MANUAL_TAB)


def latest_manual_balances() -> pd.DataFrame:
    df = list_manual_entries()
    if df.empty:
        return pd.DataFrame()
    df["value"]      = pd.to_numeric(df["value"], errors="coerce").fillna(0)
    df["entry_date"] = pd.to_datetime(df["entry_date"], errors="coerce")
    return df.sort_values("entry_date").groupby("account_name").last().reset_index()


# ── Balance snapshots ─────────────────────────────────────────────────────────

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


def latest_balances(df: Optional[pd.DataFrame] = None) -> dict[str, float]:
    if df is None:
        df = load_balances()
    if df.empty:
        return {}
    latest: dict[str, float] = {}
    for _, r in df.sort_values("date").iterrows():
        latest[str(r["account_id"])] = float(r["balance"])
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


# ── IRS helpers ───────────────────────────────────────────────────────────────

def _limits(year: int) -> dict:
    years = sorted(IRS_LIMITS)
    if year <= years[0]:  return IRS_LIMITS[years[0]]
    if year >= years[-1]: return IRS_LIMITS[years[-1]]
    return IRS_LIMITS.get(year, IRS_LIMITS[years[-1]])


def _age_at_year_end(dob: date, year: int) -> int:
    ye  = date(year, 12, 31)
    age = ye.year - dob.year
    if (ye.month, ye.day) < (dob.month, dob.day):
        age -= 1
    return age


def get_annual_contribution(
    account_type: str,
    owner: str,
    year: int,
    self_dob:   date = DEFAULT_SELF_DOB,
    spouse_dob: date = DEFAULT_SPOUSE_DOB,
) -> float:
    """Max IRS contribution for one account in one calendar year (SECURE 2.0 aware)."""
    lim  = _limits(year)
    dob  = self_dob if owner == "self" else spouse_dob
    age  = _age_at_year_end(dob, year)
    cu50 = age >= 50
    t    = str(account_type).lower()

    if t in ("roth_ira", "traditional_ira"):
        return lim["ira"] + (lim["ira_cu"] if cu50 else 0)

    if t in ("401k", "solo_401k"):
        base = lim["irs_401k"]
        return base + lim["irs_401k_cu"] if (cu50 and year < 2026) else base

    if t == "roth_401k":
        if year < 2026: return 0.0
        return lim["irs_401k_cu"] if cu50 else 0.0

    if t == "hsa":
        if owner == "self":   return 0.0
        return lim["hsa_fam"]

    return 0.0


# ── Analytics aggregation helpers ────────────────────────────────────────────

def monthly_totals(df: pd.DataFrame, months: int = 8) -> pd.DataFrame:
    """Last 8 months with total balance + MoM change."""
    if df.empty:
        return pd.DataFrame(columns=["month_str", "total", "mom_change"])
    d = df.copy()
    d["balance"] = pd.to_numeric(d["balance"], errors="coerce").fillna(0)
    d["month"]   = d["date"].dt.to_period("M")
    last_per     = d.sort_values("date").groupby(["month", "account_id"])["balance"].last().reset_index()
    totals       = last_per.groupby("month")["balance"].sum().reset_index()
    totals       = totals[totals["balance"] > 0].sort_values("month").tail(months).reset_index(drop=True)
    totals["month_str"]  = totals["month"].astype(str)
    totals["mom_change"] = totals["balance"].diff()
    return totals[["month_str", "balance", "mom_change"]].rename(columns={"balance": "total"})


def yearend_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Year-end totals with YoY change and % for each calendar year."""
    if df.empty:
        return pd.DataFrame(columns=["year", "total", "yoy_change", "yoy_pct"])
    d = df.copy()
    d["balance"] = pd.to_numeric(d["balance"], errors="coerce").fillna(0)
    d["year"]    = d["date"].dt.year
    last_per     = d.sort_values("date").groupby(["year", "account_id"])["balance"].last().reset_index()
    totals       = last_per.groupby("year")["balance"].sum().reset_index()
    totals       = totals[totals["balance"] > 0].sort_values("year").reset_index(drop=True)
    totals.rename(columns={"balance": "total"}, inplace=True)
    totals["yoy_change"] = totals["total"].diff()
    totals["yoy_pct"]    = totals["total"].pct_change() * 100
    return totals


# ── Projection engine ─────────────────────────────────────────────────────────

def project_retirement(
    accounts:             list[dict],
    start_balances:       dict[str, float],
    growth_rate:          float = 0.07,
    excluded:             Optional[set] = None,
    self_dob:             date = DEFAULT_SELF_DOB,
    spouse_dob:           date = DEFAULT_SPOUSE_DOB,
    start_year:           Optional[int] = None,
    end_year:             int = PROJECTION_END_YEAR,
    nonret_contributions: Optional[dict] = None,
) -> pd.DataFrame:
    """
    Project all accounts year-by-year to end_year.
    Each year: balance *= (1 + growth_rate), then add IRS-max contribution.
    nonret_contributions: {account_id: yearly_amount} for non-retirement accounts.
    Returns DataFrame: year, account_id, account_name, account_type, owner,
                       balance, contribution, growth_dollars
    """
    if excluded is None:
        excluded = set()
    if start_year is None:
        start_year = datetime.now().year
    if nonret_contributions is None:
        nonret_contributions = {}

    active = [a for a in accounts if a["account_id"] not in excluded]
    bals   = {a["account_id"]: float(start_balances.get(a["account_id"], 0)) for a in active}

    rows = []
    for year in range(start_year, end_year + 1):
        for acc in active:
            aid          = acc["account_id"]
            atype        = acc.get("account_type", "")
            owner        = acc.get("owner", "self")
            bal_open     = bals.get(aid, 0.0)
            growth_amt   = bal_open * growth_rate
            contrib      = get_annual_contribution(atype, owner, year, self_dob, spouse_dob)
            if contrib == 0.0:
                contrib = float(nonret_contributions.get(aid, 0.0))
            bal_close    = bal_open + growth_amt + contrib
            bals[aid]    = bal_close
            rows.append({
                "year":           year,
                "account_id":     aid,
                "account_name":   acc.get("account_name", ""),
                "account_type":   atype,
                "owner":          owner,
                "balance":        round(bal_close, 2),
                "contribution":   round(contrib, 2),
                "growth_dollars": round(growth_amt, 2),
            })

    return pd.DataFrame(rows) if rows else pd.DataFrame()

"""Google Sheets connector. All tabs auto-created if missing."""
import time
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Expected columns per tab — used to initialise empty sheets
TAB_SCHEMAS: dict[str, list[str]] = {
    "reminders":         ["id","section","title","message","due_date","remind_days","frequency","channels","status","created_at"],
    "accounts":          ["account_id","account_name","account_type","owner","active","broker_name","tax_status"],
    "account_balances":  ["date","account_id","account_name","balance"],
    "market_alerts":     ["id","ticker","condition","threshold","channels","active"],
    "brokers":           ["broker_id","broker_name","active"],
    "manual_accounts":   ["entry_date","account_name","owner","category","value","notes","created_at"],
    "AppSettings":       ["key","value"],
    "insurance_policies":["id","type","provider","policy_number","premium","frequency","due_date","notes","active"],
    "cc_cards":          ["id","name","bank","last4","annual_fee","fee_due_date","credit_limit","perks","active"],
    "classes":           ["id","child","name","provider","cost","fee_frequency","days","frequency","start_date","end_date","active","paused","time_start","time_end","location"],
    "expenses_log":      ["date","section","category","description","amount"],
    "tamil_reading_log": ["date","child","minutes","material"],
    "fisd_calendar":     ["date","event","type","source","school_year","fetched_at"],
    "staar_results":     ["id","date","child","grade","strand","score","total","pct"],
}


@st.cache_resource
def _get_client():
    creds_dict = dict(st.secrets["gsheet"])
    # Streamlit Cloud double-escapes \n in private_key — fix it
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(creds_dict, scopes=_SCOPES)
    return gspread.authorize(creds)


@st.cache_resource
def _get_spreadsheet():
    client = _get_client()
    return client.open_by_key(st.secrets["SPREADSHEET_ID"])


def _get_or_create_ws(tab: str) -> gspread.Worksheet:
    sh = _get_spreadsheet()
    try:
        ws = sh.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows=1000, cols=30)
        if tab in TAB_SCHEMAS:
            ws.append_row(TAB_SCHEMAS[tab])
        return ws
    # Migrate headers if schema has changed (adds missing columns, re-orders)
    _migrate_headers(ws, tab)
    return ws


def _migrate_headers(ws: gspread.Worksheet, tab: str) -> None:
    """If the sheet's header row doesn't match the schema, migrate in-place.

    Strategy: read existing data keyed by old headers, then rewrite with
    new headers. Missing new columns default to empty string.
    """
    expected = TAB_SCHEMAS.get(tab)
    if not expected:
        return
    current = ws.row_values(1)
    if current == expected:
        return  # already up to date

    # Read all existing data mapped by old column names
    try:
        old_records = ws.get_all_records(expected_headers=[])
    except Exception:
        old_records = []

    # Rewrite: header row + one row per old record mapped to new columns
    new_rows = [[rec.get(col, "") for col in expected] for rec in old_records]
    ws.clear()
    ws.append_row(expected)
    if new_rows:
        ws.append_rows(new_rows, value_input_option="USER_ENTERED")


def _is_rate_limit(exc: Exception) -> bool:
    """Return True if the exception is a Google API quota/rate-limit error."""
    msg = str(exc).lower()
    return any(k in msg for k in ("quota", "rate", "429", "resource_exhausted",
                                   "too many requests"))


def _read_sheet_raw(tab: str) -> pd.DataFrame:
    """Read a sheet tab with exponential-backoff retry on rate-limit errors."""
    max_attempts = 4
    delay = 2.0
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            ws   = _get_or_create_ws(tab)
            data = ws.get_all_records(expected_headers=[])
            if data:
                return pd.DataFrame(data)
            cols = TAB_SCHEMAS.get(tab, [])
            return pd.DataFrame(columns=cols)
        except gspread.exceptions.APIError as exc:
            last_exc = exc
            if _is_rate_limit(exc) and attempt < max_attempts - 1:
                time.sleep(delay)
                delay *= 2          # 2s → 4s → 8s
                continue
            raise                   # non-rate-limit API error — surface immediately
        except Exception:
            raise
    raise last_exc  # type: ignore[misc]


@st.cache_data(ttl=120)
def read_sheet(tab: str) -> pd.DataFrame:
    return _read_sheet_raw(tab)


def append_row(tab: str, row: list) -> None:
    ws = _get_or_create_ws(tab)
    ws.append_row(row, value_input_option="USER_ENTERED")
    read_sheet.clear()


def update_row(tab: str, row_idx: int, values: list) -> None:
    """row_idx is 1-based sheet row (2 = first data row)."""
    ws = _get_or_create_ws(tab)
    ws.update(f"A{row_idx}", [values])
    read_sheet.clear()


def delete_row(tab: str, row_idx: int) -> None:
    ws = _get_or_create_ws(tab)
    ws.delete_rows(row_idx)
    read_sheet.clear()


def overwrite_sheet(tab: str, df: pd.DataFrame) -> None:
    ws = _get_or_create_ws(tab)
    ws.clear()
    ws.update([df.columns.tolist()] + df.fillna("").values.tolist())
    read_sheet.clear()


def refresh_cache() -> None:
    read_sheet.clear()

"""Google Sheets connector. All tabs auto-created if missing."""
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
    "accounts":          ["account_id","account_name","account_type","owner","active"],
    "account_balances":  ["date","account_id","account_name","balance"],
    "market_alerts":     ["id","ticker","condition","threshold","channels","active"],
    "insurance_policies":["id","type","provider","policy_number","premium","frequency","due_date","notes","active"],
    "cc_cards":          ["id","name","bank","last4","annual_fee","fee_due_date","credit_limit","perks","active"],
    "classes":           ["id","child","name","provider","cost","frequency","start_date","end_date","active","days","time_start","time_end","location"],
    "expenses_log":      ["date","section","category","description","amount"],
    "tamil_reading_log": ["date","child","minutes","material"],
    "fisd_calendar":     ["date","event","type","source","school_year","fetched_at"],
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
        return sh.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows=1000, cols=30)
        if tab in TAB_SCHEMAS:
            ws.append_row(TAB_SCHEMAS[tab])
        return ws


@st.cache_data(ttl=120)
def read_sheet(tab: str) -> pd.DataFrame:
    ws = _get_or_create_ws(tab)
    data = ws.get_all_records()
    if data:
        return pd.DataFrame(data)
    cols = TAB_SCHEMAS.get(tab, [])
    return pd.DataFrame(columns=cols)


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

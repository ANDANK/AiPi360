"""
Portfolio persistent storage — reads/writes per-account trade data
to dedicated Google Sheets tabs.

Tab naming convention:
    TRX_{account_id}   — trade history
    POS_{account_id}   — open positions snapshot (equities + options)
    CASHF_{account_id} — cash flows (deposits / dividends / fees)

Account list comes from the shared 'accounts' GSheet tab.
"""

from datetime import date, datetime
from typing import Optional

import pandas as pd
import streamlit as st

from backend.gsheet import overwrite_sheet, read_sheet
from services.tos_parser import _trade_sig


# ── Column schemas ─────────────────────────────────────────────────────────────

TRX_COLS = [
    "date_str", "spread_type", "side", "qty", "pos_effect",
    "symbol", "expiry_str", "strike", "instr_type", "price",
    "is_option", "is_stock", "is_leaps", "strategy",
    "broker", "rh_trans_code", "fingerprint",
]

POS_COLS = [
    "pos_type",       # "equity" or "option"
    "symbol", "qty", "cost_basis", "mark", "mark_value",
    "pl_open", "pl_pct",
    "expiry_str", "strike", "opt_type", "days_to_exp", "is_short",
    "option_code", "description",
]

CASHF_COLS = [
    "date_str", "trans_code", "cash_type",
    "instrument", "description", "amount", "fingerprint",
]


# ── Serialise / deserialise helpers ───────────────────────────────────────────

def _b(v) -> str:
    return "TRUE" if v else "FALSE"


def _trade_to_row(t: dict) -> dict:
    return {
        "date_str":      t.get("date_str", ""),
        "spread_type":   t.get("spread_type", ""),
        "side":          t.get("side", ""),
        "qty":           t.get("qty", ""),
        "pos_effect":    t.get("pos_effect", ""),
        "symbol":        t.get("symbol", ""),
        "expiry_str":    t.get("expiry_str", ""),
        "strike":        t.get("strike", ""),
        "instr_type":    t.get("instr_type", ""),
        "price":         t.get("price", ""),
        "is_option":     _b(t.get("is_option", False)),
        "is_stock":      _b(t.get("is_stock", True)),
        "is_leaps":      _b(t.get("is_leaps", False)),
        "strategy":      t.get("strategy", ""),
        "broker":        t.get("broker", ""),
        "rh_trans_code": t.get("rh_trans_code", ""),
        "fingerprint":   _trade_sig(t),
    }


def _row_to_trade(row: dict) -> dict:
    """Reconstruct a trade dict from a stored GSheet row."""
    ds = str(row.get("date_str", "")).strip()
    dt = None
    if ds:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(ds, fmt)
                break
            except ValueError:
                pass

    es = str(row.get("expiry_str", "")).strip()
    expiry = None
    if es:
        try:
            expiry = datetime.strptime(es, "%d %b %y").date()
        except ValueError:
            pass

    def _flt(v):
        try:
            return float(v) if str(v).strip() not in ("", "None") else None
        except (ValueError, TypeError):
            return None

    def _int(v):
        try:
            return int(float(v)) if str(v).strip() not in ("", "None") else None
        except (ValueError, TypeError):
            return None

    def _bool(v):
        return str(v).upper() in ("TRUE", "1", "YES")

    return {
        "datetime":        dt,
        "date_str":        ds,
        "spread_type":     str(row.get("spread_type", "")),
        "side":            str(row.get("side", "")),
        "qty":             _int(row.get("qty")),
        "pos_effect":      str(row.get("pos_effect", "")),
        "symbol":          str(row.get("symbol", "")),
        "expiry":          expiry,
        "expiry_str":      es,
        "strike":          _flt(row.get("strike")),
        "instr_type":      str(row.get("instr_type", "")),
        "price":           _flt(row.get("price")),
        "net_price":       _flt(row.get("price")),
        "is_option":       _bool(row.get("is_option")),
        "is_stock":        _bool(row.get("is_stock")),
        "is_leaps":        _bool(row.get("is_leaps")),
        "is_continuation": False,
        "strategy":        str(row.get("strategy", "")),
        "broker":          str(row.get("broker", "")),
        "rh_trans_code":   str(row.get("rh_trans_code", "")),
    }


def _equity_to_row(e: dict) -> dict:
    return {
        "pos_type":   "equity",
        "symbol":     e.get("symbol", ""),
        "qty":        e.get("qty", ""),
        "cost_basis": e.get("cost_basis", ""),
        "mark":       e.get("mark", ""),
        "mark_value": e.get("mark_value", ""),
        "pl_open":    e.get("pl_open", ""),
        "pl_pct":     e.get("pl_pct", ""),
        "expiry_str": "",
        "strike":     "",
        "opt_type":   "",
        "days_to_exp": "",
        "is_short":   "",
        "option_code": "",
        "description": e.get("description", ""),
    }


def _option_to_row(o: dict) -> dict:
    return {
        "pos_type":    "option",
        "symbol":      o.get("symbol", ""),
        "qty":         o.get("qty", ""),
        "cost_basis":  o.get("cost_basis", ""),
        "mark":        o.get("mark", ""),
        "mark_value":  o.get("mark_value", ""),
        "pl_open":     o.get("pl_open", ""),
        "pl_pct":      o.get("pl_pct", ""),
        "expiry_str":  o.get("expiry_str", ""),
        "strike":      o.get("strike", ""),
        "opt_type":    o.get("opt_type", ""),
        "days_to_exp": o.get("days_to_exp", ""),
        "is_short":    _b(o.get("is_short", False)),
        "option_code": o.get("option_code", ""),
        "description": "",
    }


def _cf_to_row(cf: dict) -> dict:
    ds = cf.get("date_str", "")
    if not ds and cf.get("datetime"):
        try:
            ds = cf["datetime"].strftime("%Y-%m-%d")
        except Exception:
            ds = ""
    fp = f"{ds}|{cf.get('trans_code','')}|{cf.get('amount','')}"
    return {
        "date_str":    ds,
        "trans_code":  cf.get("trans_code", ""),
        "cash_type":   cf.get("cash_type", ""),
        "instrument":  cf.get("instrument", ""),
        "description": cf.get("description", ""),
        "amount":      cf.get("amount", ""),
        "fingerprint": fp,
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def list_broker_accounts() -> pd.DataFrame:
    """
    Return active accounts from the 'accounts' GSheet tab.
    Columns: account_id, account_name, account_type, owner, broker_name, tax_status
    """
    df = read_sheet("accounts")
    if df.empty:
        return pd.DataFrame(columns=["account_id", "account_name",
                                      "broker_name", "account_type", "owner"])
    active = df[df.get("active", pd.Series(["TRUE"] * len(df)))
                .astype(str).str.upper().isin(["TRUE", "1", "YES"])]
    return active.reset_index(drop=True)


def load_account_data(acct_id: str, acct_name: str = "") -> dict:
    """
    Load all persisted data for an account from GSheets.
    Returns the standard portfolio dict:
        {account_id, account_name, trades, equities, options, cash_flows, last_import}
    """
    trx_tab   = f"TRX_{acct_id}"
    pos_tab   = f"POS_{acct_id}"
    cashf_tab = f"CASHF_{acct_id}"

    # Transactions
    df_trx = read_sheet(trx_tab)
    trades = [_row_to_trade(r) for _, r in df_trx.iterrows()] if not df_trx.empty else []

    # Positions
    equities: list[dict] = []
    options:  list[dict] = []
    df_pos = read_sheet(pos_tab)
    if not df_pos.empty:
        for _, r in df_pos.iterrows():
            row = r.to_dict()
            if row.get("pos_type") == "equity":
                equities.append({
                    "symbol":      row.get("symbol", ""),
                    "qty":         _safe_int(row.get("qty")),
                    "cost_basis":  _safe_float(row.get("cost_basis")),
                    "mark":        _safe_float(row.get("mark")),
                    "mark_value":  _safe_float(row.get("mark_value")),
                    "pl_open":     _safe_float(row.get("pl_open")),
                    "pl_pct":      _safe_float(row.get("pl_pct")),
                    "description": row.get("description", ""),
                })
            else:
                options.append({
                    "symbol":      row.get("symbol", ""),
                    "qty":         _safe_int(row.get("qty")),
                    "cost_basis":  _safe_float(row.get("cost_basis")),
                    "mark":        _safe_float(row.get("mark")),
                    "mark_value":  _safe_float(row.get("mark_value")),
                    "pl_open":     _safe_float(row.get("pl_open")),
                    "pl_pct":      _safe_float(row.get("pl_pct")),
                    "expiry_str":  row.get("expiry_str", ""),
                    "strike":      _safe_float(row.get("strike")),
                    "opt_type":    row.get("opt_type", ""),
                    "days_to_exp": _safe_int(row.get("days_to_exp")),
                    "is_short":    str(row.get("is_short", "")).upper() == "TRUE",
                    "option_code": row.get("option_code", ""),
                })

    # Cash flows
    df_cf = read_sheet(cashf_tab)
    cash_flows: list[dict] = []
    if not df_cf.empty:
        for _, r in df_cf.iterrows():
            row = r.to_dict()
            ds  = str(row.get("date_str", ""))
            dt  = None
            if ds:
                try:
                    dt = datetime.strptime(ds, "%Y-%m-%d")
                except ValueError:
                    pass
            cash_flows.append({
                "datetime":    dt,
                "date_str":    ds,
                "trans_code":  row.get("trans_code", ""),
                "cash_type":   row.get("cash_type", ""),
                "instrument":  row.get("instrument", ""),
                "description": row.get("description", ""),
                "amount":      _safe_float(row.get("amount")),
            })

    return {
        "account_id":   acct_id,
        "account_name": acct_name,
        "trades":       trades,
        "equities":     equities,
        "options":      options,
        "cash_flows":   cash_flows,
        "last_import":  df_trx.attrs.get("last_import", "") if not df_trx.empty else "",
    }


def clear_account_data(acct_id: str, clear_positions: bool = True) -> dict:
    """
    Wipe all stored data for an account from GSheets.
    Returns {tabs_cleared: list[str]}.
    Useful before a full clean re-import to avoid stale / duplicate rows.
    """
    from backend.gsheet import _get_or_create_ws
    cleared = []
    tabs = [f"TRX_{acct_id}", f"CASHF_{acct_id}"]
    if clear_positions:
        tabs.append(f"POS_{acct_id}")

    for tab in tabs:
        try:
            ws = _get_or_create_ws(tab)
            ws.clear()
            cleared.append(tab)
        except Exception:
            pass   # tab might not exist yet — that's fine

    # Bust read cache so subsequent loads see empty sheets
    from backend.gsheet import read_sheet
    read_sheet.clear()

    return {"tabs_cleared": cleared}


def save_upload(acct_id: str, parsed: dict) -> dict:
    """
    Delta-merge new upload data into GSheets for this account.
    Returns stats: {new_trades, new_cashflows}.
    """
    new_trades = parsed.get("trades", [])
    new_cf     = parsed.get("cash_flows", [])
    new_eq     = parsed.get("equities", [])
    new_opt    = parsed.get("options", [])

    # ── Transactions (delta merge) ────────────────────────────────────────────
    trx_tab = f"TRX_{acct_id}"
    existing_trx = read_sheet(trx_tab)
    seen_fp = set()
    if not existing_trx.empty and "fingerprint" in existing_trx.columns:
        seen_fp = set(existing_trx["fingerprint"].astype(str).tolist())

    added_rows = []
    for t in new_trades:
        fp = _trade_sig(t)
        if fp not in seen_fp:
            row = _trade_to_row(t)
            added_rows.append(row)
            seen_fp.add(fp)

    if added_rows:
        new_df = pd.DataFrame(added_rows, columns=TRX_COLS)
        if existing_trx.empty:
            overwrite_sheet(trx_tab, new_df)
        else:
            # Align columns before concat
            for col in TRX_COLS:
                if col not in existing_trx.columns:
                    existing_trx[col] = ""
            combined = pd.concat(
                [existing_trx[TRX_COLS], new_df],
                ignore_index=True,
            )
            overwrite_sheet(trx_tab, combined)

    # ── Cash flows (delta merge) ──────────────────────────────────────────────
    cashf_tab = f"CASHF_{acct_id}"
    existing_cf = read_sheet(cashf_tab)
    seen_cf_fp  = set()
    if not existing_cf.empty and "fingerprint" in existing_cf.columns:
        seen_cf_fp = set(existing_cf["fingerprint"].astype(str).tolist())

    added_cf = []
    for cf in new_cf:
        row = _cf_to_row(cf)
        fp  = row["fingerprint"]
        if fp not in seen_cf_fp:
            added_cf.append(row)
            seen_cf_fp.add(fp)

    if added_cf:
        new_cf_df = pd.DataFrame(added_cf, columns=CASHF_COLS)
        if existing_cf.empty:
            overwrite_sheet(cashf_tab, new_cf_df)
        else:
            for col in CASHF_COLS:
                if col not in existing_cf.columns:
                    existing_cf[col] = ""
            combined_cf = pd.concat(
                [existing_cf[CASHF_COLS], new_cf_df],
                ignore_index=True,
            )
            overwrite_sheet(cashf_tab, combined_cf)

    # ── Open positions (always replace snapshot) ──────────────────────────────
    pos_tab = f"POS_{acct_id}"
    pos_rows = [_equity_to_row(e) for e in new_eq] + \
               [_option_to_row(o) for o in new_opt]
    if pos_rows:
        overwrite_sheet(pos_tab, pd.DataFrame(pos_rows, columns=POS_COLS))
    elif new_eq == [] and new_opt == []:
        pass   # RH file — don't wipe existing snapshot if file has no positions

    return {
        "new_trades":     len(added_rows),
        "new_cashflows":  len(added_cf),
        "positions_saved": bool(pos_rows),
    }


# ── Private numeric helpers ───────────────────────────────────────────────────

def _safe_float(v) -> Optional[float]:
    try:
        s = str(v).strip().replace("$", "").replace(",", "")
        return float(s) if s and s not in ("None", "") else None
    except (ValueError, TypeError):
        return None


def _safe_int(v) -> Optional[int]:
    try:
        s = str(v).strip()
        return int(float(s)) if s and s not in ("None", "") else None
    except (ValueError, TypeError):
        return None

"""
Portfolio & Trading Accounts
Import ToS / Schwab account statements → view positions, trade log, P&L, insights.
Supports delta uploads (append new trades, replace open positions snapshot).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datetime as _dt
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="AiPi360 · Portfolio", page_icon="💼", layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css, inject_global_nav_css

require_auth()
check_maintenance()
check_page_access("portfolio")
inject_3d_tab_css()
inject_global_nav_css()

from services.tos_parser import (
    compute_realized_pnl,
    detect_broker,
    merge_upload,
    parse_broker_csv,
    peek_rh_account,
)
from services.portfolio_store import (
    list_broker_accounts,
    load_account_data,
    save_upload,
    clear_account_data,
)

st.title("💼 Portfolio & Trading Accounts")
st.caption("Persistent account data from GSheets. Import new trades any time — no re-upload needed to view existing data.")

# ── Load accounts from GSheet ─────────────────────────────────────────────────
@st.cache_data(ttl=120)
def _load_gsheet_accounts():
    return list_broker_accounts()

gsheet_accounts = _load_gsheet_accounts()

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL ACCOUNT SELECTOR  (above all tabs)
# ══════════════════════════════════════════════════════════════════════════════
def _build_global_selector() -> list[dict]:
    """
    Render a single multi-select account picker above the tabs.
    Returns a merged account-data dict (trades / equities / options / cash_flows
    combined from all selected accounts).
    Returns [] if no accounts or none selected.
    """
    if gsheet_accounts.empty:
        return []

    acct_list = gsheet_accounts[["account_id", "account_name", "broker_name"]].copy()
    acct_list["label"] = acct_list["account_name"] + " (" + acct_list["broker_name"] + ")"
    id_to_label = dict(zip(acct_list["account_id"], acct_list["label"]))
    all_ids     = list(id_to_label.keys())

    # Persist selection across reruns
    if "port_sel_accts" not in st.session_state:
        st.session_state["port_sel_accts"] = [all_ids[0]] if all_ids else []

    col_sel, col_all, col_none = st.columns([6, 1, 1])
    with col_sel:
        selected = st.multiselect(
            "📂 Accounts",
            options=all_ids,
            default=st.session_state["port_sel_accts"],
            format_func=lambda x: id_to_label[x],
            key="port_acct_multi",
            label_visibility="collapsed",
        )
    with col_all:
        if st.button("All", key="port_sel_all", use_container_width=True):
            st.session_state["port_sel_accts"] = all_ids
            st.rerun()
    with col_none:
        if st.button("Clear", key="port_sel_none", use_container_width=True):
            st.session_state["port_sel_accts"] = []
            st.rerun()

    st.session_state["port_sel_accts"] = selected

    if not selected:
        st.info("Select at least one account above.")
        return []

    # Load & merge all selected accounts; tag each trade with its account name
    merged = {"trades": [], "equities": [], "options": [], "cash_flows": [],
              "account_name": ""}
    names = []
    for acct_id in selected:
        row       = gsheet_accounts[gsheet_accounts["account_id"] == acct_id].iloc[0]
        acct_name = row["account_name"]
        acct_data = load_account_data(acct_id, acct_name)
        # Tag trades with account name so Trade Log / P&L can show source
        tagged_trades = [{**t, "_account": acct_name}
                         for t in acct_data.get("trades", [])]
        merged["trades"]      += tagged_trades
        merged["equities"]    += acct_data.get("equities", [])
        merged["options"]     += acct_data.get("options", [])
        merged["cash_flows"]  += acct_data.get("cash_flows", [])
        names.append(acct_name)
    merged["account_name"] = " + ".join(names)
    return merged


# Render selector and load data once — reused by all tabs
with st.container():
    acct_data_global = _build_global_selector()
    if acct_data_global:
        st.caption(f"Viewing: **{acct_data_global['account_name']}** · "
                   f"{len(acct_data_global['trades']):,} trades · "
                   f"{len(acct_data_global['equities'])} equity positions · "
                   f"{len(acct_data_global['options'])} option positions")
    st.divider()

# ── Colour helpers ────────────────────────────────────────────────────────────
_GREEN  = "#16a34a"
_RED    = "#dc2626"
_AMBER  = "#d97706"
_BLUE   = "#2563eb"
_MUTED  = "#64748b"

def _pnl_color(v) -> str:
    if v is None: return _MUTED
    return _GREEN if v >= 0 else _RED

def _fmt_pnl(v) -> str:
    if v is None: return "—"
    return f"+${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"

def _fmt_pct(v) -> str:
    if v is None: return "—"
    return f"{v:+.1f}%"

def _color_df_pnl(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Return styled dataframe with green/red for a P&L column."""
    return df.style.map(
        lambda x: (f"color:{_GREEN};font-weight:600" if isinstance(x, (int, float)) and x > 0
                   else f"color:{_RED};font-weight:600"  if isinstance(x, (int, float)) and x < 0
                   else ""),
        subset=[col],
    )


# ─────────────────────────────────────────────────────────────────────────────
# TOP-LEVEL TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_import, tab_pos, tab_log, tab_pnl, tab_insights = st.tabs([
    "📤 Import", "💼 Open Positions", "📋 Trade Log",
    "💰 P&L Analysis", "🔍 Insights",
])

# ══════════════════════════════════════════════════════════════════════════════
# 1 · IMPORT TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_import:
    st.markdown("### 📤 Upload New Trades")
    st.caption("Select an account and upload a fresh CSV. New trades are added automatically; existing data is never overwritten.")

    if gsheet_accounts.empty:
        st.warning("No accounts found in GSheets. Create an account in Account Tracker first.")
        st.stop()

    # ── Account dropdown ──────────────────────────────────────────────────────
    acct_list = gsheet_accounts[["account_id", "account_name", "broker_name"]].copy()
    acct_list["label"] = acct_list["account_name"] + " · " + acct_list["broker_name"]
    acct_options = dict(zip(acct_list["account_id"], acct_list["label"]))

    sel_id = st.selectbox("Select account to update:", acct_options.keys(),
                          format_func=lambda x: acct_options[x],
                          key="port_acct_dropdown")
    sel_row = gsheet_accounts[gsheet_accounts["account_id"] == sel_id].iloc[0]
    sel_name = sel_row["account_name"]

    st.divider()

    # ── File upload ───────────────────────────────────────────────────────────
    with st.expander("📋 How to export from your broker", expanded=False):
        st.markdown(
            "**Schwab Transaction History** *(recommended — includes net_price)*\n"
            "1. schwab.com → Accounts → History\n"
            "2. Select account, set date range\n"
            "3. Click **Export** (CSV) — file starts with `Date,Action,Symbol,...`\n\n"
            "**ToS / Schwab Account Statement** *(thinkorswim)*\n"
            "1. thinkorswim → Monitor → Account Statement\n"
            "2. Expand: Account Trade History, Equities, Options\n"
            "3. Export to File (CSV)\n\n"
            "**Robinhood:**\n"
            "1. Account → History → Export\n\n"
            "**Fidelity:**\n"
            "1. Accounts & Trade → Account History\n"
            "2. Select date range → Download (CSV)\n\n"
            "> Remove any row with your account number before uploading."
        )

    uploaded = st.file_uploader(
        f"Upload CSV for {sel_name}:",
        type=["csv"],
        key="port_upload",
    )

    if uploaded:
        content = uploaded.read().decode("utf-8", errors="replace")
        from services.tos_parser import _rh_clean, _rh_delimiter

        # Auto-detect broker
        broker = detect_broker(content)

        if broker == "robinhood":
            _delim = _rh_delimiter(content)
            _delim_label = "tab-separated" if _delim == "\t" else "comma-separated"
            st.caption(f"🟣 **Robinhood** ({_delim_label})")
        elif broker == "tos":
            st.caption("🟢 **ToS / Schwab** (Account Statement)")
        elif broker == "schwab_tx":
            st.caption("🟢 **Schwab Transaction History** (includes net commission price)")
        elif broker == "fidelity":
            st.caption("🔵 **Fidelity** Account History")
        else:
            st.error(f"Unrecognized format. First 150 chars: `{content[:150]}`")
            st.stop()

        # Parse
        try:
            if broker == "robinhood":
                _peeked = peek_rh_account(content)
                parsed = parse_broker_csv(content, rh_account_name=sel_name)
            else:
                parsed = parse_broker_csv(content, rh_account_name=sel_name)
        except Exception as e:
            st.error(f"Parse error: {e}")
            st.stop()

        # Show what will be uploaded
        st.info(
            f"**Found:** {len(parsed['trades'])} trades  ·  "
            f"{len(parsed['equities'])} open equities  ·  "
            f"{len(parsed['options'])} open options"
        )

        if st.button("✅  Save to Portfolio", type="primary", key="port_do_save"):
            with st.spinner("Saving to GSheets..."):
                result = save_upload(sel_id, parsed)
            _load_gsheet_accounts.clear()
            # Store result in session state so success banner persists after rerun
            st.session_state["port_import_result"] = {
                "new_trades":      result["new_trades"],
                "new_cashflows":   result["new_cashflows"],
                "positions_saved": result["positions_saved"],
                "acct_id":         sel_id,
            }
            st.rerun()

# ── Post-import success banner + Refresh button (outside upload block) ────────
if st.session_state.get("port_import_result"):
    _res = st.session_state["port_import_result"]
    st.success(
        f"✅ Imported! New trades: **{_res['new_trades']}**  ·  "
        f"New cash flows: **{_res['new_cashflows']}**  ·  "
        f"Positions updated: **{_res['positions_saved']}**"
    )
    if st.button("🔄  Refresh All Tabs", type="secondary", key="port_refresh"):
        del st.session_state["port_import_result"]
        st.rerun()

# ── Danger zone: Clear & Re-import ───────────────────────────────────────────
with tab_import:
    st.divider()
    with st.expander("🗑️  Clear Account Data (for clean re-import)", expanded=False):
        st.warning(
            "**This permanently deletes all stored trades, cash flows, and positions "
            f"for the selected account from GSheets.**  \n"
            "Use this when you want to re-import from scratch with corrected data. "
            "The account itself (in Account Tracker) is NOT affected."
        )

        # Two-step confirmation: checkbox then button
        confirmed = st.checkbox(
            f"Yes, I want to clear all data for **{sel_name}**",
            key="port_clear_confirm",
        )
        if confirmed:
            if st.button("🗑️  Clear All Data Now", type="primary",
                         key="port_clear_go"):
                with st.spinner(f"Clearing data for {sel_name}…"):
                    result = clear_account_data(sel_id, clear_positions=True)
                cleared_list = ", ".join(result["tabs_cleared"]) or "none"
                st.success(
                    f"✅ Cleared {len(result['tabs_cleared'])} tabs: `{cleared_list}`  \n"
                    "You can now upload fresh CSV files for this account."
                )
                _load_gsheet_accounts.clear()
                st.session_state.pop("port_clear_confirm", None)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 2 · OPEN POSITIONS TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_pos:
    st.markdown("### 💼 Open Positions")
    acct_data = acct_data_global
    if acct_data:
        eq_tab, opt_tab = st.tabs(["📈 Equities", "🎯 Options"])

        # ── Equities ─────────────────────────────────────────────────────────
        with eq_tab:
            eq = acct_data.get("equities", [])
            if not eq:
                st.info("No open equity positions in this account.")
            else:
                df_eq = pd.DataFrame(eq)
                # Summary row
                total_val = sum(r["mark_value"] for r in eq if r["mark_value"])
                total_pnl = sum(r["pl_open"]    for r in eq if r["pl_open"])
                c1, c2, c3 = st.columns(3)
                c1.metric("Open Positions", len(eq))
                c2.metric("Total Mark Value",  f"${total_val:,.0f}" if total_val else "—")
                c3.metric("Unrealized P&L",
                          _fmt_pnl(total_pnl),
                          delta=_fmt_pct(total_pnl / (total_val - total_pnl) * 100
                                         if total_val and total_pnl else None))

                disp = df_eq[["symbol", "qty", "cost_basis", "mark",
                               "mark_value", "pl_open", "pl_pct", "description"]].copy()
                disp.columns = ["Symbol", "Qty", "Avg Cost", "Mark",
                                 "Mark Value ($)", "P/L Open ($)", "P/L %", "Description"]
                st.dataframe(
                    _color_df_pnl(disp, "P/L Open ($)"),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Avg Cost":       st.column_config.NumberColumn(format="$%.2f"),
                        "Mark":           st.column_config.NumberColumn(format="$%.2f"),
                        "Mark Value ($)": st.column_config.NumberColumn(format="$%,.0f"),
                        "P/L Open ($)":   st.column_config.NumberColumn(format="$%+,.0f"),
                        "P/L %":          st.column_config.NumberColumn(format="%+.1f%%"),
                    },
                )

        # ── Options ──────────────────────────────────────────────────────────
        with opt_tab:
            opts = acct_data.get("options", [])
            if not opts:
                st.info("No open option positions in this account.")
            else:
                df_opt  = pd.DataFrame(opts)
                total_val_o = sum(r["mark_value"] for r in opts if r["mark_value"])
                total_pnl_o = sum(r["pl_open"]    for r in opts if r["pl_open"])
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Open Contracts", len(opts))
                c2.metric("Total Mark Value",  f"${total_val_o:,.0f}" if total_val_o else "—")
                c3.metric("Unrealized P&L",    _fmt_pnl(total_pnl_o))
                longs  = sum(1 for o in opts if (o.get("qty") or 0) > 0)
                shorts = sum(1 for o in opts if (o.get("qty") or 0) < 0)
                c4.metric("Long / Short", f"{longs} / {shorts}")

                disp_o = df_opt[["symbol", "opt_type", "expiry_str", "strike",
                                  "qty", "cost_basis", "mark",
                                  "mark_value", "pl_open", "pl_pct",
                                  "days_to_exp"]].copy()
                disp_o.columns = ["Symbol", "Type", "Expiry", "Strike",
                                   "Qty", "Avg Cost", "Mark",
                                   "Value ($)", "P/L ($)", "P/L %", "DTE"]
                # Highlight short positions
                def _opt_row_style(row):
                    if row["Qty"] < 0:
                        return ["background-color:#fff9f0"] * len(row)
                    return [""] * len(row)

                styled_o = disp_o.style.apply(_opt_row_style, axis=1).map(
                    lambda x: (f"color:{_GREEN};font-weight:600" if isinstance(x, (int, float)) and x > 0
                               else f"color:{_RED};font-weight:600" if isinstance(x, (int, float)) and x < 0
                               else ""),
                    subset=["P/L ($)"],
                )
                st.dataframe(
                    styled_o,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Strike":   st.column_config.NumberColumn(format="$%.1f"),
                        "Avg Cost": st.column_config.NumberColumn(format="$%.2f"),
                        "Mark":     st.column_config.NumberColumn(format="$%.3f"),
                        "Value ($)":st.column_config.NumberColumn(format="$%,.0f"),
                        "P/L ($)":  st.column_config.NumberColumn(format="$%+,.0f"),
                        "P/L %":    st.column_config.NumberColumn(format="%+.1f%%"),
                        "DTE":      st.column_config.NumberColumn(format="%d days"),
                    },
                )
                st.caption("⬜ Yellow rows = short positions (CSP / CC / sold options)")


# ══════════════════════════════════════════════════════════════════════════════
# 3 · TRADE LOG TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_log:
    st.markdown("### 📋 Trade Log")
    acct_data = acct_data_global
    if acct_data:
        trades = acct_data.get("trades", [])
        if not trades:
            st.info("No trades in this account.")
        else:
            df_all = pd.DataFrame(trades)

            # ── Filters ───────────────────────────────────────────────────────
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                syms = sorted(df_all["symbol"].dropna().unique().tolist())
                filt_sym = st.multiselect("Symbol", syms, key="log_sym")
            with fc2:
                strats = sorted(df_all["strategy"].dropna().unique().tolist())
                filt_strat = st.multiselect("Strategy", strats, key="log_strat")
            with fc3:
                sides = ["BUY", "SELL"]
                filt_side = st.multiselect("Side", sides, key="log_side")
            with fc4:
                filt_cont = st.checkbox("Hide continuation legs", value=True, key="log_cont")

            mask = pd.Series([True] * len(df_all))
            if filt_sym:
                mask &= df_all["symbol"].isin(filt_sym)
            if filt_strat:
                mask &= df_all["strategy"].isin(filt_strat)
            if filt_side:
                mask &= df_all["side"].isin(filt_side)
            if filt_cont:
                mask &= ~df_all["is_continuation"].fillna(False)

            filtered = df_all[mask].copy()

            st.caption(f"Showing {len(filtered):,} of {len(df_all):,} trades")

            show_acct_col = "_account" in df_all.columns and \
                            df_all["_account"].nunique() > 1
            disp_cols = ["date_str", "symbol", "spread_type", "side", "qty",
                         "pos_effect", "instr_type", "expiry_str", "strike",
                         "price", "strategy"]
            rename_map = {
                "date_str":    "Date",
                "symbol":      "Symbol",
                "spread_type": "Spread",
                "side":        "Side",
                "qty":         "Qty",
                "pos_effect":  "Position",
                "instr_type":  "Type",
                "expiry_str":  "Expiry",
                "strike":      "Strike",
                "price":       "Price",
                "strategy":    "Strategy",
            }
            if show_acct_col:
                disp_cols = ["_account"] + disp_cols
                rename_map["_account"] = "Account"
            disp = filtered[disp_cols].rename(columns=rename_map)

            def _side_color(row):
                color = "#dcfce7" if row["Side"] == "BUY" else "#fee2e2"
                return [f"background-color:{color}" if c == "Side" else "" for c in row.index]

            st.dataframe(
                disp.style.apply(_side_color, axis=1),
                use_container_width=True,
                hide_index=True,
                height=480,
                column_config={
                    "Strike": st.column_config.NumberColumn(format="$%.2f"),
                    "Price":  st.column_config.NumberColumn(format="$%.2f"),
                    "Qty":    st.column_config.NumberColumn(format="%d"),
                },
            )


# ══════════════════════════════════════════════════════════════════════════════
# 4 · P&L ANALYSIS TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_pnl:
    st.markdown("### 💰 Realized P&L Analysis")
    acct_data = acct_data_global
    if acct_data:
        trades = acct_data.get("trades", [])
        if not trades:
            st.info("No trades to analyze.")
        else:
            # ── Recalculate controls ──────────────────────────────────────────
            rc1, rc2, rc3 = st.columns([2, 2, 2])
            with rc1:
                comm_correct = st.toggle(
                    "💡 Commission correction",
                    value=st.session_state.get("pnl_comm_correct", True),
                    help=(
                        "Subtracts estimated broker commissions ($0.65/contract/leg "
                        "for Schwab/Fidelity, $0 for Robinhood) from each option trade. "
                        "Use this until data is re-uploaded with the new net_price column. "
                        "New uploads store net_price automatically and won't be double-counted."
                    ),
                    key="pnl_comm_toggle",
                )
                st.session_state["pnl_comm_correct"] = comm_correct
            with rc2:
                if st.button("🔄 Recalculate P&L", key="pnl_recalc",
                             help="Force fresh P&L computation — clears cached results"):
                    for k in [k for k in st.session_state if k.startswith("pnl_cache_")]:
                        del st.session_state[k]
                    st.rerun()

            # Cache key includes the commission flag so toggling auto-recalculates
            _cache_key = f"pnl_cache_{id(trades)}_{comm_correct}"
            if _cache_key not in st.session_state:
                with st.spinner("Matching open/close pairs…"):
                    st.session_state[_cache_key] = compute_realized_pnl(
                        trades, commission_correct=comm_correct
                    )
            df_pnl_all = st.session_state[_cache_key]

            if df_pnl_all.empty:
                st.warning("No matched open/close pairs found yet. "
                           "Trades may still be open or data may be incomplete.")
            else:
                # ── Date filter ───────────────────────────────────────────────
                df_pnl_all["close_date"] = pd.to_datetime(df_pnl_all["close_date"])
                min_dt = df_pnl_all["close_date"].min().date()
                max_dt = df_pnl_all["close_date"].max().date()

                # Build YYYY and YYYY-MMM choices from actual data
                years   = sorted(df_pnl_all["close_date"].dt.year.unique(), reverse=True)
                months  = sorted(
                    df_pnl_all["close_date"].dt.to_period("M").astype(str).unique(),
                    reverse=True,
                )  # e.g. "2026-05", "2026-04", ...

                dc1, dc2, dc3 = st.columns([1, 2, 3])
                with dc1:
                    filter_mode = st.radio(
                        "Filter by", ["All time", "Year", "Month", "Custom range"],
                        key="pnl_filter_mode", horizontal=False,
                    )
                with dc2:
                    if filter_mode == "Year":
                        sel_year = st.selectbox(
                            "Year", [str(y) for y in years], key="pnl_year"
                        )
                    elif filter_mode == "Month":
                        sel_month = st.selectbox(
                            "Month (YYYY-MM)", months, key="pnl_month"
                        )
                    elif filter_mode == "Custom range":
                        cr1, cr2 = st.columns(2)
                        with cr1:
                            date_from = st.date_input(
                                "From", value=min_dt, min_value=min_dt,
                                max_value=max_dt, key="pnl_from"
                            )
                        with cr2:
                            date_to = st.date_input(
                                "To", value=max_dt, min_value=min_dt,
                                max_value=max_dt, key="pnl_to"
                            )

                # Apply filter
                if filter_mode == "Year":
                    df_pnl = df_pnl_all[df_pnl_all["close_date"].dt.year == int(sel_year)].copy()
                    period_label = sel_year
                elif filter_mode == "Month":
                    y, m  = int(sel_month[:4]), int(sel_month[5:])
                    df_pnl = df_pnl_all[
                        (df_pnl_all["close_date"].dt.year  == y) &
                        (df_pnl_all["close_date"].dt.month == m)
                    ].copy()
                    period_label = _dt.date(y, m, 1).strftime("%B %Y")
                elif filter_mode == "Custom range":
                    df_pnl = df_pnl_all[
                        (df_pnl_all["close_date"].dt.date >= date_from) &
                        (df_pnl_all["close_date"].dt.date <= date_to)
                    ].copy()
                    period_label = f"{date_from} → {date_to}"
                else:
                    df_pnl = df_pnl_all.copy()
                    period_label = "All time"

                with dc3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if df_pnl.empty:
                        st.warning("No closed trades in this period.")
                    else:
                        st.info(f"📅 **{period_label}** · {len(df_pnl)} closed trades")

                if df_pnl.empty:
                    st.stop()

                # ── Cash Activity (deposits / withdrawals) ────────────────────
                raw_cf = acct_data.get("cash_flows", [])
                if raw_cf:
                    df_cf = pd.DataFrame(raw_cf)
                    df_cf["datetime"] = pd.to_datetime(df_cf["datetime"], errors="coerce")
                    # Apply same date filter as trades
                    if filter_mode == "Year":
                        cf_mask = df_cf["datetime"].dt.year == int(sel_year)
                    elif filter_mode == "Month":
                        y2, m2 = int(sel_month[:4]), int(sel_month[5:])
                        cf_mask = (
                            (df_cf["datetime"].dt.year == y2) &
                            (df_cf["datetime"].dt.month == m2)
                        )
                    elif filter_mode == "Custom range":
                        cf_mask = (
                            (df_cf["datetime"].dt.date >= date_from) &
                            (df_cf["datetime"].dt.date <= date_to)
                        )
                    else:
                        cf_mask = pd.Series([True] * len(df_cf))
                    df_cf = df_cf[cf_mask].copy()

                    if not df_cf.empty:
                        st.markdown("#### 💵 Cash Activity")
                        # Deposits (positive ACH/transfers)
                        dep_codes   = {"ACH", "ITRF", "T/A", "ACATO", "REC"}
                        withdrawals = df_cf[df_cf["cash_type"] == "Transfer"][
                            "amount"].apply(lambda x: x if (x or 0) < 0 else 0).sum()
                        deposits    = df_cf[df_cf["cash_type"] == "Transfer"][
                            "amount"].apply(lambda x: x if (x or 0) > 0 else 0).sum()
                        dividends   = df_cf[df_cf["cash_type"] == "Dividend"]["amount"].sum()
                        interest    = df_cf[df_cf["cash_type"] == "Interest"]["amount"].sum()
                        fees        = df_cf[df_cf["cash_type"].isin(
                            ["Gold Fee", "Fee"])]["amount"].sum()
                        gold_cr     = df_cf[df_cf["cash_type"] == "Gold Credit"]["amount"].sum()
                        other       = df_cf[~df_cf["cash_type"].isin(
                            ["Transfer", "Dividend", "Interest",
                             "Gold Fee", "Fee", "Gold Credit"])]["amount"].sum()

                        ca1, ca2, ca3, ca4, ca5, ca6 = st.columns(6)
                        ca1.metric("Deposits",    _fmt_pnl(deposits)    if deposits    else "—")
                        ca2.metric("Withdrawals", _fmt_pnl(withdrawals) if withdrawals else "—")
                        ca3.metric("Dividends",   _fmt_pnl(dividends)   if dividends   else "—")
                        ca4.metric("Interest",    _fmt_pnl(interest)    if interest    else "—")
                        ca5.metric("Fees",        _fmt_pnl(fees)        if fees        else "—")
                        ca6.metric("Net Cash In", _fmt_pnl(
                            (deposits or 0) + (withdrawals or 0) +
                            (dividends or 0) + (interest or 0) + (fees or 0) + (gold_cr or 0)
                        ))

                        with st.expander("📄 Cash Activity Detail", expanded=False):
                            cf_disp = df_cf[["date_str", "trans_code", "cash_type",
                                             "instrument", "description", "amount"]].copy()
                            cf_disp.columns = ["Date", "Code", "Type",
                                               "Symbol", "Description", "Amount ($)"]
                            st.dataframe(
                                _color_df_pnl(cf_disp, "Amount ($)"),
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Amount ($)": st.column_config.NumberColumn(
                                        format="$%+,.2f"),
                                },
                            )
                        st.divider()
                else:
                    st.caption("💵 Cash activity (deposits / withdrawals / dividends) "
                               "is available for Robinhood imports only. "
                               "ToS trade history exports do not include cash transactions.")
                    st.divider()

                total_pnl   = df_pnl["pnl"].sum()
                winners     = df_pnl[df_pnl["winner"] == True]
                losers      = df_pnl[df_pnl["winner"] == False]
                win_rate    = len(winners) / len(df_pnl) * 100 if len(df_pnl) else 0
                avg_win     = winners["pnl"].mean() if len(winners) else 0
                avg_loss    = losers["pnl"].mean()  if len(losers)  else 0
                profit_factor = abs(winners["pnl"].sum() / losers["pnl"].sum()) \
                                if losers["pnl"].sum() != 0 else float("inf")

                # ── Options vs Stock breakdown ────────────────────────────────
                opt_pnl   = df_pnl[df_pnl["opt_type"] != ""]["pnl"].sum()
                stock_pnl = df_pnl[df_pnl["opt_type"] == ""]["pnl"].sum()
                sb1, sb2, sb3 = st.columns(3)
                sb1.metric("Total Realized P&L", _fmt_pnl(total_pnl))
                sb2.metric("Options P&L",         _fmt_pnl(opt_pnl),
                           help="Realized P&L from options trades (premiums)")
                sb3.metric("Stock P&L",            _fmt_pnl(stock_pnl),
                           help="Realized P&L from stock/ETF trades. "
                                "Note: all-time stock P&L may include gains from "
                                "option exercise deliveries which Robinhood may "
                                "account for differently.")
                st.divider()

                # ── Summary metrics ───────────────────────────────────────────
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Trades", len(df_pnl))
                m2.metric("Win Rate", f"{win_rate:.0f}%")
                m3.metric("Avg Winner / Loser",
                          f"${avg_win:,.0f} / ${avg_loss:,.0f}")
                m4.metric("Profit Factor", f"{profit_factor:.2f}"
                          if profit_factor != float("inf") else "∞")

                st.divider()

                # ── Strategy breakdown ────────────────────────────────────────
                strat_grp = (
                    df_pnl.groupby("strategy")
                    .agg(
                        Trades=("pnl", "count"),
                        Total_PnL=("pnl", "sum"),
                        Win_Rate=("winner", lambda x: f"{x.mean()*100:.0f}%"),
                        Avg_PnL=("pnl", "mean"),
                        Avg_Hold=("hold_days", "mean"),
                    )
                    .rename(columns={"Total_PnL": "Total P&L ($)",
                                     "Win_Rate":  "Win Rate",
                                     "Avg_PnL":   "Avg P&L ($)",
                                     "Avg_Hold":  "Avg Hold (days)"})
                    .sort_values("Total P&L ($)", ascending=False)
                    .reset_index()
                )
                strat_grp["Avg Hold (days)"] = strat_grp["Avg Hold (days)"].round(0).astype(int)

                st.markdown("#### By Strategy")
                st.dataframe(
                    _color_df_pnl(strat_grp, "Total P&L ($)"),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Total P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                        "Avg P&L ($)":   st.column_config.NumberColumn(format="$%+,.0f"),
                    },
                )

                # ── Symbol breakdown ──────────────────────────────────────────
                sym_grp = (
                    df_pnl.groupby("symbol")
                    .agg(
                        Trades=("pnl", "count"),
                        Total_PnL=("pnl", "sum"),
                        Win_Rate=("winner", lambda x: f"{x.mean()*100:.0f}%"),
                        Avg_Hold=("hold_days", "mean"),
                    )
                    .rename(columns={"Total_PnL": "Total P&L ($)",
                                     "Win_Rate":  "Win Rate",
                                     "Avg_Hold":  "Avg Hold (days)"})
                    .sort_values("Total P&L ($)", ascending=False)
                    .reset_index()
                )
                sym_grp["Avg Hold (days)"] = sym_grp["Avg Hold (days)"].round(0).astype(int)

                st.markdown("#### By Symbol")
                st.dataframe(
                    _color_df_pnl(sym_grp, "Total P&L ($)"),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Total P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                    },
                )

                # ── Cumulative P&L chart ──────────────────────────────────────
                st.markdown("#### Cumulative Realized P&L Over Time")
                cum_df = df_pnl.sort_values("close_date")[["close_date", "pnl"]].copy()
                cum_df["cumulative"] = cum_df["pnl"].cumsum()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cum_df["close_date"],
                    y=cum_df["cumulative"],
                    mode="lines+markers",
                    line=dict(color=_GREEN if total_pnl >= 0 else _RED, width=2),
                    marker=dict(size=4),
                    name="Cumulative P&L",
                    hovertemplate="%{x|%b %d %Y}<br>$%{y:,.0f}<extra></extra>",
                ))
                fig.add_hline(y=0, line_dash="dash",
                              line_color=_MUTED, line_width=1)
                fig.update_layout(
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#f8fafc",
                    margin=dict(l=0, r=0, t=10, b=0),
                    yaxis=dict(gridcolor="#e2e8f0", tickprefix="$",
                               tickformat=",.0f"),
                    xaxis=dict(showgrid=False),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── Full matched trade table ──────────────────────────────────
                with st.expander("📄 Full Matched Trade List", expanded=False):
                    cols_show = ["symbol", "strategy", "direction",
                                 "open_date", "close_date", "hold_days",
                                 "qty", "open_price", "close_price", "pnl", "pnl_pct"]
                    disp_full = df_pnl[cols_show].copy()
                    disp_full.columns = ["Symbol", "Strategy", "Dir",
                                         "Open Date", "Close Date", "Hold Days",
                                         "Qty", "Open $", "Close $", "P&L ($)", "P&L %"]
                    disp_full["Open Date"]  = disp_full["Open Date"].dt.strftime("%Y-%m-%d")
                    disp_full["Close Date"] = disp_full["Close Date"].dt.strftime("%Y-%m-%d")
                    st.dataframe(
                        _color_df_pnl(disp_full, "P&L ($)"),
                        use_container_width=True,
                        hide_index=True,
                        height=400,
                        column_config={
                            "Open $":  st.column_config.NumberColumn(format="$%.2f"),
                            "Close $": st.column_config.NumberColumn(format="$%.2f"),
                            "P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                            "P&L %":   st.column_config.NumberColumn(format="%+.1f%%"),
                        },
                    )


# ══════════════════════════════════════════════════════════════════════════════
# 5 · INSIGHTS TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_insights:
    st.markdown("### 🔍 Trade Insights")
    acct_data = acct_data_global
    if acct_data:
        trades = acct_data.get("trades", [])
        if not trades:
            st.info("No trades to analyze.")
        else:
            _comm = st.session_state.get("pnl_comm_correct", True)
            df_pnl_i = compute_realized_pnl(trades, commission_correct=_comm)

            if df_pnl_i.empty:
                st.info("Not enough matched open/close data for insights yet.")
            else:
                # ── Hold-time analysis ────────────────────────────────────────
                st.markdown("#### ⏱️ Hold Time: Winners vs Losers")
                w_hold = df_pnl_i[df_pnl_i["winner"] == True]["hold_days"]
                l_hold = df_pnl_i[df_pnl_i["winner"] == False]["hold_days"]

                ht1, ht2, ht3, ht4 = st.columns(4)
                ht1.metric("Avg hold — Winners",  f"{w_hold.mean():.0f} days" if len(w_hold) else "—")
                ht2.metric("Avg hold — Losers",   f"{l_hold.mean():.0f} days" if len(l_hold) else "—")
                ht3.metric("Longest winner hold", f"{w_hold.max():.0f} days"  if len(w_hold) else "—")
                ht4.metric("Shortest losing hold",f"{l_hold.min():.0f} days"  if len(l_hold) else "—")

                st.divider()

                ic1, ic2 = st.columns(2)

                # ── Top 5 winners ─────────────────────────────────────────────
                with ic1:
                    st.markdown("##### 🏆 Top 5 Realized Gains")
                    top5 = df_pnl_i.nlargest(5, "pnl")[
                        ["symbol", "strategy", "pnl", "pnl_pct", "hold_days"]
                    ].copy()
                    top5.columns = ["Symbol", "Strategy", "P&L ($)", "P&L %", "Days"]
                    st.dataframe(
                        _color_df_pnl(top5, "P&L ($)"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                            "P&L %":   st.column_config.NumberColumn(format="%+.1f%%"),
                        },
                    )

                # ── Top 5 losers ──────────────────────────────────────────────
                with ic2:
                    st.markdown("##### 📉 Top 5 Realized Losses")
                    bot5 = df_pnl_i.nsmallest(5, "pnl")[
                        ["symbol", "strategy", "pnl", "pnl_pct", "hold_days"]
                    ].copy()
                    bot5.columns = ["Symbol", "Strategy", "P&L ($)", "P&L %", "Days"]
                    st.dataframe(
                        _color_df_pnl(bot5, "P&L ($)"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                            "P&L %":   st.column_config.NumberColumn(format="%+.1f%%"),
                        },
                    )

                st.divider()

                # ── Short-hold losers (< 5 days, loss) ────────────────────────
                st.markdown("##### ⚡ Quick Exits That Lost (< 5 days) — Possible Impulse Trades")
                quick_loss = df_pnl_i[(df_pnl_i["hold_days"] < 5) & (df_pnl_i["pnl"] < 0)].copy()
                if quick_loss.empty:
                    st.success("✅ No quick-exit losing trades found.")
                else:
                    ql_disp = quick_loss[["symbol", "strategy", "open_date",
                                          "close_date", "hold_days", "pnl"]].copy()
                    ql_disp.columns = ["Symbol", "Strategy", "Opened",
                                       "Closed", "Days", "P&L ($)"]
                    ql_disp["Opened"] = ql_disp["Opened"].dt.strftime("%Y-%m-%d")
                    ql_disp["Closed"] = ql_disp["Closed"].dt.strftime("%Y-%m-%d")
                    st.dataframe(
                        _color_df_pnl(ql_disp, "P&L ($)"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                        },
                    )
                    st.caption("These trades were closed in under 5 days at a loss. "
                               "Review if they were intentional or reactive exits.")

                # ── Long-hold losers (> 60 days, loss > $500) ────────────────
                st.markdown("##### 🧊 Held Too Long — Loss > $500 After 60+ Days")
                stuck = df_pnl_i[(df_pnl_i["hold_days"] > 60) & (df_pnl_i["pnl"] < -500)].copy()
                if stuck.empty:
                    st.success("✅ No large long-hold losses found.")
                else:
                    st_disp = stuck[["symbol", "strategy", "open_date",
                                     "close_date", "hold_days", "pnl"]].copy()
                    st_disp.columns = ["Symbol", "Strategy", "Opened",
                                       "Closed", "Days", "P&L ($)"]
                    st_disp["Opened"] = st_disp["Opened"].dt.strftime("%Y-%m-%d")
                    st_disp["Closed"] = st_disp["Closed"].dt.strftime("%Y-%m-%d")
                    st.dataframe(
                        _color_df_pnl(st_disp, "P&L ($)"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "P&L ($)": st.column_config.NumberColumn(format="$%+,.0f"),
                        },
                    )
                    st.caption("These held 60+ days and ended in a $500+ loss. "
                               "Consider whether a stop-loss rule would have limited damage.")

                # ── Premium capture for CSPs / CCs ───────────────────────────
                st.markdown("##### 💰 Options Premium Capture Rate (CSP / Covered Call)")
                short_opts = df_pnl_i[df_pnl_i["direction"] == "Short"].copy()
                if short_opts.empty:
                    st.info("No short option (CSP/CC) round-trips found yet.")
                else:
                    short_opts["capture_pct"] = (
                        short_opts["pnl"] / (short_opts["open_price"] * short_opts["qty"] * 100) * 100
                    ).round(1)
                    cap_grp = (
                        short_opts.groupby("symbol")
                        .agg(
                            Contracts=("pnl", "count"),
                            Total_Premium=("open_price",
                                           lambda x: (x * short_opts.loc[x.index, "qty"] * 100).sum()),
                            Total_Captured=("pnl", "sum"),
                            Avg_Capture_Pct=("capture_pct", "mean"),
                        )
                        .sort_values("Total_Captured", ascending=False)
                        .reset_index()
                    )
                    cap_grp.columns = ["Symbol", "Contracts",
                                       "Premium Sold ($)", "Captured ($)", "Avg Capture %"]
                    st.dataframe(
                        cap_grp.style.map(
                            lambda x: (f"color:{_GREEN};font-weight:600"
                                       if isinstance(x, (int, float)) and x > 0
                                       else f"color:{_RED};font-weight:600"
                                       if isinstance(x, (int, float)) and x < 0 else ""),
                            subset=["Captured ($)"],
                        ),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Premium Sold ($)": st.column_config.NumberColumn(format="$%,.0f"),
                            "Captured ($)":     st.column_config.NumberColumn(format="$%+,.0f"),
                            "Avg Capture %":    st.column_config.NumberColumn(format="%.1f%%"),
                        },
                    )
                    st.caption("Capture % = actual P&L as % of premium originally sold. "
                               "100% = expired worthless (full keep). Negative = bought back for more than sold.")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER NOTE
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ This page is for personal tracking only — not financial advice. "
    "Data is stored in your browser session only and is cleared on page refresh. "
    "Coming soon: GSheets persistence for data that survives across sessions. "
    "Fidelity and Robinhood import formats can be added as additional parsers."
)

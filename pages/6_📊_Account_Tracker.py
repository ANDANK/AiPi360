"""Account Tracker — balances, analytics, projections & market alerts."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import base64

st.set_page_config(page_title="AiPi360 · Account Tracker", page_icon="📊", layout="wide")

from backend.auth import require_auth, sign_out
require_auth()

from components.metric_card import section_header, coming_soon
from components.reminder_banner import render_section_reminders
from services.accounts import (
    list_accounts, add_account, deactivate_account,
    save_balances, load_balances, latest_balances,
    list_alerts, add_alert, delete_alert,
    icon as acc_icon, label as acc_label, is_retirement,
    ACCOUNT_TYPES,
)
from backend.gsheet import read_sheet, refresh_cache

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.acct-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:12px;
    padding:14px; transition:border-color 0.15s;
}
.acct-card:hover { border-color: #2563eb; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_cache()
        st.rerun()

section_header("📊", "Account Tracker", "Equities, retirement, home, auto & expenses")

try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "accounts")
except Exception:
    pass

tab_bal, tab_analytics, tab_proj, tab_mgmt, tab_alerts = st.tabs([
    "📥 Balance Input", "📊 Analytics", "🔮 Projections", "⚙️ Manage Accounts", "🔔 Market Alerts"
])

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def _accounts():
    return list_accounts()

@st.cache_data(ttl=300)
def _balances():
    return load_balances()

try:
    accounts_df = _accounts()
except Exception as e:
    st.error(f"Could not load accounts: {e}")
    st.stop()

bal_history = _balances()
latest      = latest_balances(bal_history)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Balance Input
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bal:
    d_col, up_col = st.columns([2, 4])
    with d_col:
        snap_date = st.date_input("📅 Snapshot Date", value=date.today())
    with up_col:
        uploaded = st.file_uploader(
            "📎 Upload statement screenshot — Claude will auto-fill balances",
            type=["png","jpg","jpeg"], label_visibility="collapsed",
        )
        if uploaded and not accounts_df.empty:
            ext = uploaded.name.rsplit(".",1)[-1].lower()
            media_type = "image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            with st.spinner("🔍 Reading balances with Claude AI…"):
                try:
                    from backend.ai_refresh import process_upload
                    import json, re
                    acct_list = "\n".join(
                        f'- id:"{r["account_id"]}" name:"{r["account_name"]}" type:"{acc_label(r["account_type"])}"'
                        for _, r in accounts_df.iterrows()
                    )
                    prompt = (
                        f"Known accounts:\n{acct_list}\n\n"
                        "Extract balances visible in this statement and return JSON: "
                        "{\"account_id\": balance, ...}. Numbers only, no $ or commas."
                    )
                    raw = process_upload(uploaded.read(), media_type, prompt)
                    m = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
                    if m:
                        extracted = {k: float(v) for k, v in json.loads(m.group()).items()}
                        for aid, amt in extracted.items():
                            st.session_state[f"acct_bal_{aid}"] = amt
                        st.success(f"✅ Found {len(extracted)} balance(s) — verify below and save.")
                    else:
                        st.warning("Couldn't match balances — enter manually.")
                except Exception as exc:
                    st.error(f"Extraction failed: {exc}")

    st.markdown("---")

    if accounts_df.empty:
        st.info("No accounts yet. Go to **Manage Accounts** tab to add some.")
    else:
        balance_inputs: dict[str, float] = {}
        ret_accts    = accounts_df[accounts_df["account_type"].apply(is_retirement)]
        nonret_accts = accounts_df[~accounts_df["account_type"].apply(is_retirement)]

        def _render_acct_grid(df_accts):
            pairs = list(df_accts.iterrows())
            for i in range(0, len(pairs), 3):
                cols = st.columns(3)
                for j, (_, row) in enumerate(pairs[i:i+3]):
                    aid  = row["account_id"]
                    last = latest.get(aid, 0)
                    with cols[j]:
                        with st.container(border=True):
                            extracted_flag = st.session_state.get(f"acct_bal_{aid}") is not None
                            badge = " 📷" if extracted_flag else ""
                            st.markdown(f"**{acc_icon(row['account_type'])} {row['account_name']}**{badge}")
                            st.caption(f"{acc_label(row['account_type'])} · {row.get('owner','').title()}")
                            val = st.number_input(
                                "Balance", min_value=0.0, value=0.0, step=500.0,
                                format="%.2f", key=f"acct_bal_{aid}", label_visibility="collapsed",
                            )
                            st.caption(f"Last: ${float(last):,.0f}" if last else "Last: —")
                            balance_inputs[aid] = val

        if not ret_accts.empty:
            st.markdown("##### 🎯 Retirement Accounts")
            _render_acct_grid(ret_accts)
        if not nonret_accts.empty:
            st.markdown("##### 💼 Non-Retirement Accounts")
            _render_acct_grid(nonret_accts)

        st.markdown("---")
        sv_col, _ = st.columns([2, 5])
        with sv_col:
            if st.button("💾 Save All Balances", type="primary", use_container_width=True):
                entries = [
                    {"account_id": aid,
                     "account_name": accounts_df[accounts_df["account_id"]==aid]["account_name"].values[0] if len(accounts_df[accounts_df["account_id"]==aid]) else aid,
                     "balance": bal}
                    for aid, bal in balance_inputs.items() if bal > 0
                ]
                if entries:
                    try:
                        save_balances(entries, snap_date)
                        st.success(f"✅ Saved {len(entries)} balance(s) for {snap_date}.")
                        for aid in balance_inputs:
                            st.session_state.pop(f"acct_bal_{aid}", None)
                        refresh_cache()
                        _accounts.clear()
                        _balances.clear()
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Save failed: {exc}")
                else:
                    st.warning("Enter at least one balance > $0 before saving.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Analytics
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    if bal_history.empty or accounts_df.empty:
        st.info("No balance data yet — use the Balance Input tab to record your first snapshot.")
    else:
        total = sum(v for k, v in latest.items())
        ret_total    = sum(v for k, v in latest.items()
                          if any(accounts_df[accounts_df["account_id"]==k]["account_type"].apply(is_retirement).values))
        nonret_total = total - ret_total

        k1, k2, k3 = st.columns(3)
        k1.metric("💰 Total Net Worth (Accounts)", f"${total:,.0f}")
        k2.metric("🎯 Retirement",     f"${ret_total:,.0f}")
        k3.metric("💼 Non-Retirement", f"${nonret_total:,.0f}")

        st.divider()

        # Balance over time
        st.subheader("📈 Balance Over Time")
        hist_df = bal_history.copy()
        name_map = {r["account_id"]: r["account_name"] for _, r in accounts_df.iterrows()}
        color_pool = ["#2563eb","#10b981","#f59e0b","#8b5cf6","#ec4899","#06b6d4","#f97316"]

        fig = go.Figure()
        for i, (_, acc) in enumerate(accounts_df.iterrows()):
            aid  = acc["account_id"]
            df_a = hist_df[hist_df["account_id"]==aid].sort_values("date")
            if df_a.empty: continue
            fig.add_trace(go.Scatter(
                x=df_a["date"], y=df_a["balance"],
                name=acc["account_name"], mode="lines+markers",
                line=dict(width=1.5, color=color_pool[i % len(color_pool)]),
                hovertemplate=f"{acc['account_name']}<br>%{{x|%b %Y}}: $%{{y:,.0f}}<extra></extra>",
            ))
        combined = hist_df.groupby("date")["balance"].sum().reset_index()
        fig.add_trace(go.Scatter(
            x=combined["date"], y=combined["balance"], name="Combined",
            line=dict(width=3, color="#0f172a"),
            hovertemplate="Combined<br>%{x|%b %Y}: $%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                          height=340, hovermode="x unified",
                          legend=dict(orientation="h", y=-0.25, font_size=11),
                          xaxis=dict(showgrid=False),
                          yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
        st.plotly_chart(fig, use_container_width=True)

        # Allocation pie
        st.subheader("🥧 Current Allocation")
        alloc_rows = [{"Account": name_map.get(k,k), "Balance": v} for k,v in latest.items() if v > 0]
        if alloc_rows:
            fig2 = px.pie(pd.DataFrame(alloc_rows), values="Balance", names="Account",
                          hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=340)
            st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Projections
# ═══════════════════════════════════════════════════════════════════════════════
with tab_proj:
    if bal_history.empty:
        st.info("Record balances first to see projections.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            growth_pct = st.slider("📈 Annual Growth Rate", 3.0, 15.0, 7.0, 0.5, format="%.1f%%")
        with c2:
            target_yr  = st.number_input("🎯 Target Year", min_value=2026, max_value=2050, value=2040)
        with c3:
            target_amt = st.select_slider(
                "🏁 Target Amount",
                options=[500_000,1_000_000,1_500_000,2_000_000,3_000_000,5_000_000],
                value=2_000_000,
                format_func=lambda v: f"${v/1e6:.1f}M",
            )

        # Simple compound growth projection
        cur_year  = datetime.now().year
        total_now = sum(latest.values())
        years     = list(range(cur_year, target_yr + 1))
        projected = [total_now * ((1 + growth_pct/100) ** (y - cur_year)) for y in years]

        proj_at_target = projected[-1] if projected else 0
        gap = target_amt - proj_at_target

        k1, k2, k3 = st.columns(3)
        k1.metric("Current Total", f"${total_now:,.0f}")
        k2.metric(f"Projected {target_yr}", f"${proj_at_target:,.0f}",
                  delta=f"{'+'if proj_at_target>=target_amt else ''}{(proj_at_target-target_amt):,.0f} vs goal")
        k3.metric("Gap to Goal", "✅ On Track" if gap <= 0 else f"${gap:,.0f} short")

        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(
            x=years, y=projected, mode="lines+markers",
            name=f"{growth_pct}% Growth", line=dict(color="#2563eb", width=3),
            hovertemplate="Year %{x}: $%{y:,.0f}<extra></extra>",
            fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
        ))
        fig_p.add_hline(y=target_amt, line_dash="dash", line_color="#dc2626", line_width=2,
                        annotation_text=f"🎯 ${target_amt/1e6:.1f}M goal",
                        annotation_position="right", annotation_font=dict(color="#dc2626"))
        fig_p.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc", height=380,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"),
                            hovermode="x unified", margin=dict(r=100))
        st.plotly_chart(fig_p, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Manage Accounts
# ═══════════════════════════════════════════════════════════════════════════════
with tab_mgmt:
    st.markdown("#### ⚙️ Manage Accounts")
    if not accounts_df.empty:
        st.dataframe(
            accounts_df[["account_id","account_name","account_type","owner","active"]],
            use_container_width=True, hide_index=True,
        )
        st.markdown("**Deactivate an account:**")
        sel = st.selectbox("Select account", accounts_df["account_id"].tolist(),
                           format_func=lambda x: accounts_df[accounts_df["account_id"]==x]["account_name"].values[0])
        if st.button("🔴 Deactivate", type="secondary"):
            deactivate_account(sel)
            st.success("Account deactivated.")
            _accounts.clear()
            st.rerun()
    else:
        st.info("No accounts yet. Add one below.")

    st.markdown("---")
    with st.expander("➕ Add New Account"):
        with st.form("add_account_form"):
            c1, c2, c3 = st.columns(3)
            with c1: aname  = st.text_input("Account Name")
            with c2: atype  = st.selectbox("Type", list(ACCOUNT_TYPES.keys()),
                                            format_func=lambda x: f"{acc_icon(x)} {acc_label(x)}")
            with c3: aowner = st.selectbox("Owner", ["self","spouse","joint"])
            if st.form_submit_button("Add Account", type="primary"):
                if aname:
                    aid = add_account(aname, atype, aowner)
                    st.success(f"✅ Added: {aname} ({aid})")
                    _accounts.clear()
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Market Alerts
# ═══════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown("#### 🔔 Market Alerts")
    st.info("Set alerts for market conditions. Nightly GitHub Actions job checks and notifies you.")

    alerts_df = list_alerts()
    if not alerts_df.empty:
        active_alerts = alerts_df[alerts_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
        if not active_alerts.empty:
            for _, row in active_alerts.iterrows():
                c1, c2, c3 = st.columns([3,2,1])
                with c1:
                    st.markdown(f"**{row['ticker']}** — {row['condition']} {row['threshold']}%")
                with c2:
                    st.caption(f"Notify: {row.get('channels','push')}")
                with c3:
                    if st.button("🗑️", key=f"del_alert_{row['id']}", help="Delete alert"):
                        delete_alert(row["id"])
                        st.rerun()
        else:
            st.info("No active alerts.")
    else:
        st.info("No alerts set yet.")

    st.markdown("---")
    with st.expander("➕ Add Market Alert"):
        st.caption("Examples: SPY falls 1% in a day · QQQ falls 1% in a day · SPY falls 7% in a month")
        with st.form("add_alert_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: ticker    = st.text_input("Ticker (e.g. SPY, QQQ)")
            with c2: condition = st.selectbox("Condition", ["falls more than","rises more than","falls more than (monthly)"])
            with c3: threshold = st.number_input("Threshold (%)", min_value=0.1, max_value=50.0, value=1.0, step=0.5)
            with c4: channels  = st.selectbox("Notify via", ["push","email","push,email"])
            if st.form_submit_button("Add Alert", type="primary"):
                if ticker:
                    add_alert(ticker.upper(), condition, threshold, channels)
                    st.success(f"✅ Alert added for {ticker.upper()}")
                    st.rerun()

"""Insurance — policies, premiums, renewals & smart shopping."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="AiPi360 · Insurance", page_icon="🛡️", layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css
require_auth()
check_maintenance()
check_page_access("insurance")
inject_3d_tab_css()

from components.metric_card import section_header, coming_soon
from components.reminder_banner import render_section_reminders
from services.insurance import (
    list_policies, add_policy, update_policy, delete_policy,
    annual_total, due_soon, POLICY_TYPES, FREQUENCIES, icon as pol_icon,
)
from backend.gsheet import read_sheet

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

section_header("🛡️", "Insurance", "Manage all policies, premiums, and renewal reminders")

try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "insurance")
except Exception:
    pass

tab1, tab2, tab3 = st.tabs(["📋 All Policies", "📊 Analytics", "🛒 Shop Smart"])

# ── All Policies ──────────────────────────────────────────────────────────────
with tab1:
    df = list_policies()
    annual = annual_total(df)

    k1, k2, k3 = st.columns(3)
    k1.metric("🛡️ Active Policies", len(df) if not df.empty else 0)
    k2.metric("💰 Annual Premium Total", f"${annual:,.0f}")
    k3.metric("📅 Due in 30 days", len(due_soon(30, df)) if not df.empty else 0)

    if not df.empty:
        display = df.copy()
        display["icon"] = display["type"].apply(pol_icon)
        display["label"] = display["icon"] + " " + display["type"]
        st.dataframe(
            display[["label","provider","policy_number","premium","frequency","due_date","notes"]],
            use_container_width=True, hide_index=True,
            column_config={
                "premium": st.column_config.NumberColumn("Premium ($)", format="$%.2f"),
            }
        )

        st.markdown("##### ✏️ Manage a Policy")
        sel_id = st.selectbox("Select policy to edit/delete",
                              df["id"].tolist(),
                              format_func=lambda x: df[df["id"]==x]["provider"].values[0] + " – " + df[df["id"]==x]["type"].values[0])
        col_ed, col_del = st.columns(2)
        with col_del:
            if st.button("🗑️ Remove Policy", type="secondary"):
                delete_policy(sel_id)
                st.success("Policy removed.")
                st.rerun()
    else:
        st.info("No policies yet. Add your first below.")

    st.markdown("---")
    with st.expander("➕ Add New Policy"):
        with st.form("add_policy_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                ptype    = st.selectbox("Policy Type", POLICY_TYPES)
                provider = st.text_input("Provider / Company")
            with c2:
                policy_no = st.text_input("Policy Number (optional)")
                premium   = st.number_input("Premium ($)", min_value=0.0, step=10.0)
            with c3:
                freq     = st.selectbox("Frequency", FREQUENCIES)
                due      = st.date_input("Next Due Date", value=date.today())
            notes = st.text_input("Notes (optional)")
            if st.form_submit_button("Add Policy", type="primary"):
                if provider:
                    add_policy(ptype, provider, policy_no, premium, freq, due, notes)
                    st.success(f"✅ Added {ptype} policy from {provider}.")
                    st.rerun()

# ── Analytics ─────────────────────────────────────────────────────────────────
with tab2:
    df = list_policies()
    if df.empty:
        st.info("Add policies to see analytics.")
    else:
        df["annual"] = df.apply(lambda r: float(r.get("premium",0) or 0) * {
            "Monthly":12,"Quarterly":4,"Semi-Annual":2,"Annual":1
        }.get(r.get("frequency","Annual"),1), axis=1)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, values="annual", names="type",
                         title="Annual Premium by Policy Type",
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(df.sort_values("annual", ascending=True),
                          x="annual", y="provider", orientation="h",
                          title="Annual Cost by Provider",
                          labels={"annual":"Annual ($)","provider":"Provider"},
                          color_discrete_sequence=["#2563eb"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### 📅 Upcoming Renewals")
        upcoming = due_soon(60, df)
        if upcoming.empty:
            st.success("No renewals in the next 60 days.")
        else:
            st.dataframe(upcoming[["type","provider","premium","frequency","due_date"]],
                         use_container_width=True, hide_index=True)

# ── Shop Smart ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🛒 Smart Insurance Shopping")
    st.markdown("""
<div style="background:#eff6ff;border-radius:12px;padding:20px;border:1px solid #bfdbfe;margin-bottom:16px;">
<b>💡 Shopping tips:</b>
<ul style="margin-top:8px;padding-left:20px;">
<li>Bundle auto + home for 10-25% discount</li>
<li>Review all policies at each renewal — market changes year-over-year</li>
<li>Umbrella policy ($1M) typically costs $150-300/year — high value</li>
<li>Review medical plan during open enrollment (typically Oct-Nov)</li>
<li>Life insurance: lock in rates when young and healthy</li>
</ul>
</div>""", unsafe_allow_html=True)
    coming_soon("AI-powered comparison tool — compare current premiums to market rates")

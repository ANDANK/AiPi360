"""Calendar & Reminders — consolidated across all sections."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="AiPi360 · Calendar", page_icon="📅", layout="wide")

from backend.auth import require_auth, sign_out
require_auth()

from components.metric_card import section_header
from services.reminders import get_all, add, mark_done, delete
from backend.gsheet import read_sheet

SECTIONS   = ["All", "kids", "fisd", "school", "insurance", "cc", "travel", "accounts", "tamil", "general"]
FREQ_OPTS  = ["once", "daily", "weekly", "monthly", "yearly"]
CHAN_OPTS  = ["push", "email", "push,email"]
REMIND_DAYS = [0, 1, 3, 7, 14, 30]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.rem-row {
    display:flex; align-items:center; gap:12px;
    padding:10px 14px; background:#fff;
    border:1px solid #e2e8f0; border-radius:10px; margin-bottom:6px;
}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.markdown("---")
    st.markdown("**Filter by Section**")
    sel_section = st.selectbox("Section", SECTIONS, label_visibility="collapsed")

section_header("📅", "Calendar & Reminders", "All reminders, events & important dates in one place")

tab1, tab2, tab3 = st.tabs(["📋 All Reminders", "➕ Add Reminder", "📆 7-Day View"])

# ── All Reminders ─────────────────────────────────────────────────────────────
with tab1:
    try:
        df = read_sheet("reminders")
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.info("No reminders yet. Add your first in the 'Add Reminder' tab.")
    else:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date

        if sel_section != "All":
            df = df[df["section"].str.lower() == sel_section.lower()]

        # Status filter
        show_done = st.checkbox("Show completed reminders", value=False)
        if not show_done:
            df = df[df["status"].str.upper() != "DONE"]

        df = df.sort_values("due_date", na_position="last")

        if df.empty:
            st.success("✅ All clear — no active reminders in this section.")
        else:
            today = date.today()
            for _, r in df.iterrows():
                due = r.get("due_date")
                if due:
                    delta = (due - today).days
                    if delta < 0:
                        color, badge = "#dc2626", f"🚨 {abs(delta)}d overdue"
                    elif delta == 0:
                        color, badge = "#ea580c", "🔔 Today"
                    elif delta <= 3:
                        color, badge = "#ca8a04", f"⏰ {delta}d"
                    else:
                        color, badge = "#16a34a", f"📅 {delta}d"
                else:
                    color, badge = "#94a3b8", "No date"

                c1, c2, c3, c4, c5 = st.columns([0.8, 2.5, 1.5, 1, 1])
                with c1:
                    st.markdown(f"<span style='color:{color};font-weight:600;font-size:12px;'>{badge}</span>",
                                unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    if r.get("message"):
                        st.caption(r["message"])
                with c3:
                    st.caption(f"{r.get('section','').upper()} · {r.get('frequency','once')}")
                with c4:
                    if st.button("✅ Done", key=f"done_{r['id']}"):
                        mark_done(r["id"])
                        st.rerun()
                with c5:
                    if st.button("🗑️", key=f"del_{r['id']}", help="Delete"):
                        delete(r["id"])
                        st.rerun()

# ── Add Reminder ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### ➕ Add New Reminder")
    with st.form("add_reminder_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_section  = st.selectbox("Section", SECTIONS[1:])
            r_title    = st.text_input("Title *")
            r_message  = st.text_area("Details / Message", height=80)
        with c2:
            r_due      = st.date_input("Due Date", value=date.today())
            r_remind   = st.selectbox("Remind me (days before)", REMIND_DAYS, index=1)
            r_freq     = st.selectbox("Frequency", FREQ_OPTS)
            r_channels = st.selectbox("Notify via", CHAN_OPTS)

        submitted = st.form_submit_button("➕ Add Reminder", type="primary")
        if submitted:
            if r_title:
                add(r_section, r_title, r_message, r_due, r_remind, r_freq, r_channels)
                st.success(f"✅ Reminder added: {r_title}")
                st.rerun()
            else:
                st.error("Title is required.")

    st.markdown("---")
    st.markdown("#### 🔔 Notification Settings")
    with st.expander("Test notifications"):
        if st.button("📧 Send test notification"):
            try:
                from backend.notifications import test_notifications
                result = test_notifications()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

# ── 7-Day View ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 📆 Next 7 Days")
    try:
        all_df = read_sheet("reminders")
        if all_df.empty:
            st.info("No reminders to show.")
        else:
            all_df["due_date"] = pd.to_datetime(all_df["due_date"], errors="coerce").dt.date
            today   = date.today()
            cutoff  = today + timedelta(days=7)
            week_df = all_df[
                (all_df["status"].str.upper() != "DONE") &
                (all_df["due_date"].notna()) &
                (all_df["due_date"] >= today) &
                (all_df["due_date"] <= cutoff)
            ].sort_values("due_date")

            if week_df.empty:
                st.success("✅ Nothing due in the next 7 days!")
            else:
                current_day = None
                for _, r in week_df.iterrows():
                    if r["due_date"] != current_day:
                        current_day = r["due_date"]
                        delta = (current_day - today).days
                        day_label = "Today" if delta == 0 else ("Tomorrow" if delta == 1
                                    else current_day.strftime("%A, %b %d"))
                        st.markdown(f"**{day_label}**")
                    st.markdown(
                        f"""<div style="margin-left:16px;padding:8px 12px;
                            background:#fff;border:1px solid #e2e8f0;border-radius:8px;
                            margin-bottom:4px;display:flex;gap:12px;align-items:center;">
                          <span style="font-size:12px;background:#dbeafe;color:#1d4ed8;
                            border-radius:10px;padding:2px 8px;">{r.get('section','').upper()}</span>
                          <span style="font-size:13px;font-weight:600;">{r['title']}</span>
                          <span style="font-size:12px;color:#64748b;margin-left:auto;">{r.get('message','')}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.error(f"Could not load reminders: {e}")

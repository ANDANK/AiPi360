"""AiPi360 — Home Dashboard."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import date, timedelta
import pandas as pd

# Read auth state BEFORE set_page_config so we can collapse sidebar on login screen
_authenticated = st.session_state.get("authenticated", False)

st.set_page_config(
    page_title="AiPi360 · Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed",
)

from backend.auth import require_auth, sign_out, get_role, render_role_badge
from backend.page_manager import check_maintenance, is_page_visible
require_auth()
check_maintenance()

# Assign role immediately after auth so it's available everywhere below
_role = get_role()

from components.reminder_banner import render_reminder_banner
from components.metric_card import section_header
from components.styles import inject_global_nav_css
inject_global_nav_css()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Sidebar branding */
[data-testid="stSidebarNav"]::before {
    content: "🏠 AiPi360";
    display: block;
    font-family: 'Inter', sans-serif;
    font-size: 18px; font-weight: 800; color: #0f172a;
    padding: 20px 16px 8px 16px; letter-spacing: -0.03em;
}


/* Nav card hover */
.nav-section:hover { box-shadow: 0 4px 16px rgba(37,99,235,0.12) !important; }

/* Metric chip */
.kpi-chip {
    display:inline-flex; align-items:center; gap:6px;
    background:#eff6ff; border-radius:20px;
    padding:6px 14px; font-size:13px; font-weight:600; color:#1d4ed8;
}

/* Welcome banner */
.welcome-bar {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 24px;
    color: #fff;
}
.welcome-bar h1 {
    font-size: 26px; font-weight: 800; letter-spacing: -0.04em;
    margin: 0 0 4px 0;
}
.welcome-bar p { font-size: 14px; opacity: 0.8; margin: 0; }

/* Nav cards */
.nav-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 20px; transition: all 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.nav-card:hover { border-color: #2563eb; box-shadow: 0 4px 16px rgba(37,99,235,0.1); }
.nav-card .nav-icon { font-size: 30px; margin-bottom: 8px; }
.nav-card .nav-title { font-size: 15px; font-weight: 700; color: #0f172a; }
.nav-card .nav-desc  { font-size: 12px; color: #64748b; margin-top: 4px; }
.nav-card .nav-badge {
    display: inline-block; background: #dc2626; color: #fff;
    border-radius: 10px; padding: 1px 7px; font-size: 11px;
    font-weight: 600; margin-left: 6px; vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_role_badge()
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        sign_out()
    st.markdown("---")
    st.caption(f"📅 {date.today().strftime('%A, %B %d, %Y')}")

# ── Welcome Banner ────────────────────────────────────────────────────────────
today = date.today()
hour  = __import__("datetime").datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

st.markdown(
    f"""<div class="welcome-bar">
      <h1>🏠 {greeting}, welcome to AiPi360</h1>
      <p>Your family command center · {today.strftime("%A, %B %d, %Y")}</p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Role-split: users get a clean static home; admin gets full dashboard ──────
if _role != "admin":
    # ── User: clean nav-only home page ────────────────────────────────────────
    st.markdown("#### 🗂️ Your Sections")
    _ALL_NAV_USER = [
        ("🧒", "Kids",            "pages/1_🧒_Kids.py",            "kids",         "School, activities & planning"),
        ("🛡️", "Insurance",       "pages/2_🛡️_Insurance.py",       "insurance",    "Policies, premiums & renewals"),
        ("💳", "CC & Points",     "pages/3_💳_CC_Points.py",       "cc_points",    "Maximize rewards & offers"),
        ("✈️", "Travel",          "pages/4_✈️_Travel.py",          "travel",       "Best deals on flights & hotels"),
        ("📅", "Calendar",        "pages/5_📅_Calendar.py",        "calendar",     "Events, reminders & school"),
        ("📊", "Account Tracker", "pages/6_📊_Account_Tracker.py", "accounts",     "Balances & expenses"),
        ("💼", "Portfolio",       "pages/8_💼_Portfolio.py",       "portfolio",    "Investments & trading"),
        ("🗺️", "Destinations",    "pages/9_🗺️_Destinations.py",   "destinations", "Family trip planning"),
    ]
    USER_NAV = [
        (icon, title, page, desc)
        for icon, title, page, pkey, desc in _ALL_NAV_USER
        if is_page_visible(pkey)
    ]
    cols_per_row = 3
    rows = [USER_NAV[i:i+cols_per_row] for i in range(0, len(USER_NAV), cols_per_row)]
    for row_items in rows:
        row_cols = st.columns(cols_per_row)
        for col, (icon, title, page, desc) in zip(row_cols, row_items):
            with col:
                st.markdown(
                    f"""<div class="nav-card">
                      <div class="nav-icon">{icon}</div>
                      <div class="nav-title">{title}</div>
                      <div class="nav-desc">{desc}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                st.page_link(page, label=f"Open {title} →", use_container_width=True)

    st.markdown("---")
    # Reminders only
    try:
        from backend.gsheet import read_sheet as _rs2
        rem_df2 = _rs2("reminders")
        if not rem_df2.empty:
            render_reminder_banner(rem_df2)
    except Exception:
        pass

    st.markdown(
        "<div style='text-align:center;font-size:12px;color:#94a3b8;padding:8px 0;'>"
        "AiPi360 · Family Command Center · Powered by Streamlit + Claude AI"
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── Admin: full dashboard below ───────────────────────────────────────────────
try:
    from services.reminders import get_active
    from backend.gsheet import read_sheet
    reminders_df = read_sheet("reminders")
    if not reminders_df.empty:
        render_reminder_banner(reminders_df)
except Exception:
    pass

# ── Quick Stats Row ───────────────────────────────────────────────────────────
st.markdown("#### 📊 Quick Snapshot")
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    from backend.gsheet import read_sheet as _rs
    try:
        acc_df = _rs("accounts")
        n_accounts = len(acc_df[acc_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]) if not acc_df.empty else 0
    except Exception:
        n_accounts = 0
    st.metric("💼 Accounts", n_accounts or "—", help="Active accounts tracked")

with k2:
    try:
        ins_df = _rs("insurance_policies")
        n_ins = len(ins_df[ins_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]) if not ins_df.empty else 0
    except Exception:
        n_ins = 0
    st.metric("🛡️ Policies", n_ins or "—", help="Active insurance policies")

with k3:
    try:
        cc_df = _rs("cc_cards")
        n_cc = len(cc_df[cc_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]) if not cc_df.empty else 0
    except Exception:
        n_cc = 0
    st.metric("💳 Cards", n_cc or "—", help="Active credit cards")

with k4:
    try:
        cl_df = _rs("classes")
        n_cl = len(cl_df[cl_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]) if not cl_df.empty else 0
    except Exception:
        n_cl = 0
    st.metric("📚 Classes", n_cl or "—", help="Active classes & activities")

with k5:
    try:
        rem_df = _rs("reminders")
        n_rem = len(rem_df[rem_df["status"].str.upper() != "DONE"]) if not rem_df.empty else 0
    except Exception:
        n_rem = 0
    st.metric("🔔 Reminders", n_rem or "—", help="Active reminders")

st.markdown("---")

# ── Navigation Cards (admin) ───────────────────────────────────────────────────
st.markdown("#### 🗂️ Sections")

_ALL_NAV = [
    ("🧒", "Kids",            "pages/1_🧒_Kids.py",            "kids",      "School, activities & planning for son and daughter"),
    ("🛡️", "Insurance",       "pages/2_🛡️_Insurance.py",       "insurance", "Policies, premiums, renewals & smart shopping"),
    ("💳", "CC & Points",     "pages/3_💳_CC_Points.py",       "cc_points", "Maximize rewards, lounge access & offers"),
    ("✈️", "Travel",          "pages/4_✈️_Travel.py",          "travel",    "Best deals on flights, hotels & points travel"),
    ("📅", "Calendar",        "pages/5_📅_Calendar.py",        "calendar",  "All reminders, events & school calendars"),
    ("📊", "Account Tracker", "pages/6_📊_Account_Tracker.py", "accounts",  "Equities, home, auto & expenses dashboard"),
]
NAV = [
    (icon, title, page, desc)
    for icon, title, page, pkey, desc in _ALL_NAV
    if is_page_visible(pkey)
]
if _role == "admin":
    NAV.append(("🔒", "Admin Panel", "pages/7_🔒_Admin.py", "Site management, page controls & maintenance"))

n_cols = min(len(NAV), 3)
rows_nav = [NAV[i:i+n_cols] for i in range(0, len(NAV), n_cols)]
for row_items in rows_nav:
    row_cols = st.columns(n_cols)
    for col, (icon, title, page, desc) in zip(row_cols, row_items):
        with col:
            st.markdown(
                f"""<div class="nav-card">
                  <div class="nav-icon">{icon}</div>
                  <div class="nav-title">{title}</div>
                  <div class="nav-desc">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.page_link(page, label=f"Open {title} →", use_container_width=True)

st.markdown("---")

# ── Upcoming Events (next 7 days from reminders) ──────────────────────────────
st.markdown("#### 📆 Upcoming — Next 7 Days")
try:
    rem_df = read_sheet("reminders")
    if rem_df.empty:
        st.info("No reminders set yet. Add them in the Calendar section or within each module.")
    else:
        rem_df["due_date"] = pd.to_datetime(rem_df["due_date"], errors="coerce").dt.date
        cutoff = today + timedelta(days=7)
        upcoming = rem_df[
            (rem_df["status"].str.upper() != "DONE") &
            (rem_df["due_date"].notna()) &
            (rem_df["due_date"] >= today) &
            (rem_df["due_date"] <= cutoff)
        ].sort_values("due_date")

        if upcoming.empty:
            st.success("✅ All clear — no upcoming reminders in the next 7 days.")
        else:
            for _, r in upcoming.iterrows():
                delta = (r["due_date"] - today).days
                when  = "Today" if delta == 0 else (f"Tomorrow" if delta == 1 else f"In {delta} days ({r['due_date'].strftime('%a %b %d')})")
                color = "#dc2626" if delta == 0 else ("#ea580c" if delta <= 2 else "#2563eb")
                st.markdown(
                    f"""<div style="display:flex;align-items:center;gap:12px;
                        padding:10px 14px;background:#fff;border:1px solid #e2e8f0;
                        border-radius:10px;margin-bottom:6px;">
                      <div style="min-width:90px;font-size:12px;font-weight:600;color:{color};">{when}</div>
                      <div style="font-size:13px;font-weight:600;color:#0f172a;">{r['title']}</div>
                      <div style="font-size:12px;color:#64748b;margin-left:auto;">
                        {r.get('section','').upper()}
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
except Exception:
    st.info("Connect Google Sheets to see upcoming events.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:12px;color:#94a3b8;padding:8px 0;'>"
    "AiPi360 · Family Command Center · Powered by Streamlit + Claude AI"
    "</div>",
    unsafe_allow_html=True,
)

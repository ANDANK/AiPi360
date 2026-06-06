"""AiPi360 Admin Panel — Page Management · Maintenance Mode · Site Help."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="AiPi360 · Admin", page_icon="🔒", layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed")

from backend.auth import require_admin, sign_out, render_role_badge
from components.styles import inject_3d_tab_css
require_admin()   # redirects non-admin to home
inject_3d_tab_css()

from backend.page_manager import (
    PAGES, PAGE_FEATURES,
    load_settings, save_settings, invalidate_cache,
    is_maintenance_mode, get_maintenance_message,
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; font-size: 14px !important;
    border-radius: 10px 10px 0 0 !important;
    border: 1px solid #e2e8f0 !important; border-bottom: none !important;
    background: #f8fafc !important; padding: 10px 22px !important;
    margin-right: 4px !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(124,58,237,0.10) !important;
    border-color: rgba(124,58,237,0.45) !important;
    color: #7c3aed !important; font-weight: 700 !important;
}
.admin-section {
    font-size:13px; font-weight:700; color:#7c3aed;
    background:rgba(124,58,237,0.07); border-left:3px solid #7c3aed;
    border-radius:0 6px 6px 0; padding:5px 14px; margin:12px 0 8px 0;
}
.page-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:12px;
    padding:16px 20px; margin-bottom:10px;
}
.page-card-disabled { background:#f8fafc; border-color:#f1f5f9; }
.help-section-title {
    font-size:16px; font-weight:800; color:#0f172a; margin:0 0 4px 0;
    letter-spacing:-0.02em;
}
.help-pill {
    display:inline-block; background:#f1f5f9; border-radius:6px;
    padding:2px 10px; font-size:11px; font-weight:600; color:#475569;
    margin:2px 3px 2px 0;
}
.help-pill-green {
    background:rgba(16,185,129,0.1); color:#059669;
}
.help-pill-blue {
    background:rgba(37,99,235,0.1); color:#2563eb;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_role_badge()
    st.markdown("---")
    if st.button("🔄 Refresh Settings", use_container_width=True):
        invalidate_cache()
        st.rerun()
    if st.button("🚪 Sign Out", use_container_width=True):
        sign_out()
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

# ── Header ────────────────────────────────────────────────────────────────────
maint_on = is_maintenance_mode()
maint_badge = (
    '<span style="font-size:12px;background:#fef3c7;color:#92400e;border-radius:6px;'
    'padding:2px 10px;margin-left:10px;font-weight:600">🚧 Maintenance ON</span>'
    if maint_on else ""
)
st.markdown(
    f'<div style="font-size:26px;font-weight:800;color:#0f172a;letter-spacing:-0.03em">'
    f'🔒 Admin Panel{maint_badge}</div>'
    f'<div style="font-size:12px;color:#94a3b8;margin-top:2px;">'
    f'Page & Feature Management · Maintenance · Site Help · Admin only</div>',
    unsafe_allow_html=True,
)
st.divider()

settings = load_settings()

tab_pages, tab_maint, tab_help = st.tabs([
    "🔧 Page & Feature Management",
    "🚧 Maintenance Mode",
    "📖 Site Navigation & Help",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Page & Feature Management
# ═══════════════════════════════════════════════════════════════════════════════
with tab_pages:
    st.markdown("#### 🔧 Page & Feature Management")
    st.caption(
        "Control which pages and features are visible to **User** role. "
        "Kid role always shows only the Kids page — this is hardcoded and cannot be changed here. "
        "Admin always sees everything."
    )

    st.markdown('<div class="admin-section">👤 User Role — Page Visibility</div>', unsafe_allow_html=True)

    new_settings = dict(settings)

    for page in PAGES:
        pk    = page["key"]
        label = page["label"]
        is_kid_req = page.get("kid_required", False)
        cur_val = settings.get(f"page:{pk}:user", "true").lower() not in ("false", "0", "no")

        features = PAGE_FEATURES.get(pk, [])

        # Page toggle row
        p_col, f_col = st.columns([4, 1])
        with p_col:
            with st.expander(
                f"{'✅' if cur_val else '⛔'} **{label}**"
                + (" · *(Kid-required)*" if is_kid_req else ""),
                expanded=False,
            ):
                new_val = st.toggle(
                    f"Enable {label} for User role",
                    value=cur_val,
                    key=f"pg_{pk}",
                )
                new_settings[f"page:{pk}:user"] = "true" if new_val else "false"

                if features:
                    st.markdown(
                        '<div style="font-size:12px;font-weight:600;color:#64748b;'
                        'margin:12px 0 6px 0;border-top:1px solid #f1f5f9;padding-top:10px">'
                        'Sub-Features (User role):</div>',
                        unsafe_allow_html=True,
                    )
                    for fk, flabel in features:
                        fcur = settings.get(f"feature:{pk}:{fk}:user", "true").lower() not in ("false", "0", "no")
                        fval = st.toggle(flabel, value=fcur, key=f"feat_{pk}_{fk}")
                        new_settings[f"feature:{pk}:{fk}:user"] = "true" if fval else "false"

    st.markdown('<div class="admin-section">🧒 Kid Role (hardcoded)</div>', unsafe_allow_html=True)
    st.info(
        "**Kid role always shows only the Kids page.** "
        "All other pages are blocked by the system — no configuration needed. "
        "When KID_PASSWORD is entered, the sidebar automatically hides all pages except Kids."
    )

    st.markdown("---")
    sc1, sc2 = st.columns([2, 5])
    with sc1:
        if st.button("💾 Save Page Settings", type="primary", use_container_width=True):
            # Preserve maintenance settings from current
            new_settings["maintenance:enabled"] = settings.get("maintenance:enabled", "false")
            new_settings["maintenance:message"]  = settings.get("maintenance:message", "")
            save_settings(new_settings)
            st.success("✅ Page settings saved.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Maintenance Mode
# ═══════════════════════════════════════════════════════════════════════════════
with tab_maint:
    st.markdown("#### 🚧 Maintenance Mode")
    st.caption("When enabled, User and Kid roles see a maintenance page instead of site content. Admin is always exempt.")

    cur_maint  = settings.get("maintenance:enabled", "false").lower() in ("true", "1", "yes")
    cur_msg    = settings.get("maintenance:message", get_maintenance_message())

    mc1, mc2 = st.columns([1, 2])
    with mc1:
        maint_status_color = "#dc2626" if cur_maint else "#059669"
        maint_status_text  = "🟥 Currently ON" if cur_maint else "🟩 Currently OFF"
        st.markdown(
            f'<div style="background:{"#fef2f2" if cur_maint else "#f0fdf4"};'
            f'border:2px solid {"#fca5a5" if cur_maint else "#86efac"};'
            f'border-radius:12px;padding:20px;text-align:center;">'
            f'<div style="font-size:36px">{"🚧" if cur_maint else "✅"}</div>'
            f'<div style="font-size:14px;font-weight:700;color:{maint_status_color};margin-top:8px">'
            f'{maint_status_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with mc2:
        with st.form("maint_form"):
            new_maint = st.toggle("Enable Maintenance Mode", value=cur_maint, key="maint_toggle")
            new_msg   = st.text_area(
                "Maintenance Message (shown to users)",
                value=cur_msg,
                height=100,
                key="maint_msg",
                help="Supports plain text. Shown to User and Kid roles when maintenance is on.",
            )
            if st.form_submit_button("💾 Save Maintenance Settings", type="primary"):
                updated = dict(settings)
                updated["maintenance:enabled"] = "true" if new_maint else "false"
                updated["maintenance:message"]  = new_msg.strip() or get_maintenance_message()
                save_settings(updated)
                st.success(f"✅ Maintenance mode {'enabled' if new_maint else 'disabled'}.")
                st.rerun()

    # Preview
    st.markdown("---")
    st.markdown("**Preview — What users see when maintenance is ON:**")
    preview_msg = cur_msg or get_maintenance_message()
    st.markdown(
        f'<div style="max-width:480px;margin:0 auto;text-align:center;'
        f'background:#fef3c7;border:2px solid #f59e0b;border-radius:16px;padding:40px;">'
        f'<div style="font-size:44px;margin-bottom:12px">🚧</div>'
        f'<div style="font-size:20px;font-weight:800;color:#92400e;margin-bottom:10px">'
        f'Site Under Maintenance</div>'
        f'<div style="font-size:14px;color:#78350f;line-height:1.6">{preview_msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Site Navigation & Help
# ═══════════════════════════════════════════════════════════════════════════════
with tab_help:
    st.markdown("#### 📖 Site Navigation & Help")
    st.caption(
        "Reference guide for all pages and features. "
        "Update this section when new functionality is added. "
        "Admin-only — not shown to User or Kid roles."
    )

    # ── Document format helper ─────────────────────────────────────────────────
    def _page_header(icon: str, title: str, route: str, roles: list[str], status: str = "Live"):
        status_color = {"Live": "#059669", "Beta": "#d97706", "Planned": "#64748b"}.get(status, "#64748b")
        roles_html = "".join(
            f'<span class="help-pill help-pill-{"green" if r == "All" else "blue"}">{r}</span>'
            for r in roles
        )
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
            f'<span style="font-size:28px">{icon}</span>'
            f'<div>'
            f'<div class="help-section-title">{title}</div>'
            f'<code style="font-size:11px;color:#94a3b8">{route}</code>'
            f'&nbsp; {roles_html}'
            f'&nbsp; <span style="font-size:11px;font-weight:600;color:{status_color}">'
            f'● {status}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    def _feature_row(label: str, desc: str, status: str = "Live"):
        color = {"Live": "#059669", "Beta": "#d97706", "Planned": "#64748b"}.get(status, "#64748b")
        st.markdown(
            f'<div style="padding:6px 12px;background:#f8fafc;border-radius:8px;'
            f'margin-bottom:4px;display:flex;gap:10px;align-items:flex-start">'
            f'<span style="font-size:10px;font-weight:700;color:{color};min-width:42px;'
            f'margin-top:2px">{status}</span>'
            f'<div><span style="font-size:13px;font-weight:600">{label}</span>'
            f'<span style="font-size:12px;color:#64748b;margin-left:8px">{desc}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HOME
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("🏠  Home Dashboard", expanded=False):
        _page_header("🏠", "Home Dashboard", "app.py", ["All roles"])
        st.markdown("**Purpose:** Family command center — welcome banner, quick stats, reminders, nav cards.")
        st.markdown("**Main Features:**")
        _feature_row("Quick Stats",      "Live counts: Accounts, Policies, Cards, Classes, Reminders")
        _feature_row("Reminder Banner",  "Shows due-soon reminders across all sections")
        _feature_row("Nav Cards",        "Visual shortcuts to all 6 sections — filtered by role")
        _feature_row("Upcoming 7 Days",  "Timeline of reminders due within the next week")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Role-specific welcome message (admin vs user vs kid)")
        st.markdown("- [ ] Add weather widget placeholder")

    # ─────────────────────────────────────────────────────────────────────────
    # KIDS
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("🧒  Kids", expanded=False):
        _page_header("🧒", "Kids", "pages/1_🧒_Kids.py", ["All roles"], "Live")
        st.markdown("**Purpose:** School & activity hub for kids. Only page visible to Kid role.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("📚 Syllabus & Plan",
                     "School curriculum by subject, TEKS-by-month, tests & assessments. FISD + Tamil school.")
        _feature_row("🏆 Math Rocks",
                     "Math competitions (UIL, MATHCOUNTS, AMC) near McKinney TX. Resources + mini tests.")
        _feature_row("📝 STAAR Practice",
                     "20-question mini tests by strand. Tracks weak areas. Recommends focus topics.")
        _feature_row("📅 School Calendar",
                     "FISD & Tamil school calendars. Parent-teacher conferences. Holidays.")
        _feature_row("🔔 Reminders",      "Add/manage reminders for school events.", "Live")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Math Rocks question bank expansion (target: 100+ per category)")
        st.markdown("- [ ] STAAR 2027 date confirmation (currently estimated late April)")
        st.markdown("- [ ] Tamil school Unit 4–6 detailed lesson plan")

    # ─────────────────────────────────────────────────────────────────────────
    # INSURANCE
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("🛡️  Insurance", expanded=False):
        _page_header("🛡️", "Insurance", "pages/2_🛡️_Insurance.py", ["Admin", "User"], "Live")
        st.markdown("**Purpose:** Track all insurance policies — renewals, premiums, coverage.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("📋 Policy List",       "All active policies with renewal dates and premium amounts")
        _feature_row("🔔 Renewal Alerts",    "Upcoming renewals within 30/60/90 days")
        _feature_row("📊 Policy Comparison", "Side-by-side comparison of plans", "Beta")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Auto-reminder for renewals via ntfy push")
        st.markdown("- [ ] Add dental/vision separate tracking")

    # ─────────────────────────────────────────────────────────────────────────
    # CC & POINTS
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("💳  CC & Points", expanded=False):
        _page_header("💳", "CC & Points", "pages/3_💳_CC_Points.py", ["Admin", "User"], "Live")
        st.markdown("**Purpose:** Maximize credit card rewards — points, offers, lounge access.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("💳 Card List",        "All active cards with limits and reward categories")
        _feature_row("🎁 Offers Tracker",   "Current card offers and their expiry dates")
        _feature_row("💰 Rewards Summary",  "Points/miles balances and estimated values")
        _feature_row("🛋️ Lounge Access",    "Which cards provide lounge access + visit counts", "Beta")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Add Chase UR / Amex MR point value estimator")
        st.markdown("- [ ] Travel portal comparison (Chase vs Amex vs Citi)")

    # ─────────────────────────────────────────────────────────────────────────
    # TRAVEL
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("✈️  Travel", expanded=False):
        _page_header("✈️", "Travel", "pages/4_✈️_Travel.py", ["Admin", "User"], "Live")
        st.markdown("**Purpose:** Plan and track trips — flights, hotels, points redemption.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("✈️ My Trips",         "Upcoming and past trips with cost breakdown")
        _feature_row("🔍 Deal Finder",      "Best-value redemptions for target destinations", "Beta")
        _feature_row("🏨 Hotels",           "Hotel bookings and loyalty program tracking")
        _feature_row("💎 Points Redemption","Optimal point redemption strategy by trip")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Integrate Google Flights price alerts")
        st.markdown("- [ ] Award chart reference (Delta, United, AA)")

    # ─────────────────────────────────────────────────────────────────────────
    # CALENDAR
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📅  Calendar", expanded=False):
        _page_header("📅", "Calendar", "pages/5_📅_Calendar.py", ["Admin", "User"], "Live")
        st.markdown("**Purpose:** Central family calendar — all reminders and events in one view.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("🔔 All Reminders",  "All active reminders across all sections, sortable by date")
        _feature_row("📅 Events View",    "Calendar grid showing upcoming events")
        _feature_row("🏫 School Calendar","FISD academic calendar with grading periods")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Google Calendar sync")
        st.markdown("- [ ] iCal export for FISD/Tamil school events")

    # ─────────────────────────────────────────────────────────────────────────
    # ACCOUNT TRACKER
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📊  Account Tracker", expanded=False):
        _page_header("📊", "Account Tracker", "pages/6_📊_Account_Tracker.py", ["Admin", "User"], "Live")
        st.markdown("**Purpose:** Financial accounts — balances, analytics, retirement projections.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("📥 Balance Input",      "Enter/upload account balances. AI auto-reads from statements.")
        _feature_row("📊 Analytics",          "Monthly trend, year-end totals, Self vs Spouse comparison.")
        _feature_row("🔮 Projections",        "Retirement projections to 2040 with IRS contribution modeling.")
        _feature_row("⚙️ Setup",              "Add accounts with broker + tax status. Manual entries (real estate, auto). Broker management.")
        _feature_row("🔔 Market Alerts",      "Trigger conditions for SPY/QQQ drops. Notified via ntfy push.")
        st.markdown("**Google Sheets tabs used:**")
        st.markdown("`accounts` · `account_balances` · `market_alerts` · `brokers` · `manual_accounts`")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Net worth chart (accounts + manual entries combined)")
        st.markdown("- [ ] Import from Schwab/Fidelity CSV")
        st.markdown("- [ ] Debt-to-equity ratio tracker")

    # ─────────────────────────────────────────────────────────────────────────
    # ADMIN PANEL
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("🔒  Admin Panel", expanded=False):
        _page_header("🔒", "Admin Panel", "pages/7_🔒_Admin.py", ["Admin only"], "Live")
        st.markdown("**Purpose:** Site administration — page controls, maintenance, documentation.")
        st.markdown("**Sub-pages (tabs):**")
        _feature_row("🔧 Page & Feature Management", "Toggle pages/features per role. Kid role hardcoded to Kids-only.")
        _feature_row("🚧 Maintenance Mode",          "Enable/disable site with custom message. Admin always exempt.")
        _feature_row("📖 Site Navigation & Help",    "This document — placeholder framework for all features.")
        st.markdown("**Secrets required (Streamlit Secrets):**")
        st.markdown("`ADMIN_PASSWORD` · `USER_PASSWORD` · `KID_PASSWORD`")
        st.markdown("**Notes / To-Do:**")
        st.markdown("- [ ] Audit log (who logged in, when)")
        st.markdown("- [ ] Per-user feature-level overrides (future)")
        st.markdown("- [ ] Email notification when maintenance mode is toggled")

    # ── GSheets Schema Reference ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="admin-section">📋 Google Sheets Tab Reference</div>', unsafe_allow_html=True)
    sheet_data = [
        ("accounts",         "account_id, account_name, account_type, owner, active, broker_name, tax_status"),
        ("account_balances", "date, account_id, account_name, balance"),
        ("market_alerts",    "id, ticker, condition, threshold, channels, active"),
        ("brokers",          "broker_id, broker_name, active"),
        ("manual_accounts",  "entry_date, account_name, owner, category, value, notes, created_at"),
        ("reminders",        "id, section, title, message, due_date, remind_days, frequency, channels, status, created_at"),
        ("insurance_policies","id, policy_name, type, carrier, premium, renewal_date, active, notes"),
        ("cc_cards",         "id, card_name, bank, limit, reward_type, annual_fee, active"),
        ("classes",          "id, name, subject, teacher, active"),
        ("AppSettings",      "key, value  ← page/feature flags + maintenance state"),
    ]
    import pandas as pd
    sheets_df = pd.DataFrame(sheet_data, columns=["Tab Name", "Columns"])
    st.dataframe(sheets_df, use_container_width=True, hide_index=True,
                 column_config={
                     "Tab Name": st.column_config.TextColumn(width="medium"),
                     "Columns":  st.column_config.TextColumn(width="large"),
                 })
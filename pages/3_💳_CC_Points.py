"""CC & Points — maximize rewards, track cards, lounge access."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="AiPi360 · CC & Points", page_icon="💳", layout="wide")

from backend.auth import require_auth, sign_out
require_auth()

from components.metric_card import section_header, coming_soon
from components.reminder_banner import render_section_reminders
from services.cc_points import (
    list_cards, add_card, delete_card,
    total_annual_fees, fees_due_soon, icon as card_icon,
)
from backend.gsheet import read_sheet

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.cc-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:18px; margin-bottom:8px;
}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

section_header("💳", "CC & Points", "Maximize rewards, track annual fees & lounge access")

try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "cc")
except Exception:
    pass

tab1, tab2, tab3, tab4 = st.tabs(["💳 My Cards", "🏆 Points Strategy", "🛋️ Lounge Access", "💡 Best Offers"])

# ── My Cards ──────────────────────────────────────────────────────────────────
with tab1:
    df = list_cards()
    total_fees = total_annual_fees(df)
    due_df = fees_due_soon(30, df)

    k1, k2, k3 = st.columns(3)
    k1.metric("💳 Active Cards", len(df) if not df.empty else 0)
    k2.metric("💰 Total Annual Fees", f"${total_fees:,.0f}")
    k3.metric("⏰ Fee Due in 30d", len(due_df) if not due_df.empty else 0)

    if not df.empty:
        for _, row in df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3,2,2,1])
                with c1:
                    st.markdown(f"**{card_icon(row.get('bank',''))} {row['name']}** `···{row.get('last4','')}`")
                    st.caption(row.get("bank","").title())
                with c2:
                    st.markdown(f"Annual Fee: **${float(row.get('annual_fee',0) or 0):,.0f}**")
                    st.caption(f"Due: {row.get('fee_due_date','—')}")
                with c3:
                    st.markdown(f"Limit: **${float(row.get('credit_limit',0) or 0):,.0f}**")
                with c4:
                    if st.button("🗑️", key=f"del_cc_{row['id']}", help="Remove card"):
                        delete_card(row["id"])
                        st.rerun()
                if row.get("perks"):
                    st.caption(f"✨ {row['perks']}")
                st.markdown("---")
    else:
        st.info("No cards yet. Add your first below.")

    with st.expander("➕ Add Credit Card"):
        with st.form("add_cc_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cname  = st.text_input("Card Name (e.g. Chase Sapphire Preferred)")
                cbank  = st.text_input("Bank / Issuer")
            with c2:
                clast4 = st.text_input("Last 4 digits", max_chars=4)
                cfee   = st.number_input("Annual Fee ($)", min_value=0.0, step=5.0)
            with c3:
                cfee_due = st.date_input("Fee Due Date", value=date.today())
                climit   = st.number_input("Credit Limit ($)", min_value=0.0, step=500.0)
            cperks = st.text_area("Perks / Benefits (brief)", height=60)
            if st.form_submit_button("Add Card", type="primary"):
                if cname:
                    add_card(cname, cbank, clast4, cfee, cfee_due, climit, cperks)
                    st.success(f"✅ Added {cname}")
                    st.rerun()

# ── Points Strategy ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### 🏆 Maximize Your Points")
    st.markdown("""
<div style="background:#f0fdf4;border-radius:12px;padding:20px;border:1px solid #bbf7d0;margin-bottom:16px;">
<b>💡 Category maximization guide:</b>
<table style="width:100%;margin-top:10px;border-collapse:collapse;">
<tr style="background:#dcfce7;"><th style="padding:8px;text-align:left;">Category</th><th>Best Card to Use</th><th>Points/$ </th></tr>
<tr><td style="padding:6px;">✈️ Travel / Airlines</td><td>Chase Sapphire / Amex Platinum</td><td>3-5x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">🏨 Hotels</td><td>Marriott Bonvoy / Hilton Honors</td><td>6-14x</td></tr>
<tr><td style="padding:6px;">🍽️ Dining</td><td>Amex Gold / Chase Sapphire</td><td>3-4x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">🛒 Groceries</td><td>Amex Gold / Blue Cash</td><td>4-6x</td></tr>
<tr><td style="padding:6px;">⛽ Gas</td><td>Citi Custom Cash / BofA</td><td>3-5x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">📺 Streaming</td><td>Use card with streaming credit</td><td>Reimbursed</td></tr>
</table>
</div>""", unsafe_allow_html=True)

    st.markdown("##### 💸 Smart Allowance Usage")
    st.markdown("""
- **Netflix / Streaming** — use the card that reimburses entertainment
- **Uber / Lyft credits** — Amex Platinum, Chase Sapphire
- **Dining credits** — use monthly before they expire
- **Fancy restaurants** — book through Amex Fine Dining for bonus points
- **Travel portal vs. transfer** — compare before booking; transfers often win 20-30%
""")
    coming_soon("Personalized points optimizer — enter your cards for custom recommendations")

# ── Lounge Access ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🛋️ Airport Lounge Access")
    st.markdown("""
| Network | Access via | Guest Policy |
|---------|-----------|--------------|
| ✈️ Priority Pass | Amex Platinum, Chase Sapphire Reserve | Varies |
| 🔵 Centurion Lounge | Amex Platinum / Centurion | 2 free guests |
| 🟠 Capital One Lounge | Venture X | 2 free guests |
| 🔴 Delta Sky Club | Delta Amex Reserve | Paid guests |
| 🟡 Admirals Club | Citi AAdvantage | Fee or card |
""")
    coming_soon("Lounge finder — search by airport with your access level")

# ── Best Offers ───────────────────────────────────────────────────────────────
with tab4:
    coming_soon("Best current credit card offers — updated via nightly scan + Claude analysis")

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
    CARD_REWARDS, LOUNGE_DATA, TOP_OFFERS, SPEND_CATEGORIES,
    match_card, best_card_per_category, calc_annual_rewards, user_lounge_networks,
    BANK_ICONS,
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
    st.markdown("#### 🏆 Points Optimizer")

    # Match user's cards to the knowledge base
    user_cards_df = list_cards()
    matched_keys, unmatched = [], []
    if not user_cards_df.empty:
        for _, row in user_cards_df.iterrows():
            key = match_card(str(row.get("name", "")))
            if key:
                matched_keys.append(key)
            else:
                unmatched.append(str(row.get("name", "")))
        matched_keys = list(dict.fromkeys(matched_keys))  # dedupe preserving order

    opt_tab, calc_tab, ref_tab = st.tabs(["🎯 Best Card by Category", "🧮 Rewards Calculator", "📋 General Guide"])

    # ── Optimizer: best card per category from user's wallet ─────────────────
    with opt_tab:
        if matched_keys:
            best = best_card_per_category(matched_keys)
            # Header row
            rows_html = ""
            for i, (cat_label, cat_key) in enumerate(SPEND_CATEGORIES):
                if cat_key not in best:
                    continue
                bkey, bcpp = best[cat_key]
                card = CARD_REWARDS[bkey]
                mult = card["categories"].get(cat_key, 1)
                pct  = f"{mult:.1f}x ({bcpp*100:.1f}¢/$)"
                icon_c = card_icon(card["bank"])
                bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
                rows_html += (
                    f'<tr style="background:{bg};">'
                    f'<td style="padding:7px 10px;font-size:13px;">{cat_label}</td>'
                    f'<td style="padding:7px 10px;font-size:13px;font-weight:600;">'
                    f'{icon_c} {card["display"]}</td>'
                    f'<td style="padding:7px 10px;font-size:13px;color:#16a34a;font-weight:700;">{pct}</td>'
                    f'<td style="padding:7px 10px;font-size:11px;color:#64748b;">{card["network"]}</td>'
                    f'</tr>'
                )
            st.markdown(
                f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;'
                f'padding:4px;margin-bottom:12px;">'
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tr style="background:#dcfce7;">'
                f'<th style="padding:8px 10px;text-align:left;font-size:12px;">Category</th>'
                f'<th style="padding:8px 10px;text-align:left;font-size:12px;">Best Card in Your Wallet</th>'
                f'<th style="padding:8px 10px;text-align:left;font-size:12px;">Rate</th>'
                f'<th style="padding:8px 10px;text-align:left;font-size:12px;">Points Network</th>'
                f'</tr>{rows_html}</table></div>',
                unsafe_allow_html=True,
            )
            # Credits/perks reminders
            st.markdown("##### 💸 Don't forget your monthly credits")
            for key in matched_keys:
                card = CARD_REWARDS[key]
                if card.get("credits"):
                    credits_list = " · ".join(card["credits"])
                    st.markdown(
                        f'<div style="background:#fefce8;border-left:3px solid #ca8a04;'
                        f'border-radius:6px;padding:6px 12px;margin:4px 0;font-size:12.5px;">'
                        f'<b>{card_icon(card["bank"])} {card["display"]}</b> — {credits_list}</div>',
                        unsafe_allow_html=True,
                    )
            if unmatched:
                st.caption(f"⚠️ Not in database (add manually): {', '.join(unmatched)}")
        else:
            st.info("Add your cards in the **My Cards** tab to see personalized recommendations.")
            st.markdown("Once added, this view shows which of YOUR cards earns the most for each spending category.")

    # ── Monthly rewards calculator ───────────────────────────────────────────
    with calc_tab:
        st.markdown("##### 🧮 Estimate Annual Rewards Value")
        st.markdown("Enter your **monthly spend** per category to see which card earns the most for your habits.")
        with st.form("rewards_calc"):
            spend: dict[str, float] = {}
            col_a, col_b = st.columns(2)
            for i, (cat_label, cat_key) in enumerate(SPEND_CATEGORIES):
                col = col_a if i % 2 == 0 else col_b
                spend[cat_key] = col.number_input(cat_label, min_value=0.0, step=50.0,
                                                   value=0.0, key=f"spend_{cat_key}")
            calc_keys = matched_keys if matched_keys else list(CARD_REWARDS.keys())[:6]
            compare_label = "Your matched cards" if matched_keys else "Sample popular cards"
            submitted = st.form_submit_button("Calculate Rewards", type="primary")

        if submitted and any(v > 0 for v in spend.values()):
            results = [(key, calc_annual_rewards(spend, key)) for key in calc_keys]
            results.sort(key=lambda x: x[1], reverse=True)
            import plotly.graph_objects as _go
            names  = [CARD_REWARDS[k]["display"] for k, _ in results]
            values = [v for _, v in results]
            colors = ["#16a34a" if i == 0 else "#3b82f6" if i == 1 else "#94a3b8"
                      for i in range(len(results))]
            fig = _go.Figure(_go.Bar(
                x=names, y=values, marker_color=colors,
                text=[f"${v:,.0f}" for v in values], textposition="outside",
            ))
            fig.update_layout(
                title=f"Estimated Annual Rewards — {compare_label}",
                yaxis_title="Est. $ value/year", height=340,
                margin=dict(t=40, b=10), plot_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig, use_container_width=True)
            best_key, best_val = results[0]
            best_card = CARD_REWARDS[best_key]
            st.success(
                f"🏆 **{best_card['display']}** earns the most — ~**${best_val:,.0f}/yr** "
                f"at {best_card['point_value']}¢/pt ({best_card['network']})"
            )
            st.caption("Estimates use conservative point values. Actual value varies by redemption method.")

    # ── Generic reference guide ──────────────────────────────────────────────
    with ref_tab:
        st.markdown("""
<div style="background:#f0fdf4;border-radius:12px;padding:16px;border:1px solid #bbf7d0;">
<b>💡 General category maximization guide:</b>
<table style="width:100%;margin-top:10px;border-collapse:collapse;">
<tr style="background:#dcfce7;"><th style="padding:8px;text-align:left;">Category</th><th>Best Cards</th><th>Rate</th></tr>
<tr><td style="padding:6px;">✈️ Travel / Airlines</td><td>CSR, Venture X, Amex Platinum</td><td>5–10x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">🍽️ Dining</td><td>Amex Gold, CSP, CSR</td><td>3–4x</td></tr>
<tr><td style="padding:6px;">🛒 Grocery</td><td>Amex Gold, Blue Cash Preferred</td><td>4–6x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">⛽ Gas</td><td>Blue Cash Preferred, Citi Custom Cash</td><td>3–5x</td></tr>
<tr><td style="padding:6px;">📺 Streaming</td><td>Blue Cash Preferred, CSP</td><td>3–6x</td></tr>
<tr style="background:#f9fafb;"><td style="padding:6px;">🛍️ Everything else</td><td>Citi Double Cash, CFU</td><td>2x flat</td></tr>
</table></div>""", unsafe_allow_html=True)
        st.markdown("""
**💡 Pro tips**
- **Transfer vs. portal** — airline/hotel transfers typically get 50–100% more value than portal redemptions
- **Monthly credits** — set a calendar reminder to use Amex Gold dining ($10/mo) and Uber Cash ($10/mo)
- **Pair cards** — CFU + CSP earns 1.5x everywhere + boosts CFU points to 1.25¢ via CSP portal
- **5/24 rule** — Chase denies most applications if you opened 5+ cards in 24 months; plan accordingly
""")

# ── Lounge Access ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🛋️ Airport Lounge Finder")

    # Determine user's lounge networks
    user_cards_df2 = list_cards()
    matched_keys2: list[str] = []
    if not user_cards_df2.empty:
        for _, row in user_cards_df2.iterrows():
            key = match_card(str(row.get("name", "")))
            if key:
                matched_keys2.append(key)
    matched_keys2 = list(dict.fromkeys(matched_keys2))
    user_networks = user_lounge_networks(matched_keys2)

    # Network summary banner
    if user_networks:
        nets_html = " · ".join(
            f'<span style="background:#dbeafe;color:#1d4ed8;border-radius:20px;'
            f'padding:2px 10px;font-size:12px;font-weight:600;">{n}</span>'
            for n in sorted(user_networks)
        )
        st.markdown(
            f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;'
            f'padding:10px 16px;margin-bottom:12px;">🎟️ <b>Your lounge access:</b> {nets_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Add your cards in **My Cards** to see which lounges you can access.")

    # Airport search
    airport_list = sorted(LOUNGE_DATA.keys())
    airport_options = {f"{code} — {LOUNGE_DATA[code]['city']}": code for code in airport_list}
    sel_label = st.selectbox(
        "Search airport", ["— select —"] + list(airport_options.keys()), key="lounge_airport"
    )

    if sel_label != "— select —":
        sel_code = airport_options[sel_label]
        airport  = LOUNGE_DATA[sel_code]
        st.markdown(f"##### ✈️ {sel_code} — {airport['name']}")

        for lounge in airport["lounges"]:
            network = lounge["network"]
            has_access = any(network == n or network in user_networks for n in user_networks) \
                         or network in user_networks
            bg     = "#f0fdf4" if has_access else "#f8fafc"
            border = "#16a34a" if has_access else "#e2e8f0"
            badge  = ('✅ <span style="color:#15803d;font-weight:700;">You have access</span>'
                      if has_access else
                      '<span style="color:#94a3b8;">No access with current cards</span>')
            # Which of user's cards grants access
            grant_cards = []
            for key in matched_keys2:
                if network in CARD_REWARDS[key].get("lounge_networks", []):
                    grant_cards.append(CARD_REWARDS[key]["display"])
            via_str = ""
            if grant_cards:
                via_str = (f' <span style="font-size:11px;color:#64748b;">via '
                           f'{", ".join(grant_cards)}</span>')
            st.markdown(
                f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
                f'padding:10px 16px;margin:5px 0;">'
                f'<span style="font-weight:600;font-size:13.5px;">{lounge["name"]}</span>'
                f'<span style="color:#64748b;font-size:12px;margin-left:10px;">Terminal {lounge["terminal"]}</span>'
                f'<br>{badge}{via_str}</div>',
                unsafe_allow_html=True,
            )

    # Reference table
    with st.expander("📋 Lounge network overview", expanded=False):
        st.markdown("""
| Network | Top Access Cards | Guests |
|---------|-----------------|--------|
| 🔵 Centurion Lounge | Amex Platinum | 2 free guests |
| 🟣 Priority Pass | Amex Platinum, Chase Sapphire Reserve, Venture X | Varies by card |
| 🟠 Capital One Lounge | Capital One Venture X | 2 free guests |
| 🔴 Delta Sky Club | Delta Amex Reserve, Amex Platinum* | Paid guests |
| 🟡 Admirals Club | Citi AAdvantage Executive | 2 free guests |
| 🔵 United Club | United Club Infinite card | 2 free guests |
| 🟢 Chase Sapphire Lounge | Chase Sapphire Reserve | 2 free guests |
""")
        st.caption("*Amex Platinum Delta Sky Club access may be limited to 10 visits/yr depending on card version.")

# ── Best Offers ───────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### 💡 Top Credit Card Offers")
    st.caption("⚠️ Offers change frequently — always verify current terms at the issuer's website before applying.")

    # Group by category
    categories_seen = []
    offers_by_cat: dict[str, list] = {}
    for offer in TOP_OFFERS:
        cat = offer["category"]
        if cat not in offers_by_cat:
            offers_by_cat[cat] = []
            categories_seen.append(cat)
        offers_by_cat[cat].append(offer)

    for cat in categories_seen:
        st.markdown(f"##### 🏆 {cat}")
        cols = st.columns(len(offers_by_cat[cat]))
        for col, offer in zip(cols, offers_by_cat[cat]):
            bank_icon = BANK_ICONS.get(offer["bank"], "💳")
            fee_color = "#16a34a" if offer["annual_fee"] == 0 else "#dc2626" if offer["annual_fee"] >= 500 else "#ea580c"
            col.markdown(
                f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;'
                f'padding:16px;height:100%;">'
                f'<div style="font-size:14px;font-weight:700;margin-bottom:4px;">'
                f'{bank_icon} {offer["card"]}</div>'
                f'<div style="font-size:11px;color:{fee_color};font-weight:600;margin-bottom:8px;">'
                f'Annual fee: ${offer["annual_fee"]:,}</div>'
                f'<div style="background:#fefce8;border-radius:8px;padding:8px;margin-bottom:8px;">'
                f'<div style="font-size:11px;font-weight:700;color:#92400e;">Sign-on offer</div>'
                f'<div style="font-size:13px;font-weight:600;color:#713f12;">{offer["offer"]}</div>'
                f'<div style="font-size:11px;color:#92400e;">Spend {offer["spend_req"]}</div>'
                f'<div style="font-size:11.5px;color:#15803d;font-weight:600;">'
                f'Est. value: {offer["est_value"]}</div>'
                f'</div>'
                f'<div style="font-size:11.5px;color:#475569;line-height:1.5;">{offer["highlight"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("")  # spacer between groups

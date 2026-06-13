"""Credit Cards — manage cards, maximize rewards, compare top cards."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="AiPi360 · Credit Cards", page_icon="💳", layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css, inject_global_nav_css
require_auth()
check_maintenance()
check_page_access("cc_points")
inject_3d_tab_css()
inject_global_nav_css()

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

section_header("💳", "Credit Cards", "Manage cards, maximize rewards & compare top premium cards")

try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "cc")
except Exception:
    pass

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💳 My Cards", "🏆 Points Strategy", "🛋️ Lounge Access", "💡 Best Offers", "🃏 Card Compare"])

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

# ── Card Compare ──────────────────────────────────────────────────────────────
with tab5:

    # ── Card data ─────────────────────────────────────────────────────────────
    _CARDS = [
        {
            "id": "amex_plat", "name": "Amex Platinum", "issuer": "American Express",
            "network": "Amex", "color": "#B8A06A", "text_color": "#2c1a00",
            "annual_fee": 895, "welcome_bonus": "80,000–175,000 MR pts",
            "welcome_spend": "$8,000 in 6 months",
            "reward_rate": "5x flights (direct/Amex Travel), 5x hotels (Amex Travel), 1x all else",
            "points_currency": "Membership Rewards", "cpp_estimate": "1.8–2.1¢",
            "ref_link": "https://www.americanexpress.com/us/credit-cards/card/platinum/",
            "best_for": ["Lounge access", "Hotel status", "Premium travel perks"],
            "not_ideal_for": ["Low spenders (<$15k/yr)", "Those who won't maximize $1,400+ in credits"],
            "benefits": {
                "Travel Credits": [
                    {"name": "$200 Airline Fee Credit", "value": "$200/yr", "fp": True,
                     "notes": "Select ONE airline at enrollment. Covers incidental fees only — NOT ticket purchases. Re-select airline each Jan 1."},
                    {"name": "$200 Uber Cash", "value": "$200/yr", "fp": True,
                     "notes": "$15/month + $35 in Dec. Must add Amex Plat to Uber app. Does NOT roll over."},
                    {"name": "$600 Hotel Credit", "value": "$300 semi-annual", "fp": True,
                     "notes": "Up from $200/yr. Now $300 Jan–Jun + $300 Jul–Dec = $600/yr total. Valid at Fine Hotels + Resorts or The Hotel Collection via Amex Travel only. NOT bookable at hotel.com."},
                    {"name": "$189 CLEAR Plus Credit", "value": "$189/yr", "fp": False,
                     "notes": "Reimburses CLEAR Plus membership. Family plan not covered."},
                    {"name": "$155 Walmart+ Credit", "value": "$155/yr", "fp": True,
                     "notes": "Monthly charge only — annual prepay does NOT qualify."},
                    {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "fp": True,
                     "notes": "Once every 4 years. Can pay for another person's fee."},
                    {"name": "Centurion Lounge Access", "value": "Within 5 hrs of flight*", "fp": True,
                     "notes": "From July 8, 2026: access limited to within 5 hours of your departing/connecting flight. Guests $50 each unless $75k+ spend on card. Policy tightened significantly."},
                    {"name": "Priority Pass Select", "value": "Unlimited", "fp": False,
                     "notes": "Unlimited visits + 2 guests. Restaurant credit $28/person at select PP restaurants."},
                    {"name": "Delta SkyClub (when flying Delta)", "value": "10 visits/yr*", "fp": True,
                     "notes": "Capped at 10 visits/yr unless $75k+ spend on card (unlimited then). Must be flying Delta same day."},
                ],
                "Hotel & Lifestyle": [
                    {"name": "Fine Hotels + Resorts (FHR)", "value": "Elite perks", "fp": True,
                     "notes": "Room upgrade, noon check-in, 4pm late checkout, daily breakfast for 2, $100 property credit. Book via Amex Travel only."},
                    {"name": "The Hotel Collection (THC)", "value": "2-night min", "fp": True,
                     "notes": "$100 experience credit + room upgrade. Requires 2-night minimum. Fewer guarantees than FHR."},
                    {"name": "Hilton Honors Gold Status", "value": "Complimentary", "fp": True,
                     "notes": "80% bonus points, free breakfast at some properties. Must enroll via benefits portal."},
                    {"name": "Marriott Bonvoy Gold Elite", "value": "Complimentary", "fp": True,
                     "notes": "25% bonus points, enhanced room upgrade, 2pm checkout (request basis)."},
                ],
                "Dining & Entertainment": [
                    {"name": "$400 Resy Dining Credit", "value": "$400/yr", "fp": True,
                     "notes": "NEW in 2026. At US restaurants on Resy. Must book and dine through Resy app/site. Specific enrolled restaurants only — not all Resy listings qualify."},
                    {"name": "$300 Digital Entertainment Credit", "value": "$25/mo", "fp": True,
                     "notes": "Up from $240/yr. Now $300/yr ($25/mo). Covers Disney+, ESPN+, Hulu, Peacock, NYT, WSJ, SiriusXM, The Atlantic. NOT Netflix."},
                    {"name": "$300 Equinox Credit", "value": "$300/yr", "fp": False,
                     "notes": "For Equinox gym memberships including Equinox+ app."},
                    {"name": "Saks Fifth Avenue Credit", "value": "✗ Removed Jul 2026", "fp": True,
                     "notes": "Saks credit ($100/yr) ends July 1, 2026. No longer a benefit after that date."},
                ],
                "Protections": [
                    {"name": "Trip Cancellation / Interruption", "value": "$10,000/trip", "fp": True,
                     "notes": "$20k per year. Covered reasons must be listed. Pay fare with card."},
                    {"name": "Trip Delay Insurance", "value": "$500 after 6 hrs", "fp": False,
                     "notes": "Covers meals, lodging after 6-hour delay."},
                    {"name": "Cell Phone Protection", "value": "✗ Not included", "fp": True,
                     "notes": "Amex Plat does NOT include cell phone protection."},
                    {"name": "Primary Rental Car", "value": "✗ Secondary", "fp": False, "notes": ""},
                    {"name": "No Foreign Transaction Fee", "value": "✓", "fp": False, "notes": ""},
                ],
                "Transfer Partners": [
                    {"name": "Airlines (17+)", "value": "1:1 ratio", "fp": False,
                     "notes": "Delta, Aeroplan, United (shop), BA, Flying Blue, Avianca, Turkish, Singapore, ANA, Cathay, Emirates, Etihad, Hawaiian, Iberia, JetBlue, Qantas, Virgin Atlantic."},
                    {"name": "Hotels", "value": "varies", "fp": False,
                     "notes": "Hilton (1:2), Marriott (1:1), Choice (1:1)."},
                ],
            },
        },
        {
            "id": "csr", "name": "Chase Sapphire Reserve", "issuer": "Chase",
            "network": "Visa Infinite", "color": "#1a1a2e", "text_color": "#e8d5a3",
            "annual_fee": 795, "welcome_bonus": "60,000–75,000 UR pts",
            "welcome_spend": "$4,000 in 3 months",
            "reward_rate": "10x hotels+cars (Chase Travel), 5x flights (Chase Travel), 3x dining+travel, 1x else",
            "points_currency": "Ultimate Rewards", "cpp_estimate": "1.5–2.0¢",
            "ref_link": "https://creditcards.chase.com/rewards-credit-cards/sapphire/reserve",
            "best_for": ["Flexible $300 travel credit", "Primary rental car", "Edit hotel credits", "Cell phone protection"],
            "not_ideal_for": ["Amex lounge seekers", "Those who won't use $500 hotel credit"],
            "benefits": {
                "Travel Credits": [
                    {"name": "$300 Travel Credit", "value": "$300/yr", "fp": False,
                     "notes": "Broadest travel credit — any airline, hotel, Airbnb, Uber, Lyft, parking, tolls, transit, cruises. Resets on anniversary."},
                    {"name": "$500 The Edit Hotel Credit", "value": "$250 semi-annual", "fp": True,
                     "notes": "NEW. $250 Jan–Jun + $250 Jul–Dec = $500/yr at The Edit collection via Chase Travel. 2-night minimum prepaid stay required. Massive new benefit offsetting fee increase."},
                    {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "fp": False,
                     "notes": "Once every 4 years. Can use for authorized user."},
                    {"name": "Priority Pass Select", "value": "Unlimited", "fp": True,
                     "notes": "Unlimited visits + 2 guests. $28/person restaurant credit at select PP restaurants."},
                    {"name": "Chase Sapphire Lounge by The Club", "value": "Included", "fp": False,
                     "notes": "CSR-exclusive lounges at BOS, HKG, LGA, LAS, LHR, PHX, SFO and more. 2 guests free."},
                ],
                "Hotel & Lifestyle": [
                    {"name": "Luxury Hotel & Resort Collection", "value": "Elite perks", "fp": True,
                     "notes": "Room upgrade, early/late checkout, daily breakfast, $100 property credit. Book via Chase Travel."},
                    {"name": "Complimentary Lyft Pink", "value": "1 yr free", "fp": False,
                     "notes": "15% off rides, priority pickup. Auto-enrolls annually."},
                    {"name": "Authorized User Fee", "value": "$195/AU", "fp": True,
                     "notes": "Increased from $75 to $195/AU. Each AU gets Priority Pass. Evaluate if AU cost is worth it."},
                ],
                "Protections": [
                    {"name": "Trip Cancellation / Interruption", "value": "$10,000/trip", "fp": True,
                     "notes": "$20k per year. Listed covered reasons only."},
                    {"name": "Trip Delay Insurance", "value": "$500 after 6 hrs", "fp": False, "notes": ""},
                    {"name": "Primary Rental Car Insurance", "value": "✓ Primary", "fp": False,
                     "notes": "Decline CDW at counter. Primary — doesn't touch personal auto policy."},
                    {"name": "Cell Phone Protection", "value": "$800/claim", "fp": True,
                     "notes": "Up to 2 claims/yr. $50 deductible. Pay monthly bill with card."},
                    {"name": "No Foreign Transaction Fee", "value": "✓", "fp": False, "notes": ""},
                ],
                "Transfer Partners": [
                    {"name": "Airlines (11)", "value": "1:1 ratio", "fp": False,
                     "notes": "United, Southwest, BA, Aeroplan, Flying Blue, Iberia, Singapore, Virgin Atlantic, JetBlue, Emirates."},
                    {"name": "Hotels", "value": "1:1 ratio", "fp": False,
                     "notes": "Hyatt (best value — 1:1), IHG, Marriott."},
                ],
            },
        },
        {
            "id": "venture_x", "name": "Capital One Venture X", "issuer": "Capital One",
            "network": "Visa Infinite", "color": "#c8102e", "text_color": "#ffffff",
            "annual_fee": 395, "welcome_bonus": "75,000 miles",
            "welcome_spend": "$4,000 in 3 months",
            "reward_rate": "10x hotels+cars (C1 Travel), 5x flights (C1 Travel), 2x all else",
            "points_currency": "Capital One Miles", "cpp_estimate": "1.0–1.7¢",
            "ref_link": "https://capitalone.com/credit-cards/venture-x/",
            "best_for": ["Best fee-to-value ratio", "2x on everything", "C1 Lounge at DFW"],
            "not_ideal_for": ["Hyatt/Marriott/Hilton status seekers", "Portal-averse travelers"],
            "benefits": {
                "Travel Credits": [
                    {"name": "$300 C1 Travel Credit", "value": "$300/yr", "fp": True,
                     "notes": "ONLY for bookings through Capital One Travel portal. NOT for direct airline/hotel bookings."},
                    {"name": "10,000 Anniversary Miles", "value": "~$100 value", "fp": False,
                     "notes": "10k miles added each account anniversary. Worth $100+ toward C1 Travel. Offsets $100 of the fee."},
                    {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "fp": False, "notes": "Once every 4 years."},
                    {"name": "Priority Pass Select", "value": "Unlimited", "fp": False,
                     "notes": "Unlimited visits. PP guests now $35/person (changed Feb 2026)."},
                    {"name": "Capital One Lounge", "value": "Unlimited", "fp": False,
                     "notes": "C1 Lounges at DFW, DEN, IAD and more. 2 free guests per visit at C1 Lounges."},
                ],
                "Hotel & Lifestyle": [
                    {"name": "Premier Collection Hotels", "value": "Elite perks", "fp": True,
                     "notes": "$100 experience credit, room upgrade, early/late checkout, daily breakfast. Book via C1 Travel."},
                    {"name": "Authorized Users (up to 4)", "value": "$125/yr (all AUs)", "fp": True,
                     "notes": "From Feb 1, 2026: AUs no longer get free lounge access. Pay $125/yr per account to give all AUs C1+PP lounge access. PP guests now $35/person for everyone."},
                ],
                "Protections": [
                    {"name": "Trip Cancellation / Interruption", "value": "$2,000/trip", "fp": True,
                     "notes": "Lower cap than Amex/Chase ($2k vs $10k)."},
                    {"name": "Trip Delay Insurance", "value": "$500 after 6 hrs", "fp": False, "notes": ""},
                    {"name": "Primary Rental Car Insurance", "value": "✓ Primary", "fp": False, "notes": ""},
                    {"name": "Cell Phone Protection", "value": "$800/claim", "fp": False,
                     "notes": "Up to 2 claims/yr. $50 deductible. Pay phone bill with card."},
                    {"name": "No Foreign Transaction Fee", "value": "✓", "fp": False, "notes": ""},
                ],
                "Transfer Partners": [
                    {"name": "Airlines (15+)", "value": "1:1 mostly", "fp": True,
                     "notes": "Turkish, Aeroplan, Avianca, Flying Blue, BA, Singapore, Emirates, Etihad, Finnair, TAP, Cathay. Some at 2:1.5."},
                    {"name": "Hotels", "value": "1:1", "fp": False, "notes": "Wyndham, Choice Hotels."},
                ],
            },
        },
        {
            "id": "amex_gold", "name": "Amex Gold", "issuer": "American Express",
            "network": "Amex", "color": "#CFB271", "text_color": "#2c1a00",
            "annual_fee": 325, "welcome_bonus": "60,000–100,000 MR pts",
            "welcome_spend": "$6,000 in 6 months",
            "reward_rate": "5x prepaid hotels (Amex Travel), 4x dining (worldwide), 4x US supermarkets (up to $25k/yr), 3x flights, 2x prepaid cars (Amex Travel), 1x else",
            "points_currency": "Membership Rewards", "cpp_estimate": "1.8–2.1¢",
            "ref_link": "https://www.americanexpress.com/us/credit-cards/card/gold-card/",
            "best_for": ["Best dining earn rate (4x)", "Grocery shoppers (4x)", "5x hotels via Amex Travel"],
            "not_ideal_for": ["Lounge access needed", "Travelers needing trip protections"],
            "benefits": {
                "Travel Credits": [
                    {"name": "$100 Airline Fee Credit", "value": "$100/yr", "fp": True,
                     "notes": "ONE pre-selected airline, incidental fees only (not tickets). Resets Jan 1."},
                    {"name": "$120 Uber Cash", "value": "$10/mo", "fp": True,
                     "notes": "$10/month to Uber/Uber Eats. Does NOT roll over. Add Gold to Uber app."},
                    {"name": "5x Prepaid Hotels", "value": "5x MR", "fp": True,
                     "notes": "NEW Apr 2026. 5x MR on prepaid hotel bookings via AmexTravel.com or Amex Travel App. Was 2x previously. Must book through Amex Travel — direct bookings earn 1x."},
                    {"name": "2x Prepaid Car Rentals", "value": "2x MR", "fp": True,
                     "notes": "NEW Apr 2026. 2x MR on prepaid car rentals via AmexTravel.com or Amex Travel App."},
                    {"name": "No Lounge Access", "value": "✗ None", "fp": True,
                     "notes": "Gold does not include any lounge access. Upgrade to Amex Plat for this."},
                    {"name": "No GE / TSA Credit", "value": "✗ None", "fp": True,
                     "notes": "Amex Gold does not offer Global Entry or TSA Pre✓ credit."},
                ],
                "Dining & Entertainment": [
                    {"name": "$120 Dining Credit", "value": "$10/mo", "fp": True,
                     "notes": "At Grubhub, Cheesecake Factory, Goldbelly, Wine.com, Milk Bar, select Shake Shack, Buffalo Wild Wings (NEW 2026). NOT all restaurants."},
                    {"name": "$100 Resy Credit", "value": "$50 semi-annual", "fp": True,
                     "notes": "US restaurants on Resy only. $50 Jan–Jun, $50 Jul–Dec. Must book and dine via Resy."},
                    {"name": "4x on Dining", "value": "4x MR", "fp": False,
                     "notes": "All restaurants worldwide including delivery. Best dining earn rate among premium cards."},
                    {"name": "4x on US Supermarkets", "value": "4x MR (cap $25k)", "fp": True,
                     "notes": "Capped at $25k/yr spend, then 1x. Does NOT include warehouse clubs (Costco, Sam's)."},
                    {"name": "Hertz Five Star Status", "value": "Complimentary", "fp": False,
                     "notes": "NEW 2026. Faster pickup, upgrades at Hertz. Enroll via Amex benefits portal."},
                ],
                "Protections": [
                    {"name": "Trip Delay Insurance", "value": "✗ Not included", "fp": True,
                     "notes": "Amex Gold does NOT have trip delay insurance. Major gap vs CSR/Venture X."},
                    {"name": "Trip Cancellation", "value": "✗ Not included", "fp": True, "notes": ""},
                    {"name": "Primary Rental Car", "value": "✗ Secondary", "fp": False, "notes": ""},
                    {"name": "No Foreign Transaction Fee", "value": "✓", "fp": False, "notes": ""},
                ],
                "Transfer Partners": [
                    {"name": "Airlines (17+)", "value": "1:1 ratio", "fp": False,
                     "notes": "Same MR partners as Amex Platinum — Delta, Aeroplan, BA, Flying Blue, Turkish, Singapore, etc."},
                    {"name": "Hotels", "value": "varies", "fp": False,
                     "notes": "Hilton (1:2), Marriott (1:1), Choice (1:1)."},
                ],
            },
        },
        {
            "id": "csp", "name": "Chase Sapphire Preferred", "issuer": "Chase",
            "network": "Visa Signature", "color": "#2e5fa3", "text_color": "#ffffff",
            "annual_fee": 95, "welcome_bonus": "60,000–100,000 UR pts",
            "welcome_spend": "$4,000 in 3 months",
            "reward_rate": "5x Chase Travel, 3x dining+online grocery+streaming+gas+EV+vacation rentals, 2x other travel, 1x else",
            "points_currency": "Ultimate Rewards", "cpp_estimate": "1.25–2.0¢",
            "ref_link": "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
            "best_for": ["Entry-level premium card at $95", "3x gas & vacation rentals (new)", "Primary rental car on budget", "GE credit (new)"],
            "not_ideal_for": ["Frequent lounge visitors", "Heavy Hyatt spenders (4:3 ratio from Oct 2026)"],
            "benefits": {
                "Travel Credits": [
                    {"name": "$100 Annual Hotel Credit", "value": "$100/yr", "fp": True,
                     "notes": "Doubled from $50. Hotels booked through Chase Travel only. Resets on card anniversary."},
                    {"name": "Global Entry / TSA Pre✓", "value": "$120 every 4 yrs", "fp": False,
                     "notes": "NEW 2026. Application fee credit for GE, TSA Pre✓, or NEXUS. Previously CSP did not include this."},
                    {"name": "Complimentary Apple TV+", "value": "1 year free", "fp": True,
                     "notes": "NEW. Activate by Dec 31, 2026. One-time benefit for new and existing cardholders."},
                    {"name": "No Lounge Access", "value": "✗ None", "fp": False, "notes": ""},
                ],
                "Dining & Entertainment": [
                    {"name": "10% Anniversary Bonus", "value": "Removed for new", "fp": True,
                     "notes": "REMOVED for cardholders who apply on/after June 15, 2026. Existing cardholders keep it through Oct 1, 2026 (points awarded by Jan 31, 2027)."},
                    {"name": "3x Dining", "value": "3x UR", "fp": False, "notes": "All restaurants including delivery."},
                    {"name": "3x Online Groceries", "value": "3x UR", "fp": True,
                     "notes": "Instacart, Amazon Fresh. NOT physical grocery stores."},
                    {"name": "3x Streaming", "value": "3x UR", "fp": False,
                     "notes": "Netflix, Hulu, Spotify, Disney+, etc."},
                    {"name": "3x Gas & EV Charging", "value": "3x UR", "fp": False,
                     "notes": "NEW 2026. Gas stations and EV charging stations earn 3x."},
                    {"name": "3x Vacation Rentals", "value": "3x UR", "fp": False,
                     "notes": "NEW 2026. Airbnb, Vrbo and other vacation rental platforms earn 3x."},
                ],
                "Protections": [
                    {"name": "Trip Cancellation / Interruption", "value": "$10,000/trip", "fp": True,
                     "notes": "$20k per year. Listed covered reasons only."},
                    {"name": "Trip Delay Insurance", "value": "$500 after 12 hrs", "fp": True,
                     "notes": "Triggers at 12 hours — stricter than CSR (6 hrs) and Venture X (6 hrs)."},
                    {"name": "Primary Rental Car Insurance", "value": "✓ Primary", "fp": False,
                     "notes": "Primary coverage — unusual for a $95 card. Same as CSR."},
                    {"name": "No Cell Phone Protection", "value": "✗ None", "fp": False, "notes": ""},
                    {"name": "No Foreign Transaction Fee", "value": "✓", "fp": False, "notes": ""},
                ],
                "Transfer Partners": [
                    {"name": "Airlines (11)", "value": "1:1 ratio", "fp": False,
                     "notes": "Same Chase UR partners as CSR — United, Southwest, BA, Aeroplan, Flying Blue, Iberia, Singapore, Virgin Atlantic, JetBlue, Emirates."},
                    {"name": "Hyatt", "value": "4:3 from Oct 2026", "fp": True,
                     "notes": "MAJOR CHANGE. Hyatt transfers move from 1:1 to 4:3 starting Oct 1, 2026 (immediately for new cardholders from June 15, 2026). 1,000 UR → 750 Hyatt pts. CSR stays 1:1."},
                    {"name": "IHG + Marriott", "value": "1:1 ratio", "fp": False, "notes": ""},
                ],
            },
        },
    ]

    _COMPARE_ROWS = [
        ("Annual Fee",            ["$895", "$795", "$395", "$325", "$95"]),
        ("Network",               ["Amex", "Visa Infinite", "Visa Infinite", "Amex", "Visa Signature"]),
        ("Points Currency",       ["Membership Rewards", "Ultimate Rewards", "C1 Miles", "Membership Rewards", "Ultimate Rewards"]),
        ("Est. CPP",              ["1.8–2.1¢", "1.5–2.0¢", "1.0–1.7¢", "1.8–2.1¢", "1.25–2.0¢"]),
        ("Welcome Bonus",         ["80k–175k MR", "60k–75k UR", "75k miles", "60k–100k MR", "60k–100k UR"]),
        ("Min Spend (Bonus)",     ["$8k / 6mo", "$4k / 3mo", "$4k / 3mo", "$6k / 6mo", "$4k / 3mo"]),
        ("Travel Credit",         ["$200 airline\n(incidentals only)", "$300 any travel\n(broadest)", "$300 C1 Travel\n(portal only)", "$100 airline\n(incidentals only)", "$100 Chase Travel\n(hotels only)"]),
        ("Hotel Credit",          ["$600/yr\n($300 semi-annual)\nFHR/THC only", "$500/yr\n($250 semi-annual)\nThe Edit, 2-night min", "✗ None", "✗ None", "$100/yr\nChase Travel only"]),
        ("Dining Credit",         ["$400 Resy\n+ $300 digital ent.", "—", "—", "$120/yr\n(select merchants)", "—"]),
        ("Lounge Access",         ["Centurion + PP\n+ Delta (10x/yr)\n5hr flight window", "CSR Lounge + PP\n+ Sapphire Lounges", "C1 Lounge + PP\n+ Plaza Premium", "✗ None", "✗ None"]),
        ("Hotel Status",          ["Hilton Gold\n+ Marriott Gold", "✗ None\n(LHRC perks)", "Premier Collection\nperks", "✗ None\n(THC perks)", "LHRC perks"]),
        ("GE / TSA Pre✓",         ["✓ GE ($100)", "✓ GE ($100)", "✓ GE ($100)", "✗ None", "✓ GE ($120) NEW"]),
        ("Trip Cancel/Interrupt", ["✓ $10k/trip", "✓ $10k/trip", "✓ $2k/trip", "✗ None", "✓ $10k/trip"]),
        ("Trip Delay",            ["✓ 6 hrs / $500", "✓ 6 hrs / $500", "✓ 6 hrs / $500", "✗ None", "✓ 12 hrs / $500"]),
        ("Primary Rental Car",    ["✗ Secondary", "✓ Primary", "✓ Primary", "✗ Secondary", "✓ Primary"]),
        ("Cell Phone Prot.",      ["✗ None", "✓ $800/claim", "✓ $800/claim", "✗ None", "✗ None"]),
        ("AU Lounge / Fee",       ["✗ $175/AU", "✗ $195/AU\n(up from $75)", "✗ $125/yr (all AUs)\nfrom Feb 2026", "N/A", "N/A"]),
        ("No FX Fee",             ["✓", "✓", "✓", "✓", "✓"]),
        ("Best Transfer Partner", ["Aeroplan (2¢+)", "Hyatt 1:1 (2.5¢+)", "Aeroplan (2¢+)", "Aeroplan (2¢+)", "Hyatt 4:3\nfrom Oct 2026"]),
    ]

    # ── CSS (scoped) ──────────────────────────────────────────────────────────
    st.markdown("""
<style>
.cc-hdr {
    border-radius:14px; padding:16px 18px 12px; margin-bottom:6px;
    min-height:130px; display:flex; flex-direction:column; justify-content:space-between;
}
.cc-hdr-name  { font-size:16px; font-weight:800; letter-spacing:.4px; }
.cc-hdr-issuer{ font-size:11px; opacity:.75; margin-top:2px; }
.cc-hdr-fee   { font-size:24px; font-weight:900; margin-top:8px; }
.cc-hdr-label { font-size:11px; opacity:.65; }
.cc-hdr-net   { font-size:11px; opacity:.8; margin-top:3px; font-style:italic; }
.ben-row {
    background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
    padding:7px 11px; margin-bottom:4px;
}
.ben-name  { font-size:13px; font-weight:700; color:#1e3a5f; }
.ben-val   { font-size:13px; font-weight:800; color:#059669; float:right; }
.ben-notes { font-size:11.5px; color:#475569; margin-top:3px; line-height:1.4; }
.fp-badge  {
    background:#fef3c7; color:#92400e; font-size:10px;
    padding:1px 6px; border-radius:10px; font-weight:700;
    display:inline-block; margin-left:6px; vertical-align:middle;
}
.cmp-tbl { width:100%; border-collapse:collapse; font-size:12px; }
.cmp-tbl th { padding:9px 10px; color:#fff; font-size:11px; font-weight:800;
              text-align:center; border-bottom:3px solid #fff; }
.cmp-tbl td { padding:7px 10px; border-bottom:1px solid #e2e8f0;
              text-align:center; vertical-align:middle; color:#334155; }
.cmp-tbl tr:hover td { background:#f0f9ff; }
.cmp-tbl td:first-child { text-align:left; font-weight:700; color:#1e3a5f; background:#f8fafc; width:140px; }
.cmp-tbl th:first-child { text-align:left; background:#1e3a5f; }
.ctick { color:#059669; font-weight:900; font-size:14px; }
.ccross{ color:#dc2626; font-weight:900; font-size:14px; }
.tg-good { background:#dcfce7; color:#166534; padding:2px 9px; border-radius:11px;
           font-size:11px; font-weight:700; display:inline-block; margin:2px; }
.tg-bad  { background:#fee2e2; color:#991b1b; padding:2px 9px; border-radius:11px;
           font-size:11px; font-weight:700; display:inline-block; margin:2px; }
.src-note { font-size:11px; color:#94a3b8; font-style:italic; }
</style>
""", unsafe_allow_html=True)

    st.markdown(
        "<div class='src-note'>Data verified June 2026 · Amex Plat $895 (Sep 2025), CSR $795 (Jun 2025) · "
        "⚠ fine print badges highlight gotchas · Always confirm at issuer site before applying</div>",
        unsafe_allow_html=True,
    )

    # ── Sub-tabs ──────────────────────────────────────────────────────────────
    cmp_tab, dive_tab, fp_tab, ref_tab = st.tabs([
        "📊 Side-by-Side", "🔍 Deep Dive", "⚠️ Fine Print", "🔗 References",
    ])

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _card_header(c):
        st.markdown(
            f'<div class="cc-hdr" style="background:{c["color"]};color:{c["text_color"]};">'
            f'<div><div class="cc-hdr-name">{c["name"]}</div>'
            f'<div class="cc-hdr-issuer">{c["issuer"]} · {c["network"]}</div></div>'
            f'<div><div class="cc-hdr-fee">${c["annual_fee"]:,}</div>'
            f'<div class="cc-hdr-label">annual fee</div>'
            f'<div class="cc-hdr-net">{c["points_currency"]} · ~{c["cpp_estimate"]}/pt</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    def _benefit_block(card, category):
        items = card["benefits"].get(category, [])
        if not items:
            st.markdown('<div style="color:#94a3b8;font-size:12px;padding:4px 0;">—</div>',
                        unsafe_allow_html=True)
            return
        for b in items:
            fp = '<span class="fp-badge">⚠ fine print</span>' if b.get("fp") else ""
            notes = f'<div class="ben-notes">{b["notes"]}</div>' if b.get("notes") else ""
            st.markdown(
                f'<div class="ben-row"><span class="ben-name">{b["name"]}</span>'
                f'<span class="ben-val">{b["value"]}</span>{fp}{notes}</div>',
                unsafe_allow_html=True,
            )

    # ── Side-by-Side ─────────────────────────────────────────────────────────
    with cmp_tab:
        st.markdown("**Select cards to compare:**")
        sel_cols = st.columns(len(_CARDS))
        selected_ids = []
        for i, card in enumerate(_CARDS):
            with sel_cols[i]:
                if st.checkbox(card["name"], value=True, key=f"cmp_sel_{card['id']}"):
                    selected_ids.append(card["id"])

        if selected_ids:
            selected = [c for c in _CARDS if c["id"] in selected_ids]
            all_indices = {c["id"]: i for i, c in enumerate(_CARDS)}

            hdr = '<tr><th style="min-width:130px;">Feature</th>'
            for c in selected:
                hdr += f'<th style="background:{c["color"]};color:{c["text_color"]};">{c["name"]}</th>'
            hdr += "</tr>"

            rows_html = ""
            for label, values in _COMPARE_ROWS:
                row = f"<tr><td>{label}</td>"
                for c in selected:
                    v = values[all_indices[c["id"]]]
                    v = v.replace("✓", '<span class="ctick">✓</span>') \
                         .replace("✗", '<span class="ccross">✗</span>') \
                         .replace("\n", "<br>")
                    row += f"<td>{v}</td>"
                row += "</tr>"
                rows_html += row

            st.markdown(
                f'<div style="overflow-x:auto;"><table class="cmp-tbl">'
                f'<thead>{hdr}</thead><tbody>{rows_html}</tbody></table></div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Select at least one card above.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Card Profiles")
        pcols = st.columns(len(_CARDS))
        for i, card in enumerate(_CARDS):
            with pcols[i]:
                _card_header(card)
                best_html = "".join(f'<span class="tg-good">{t}</span>' for t in card["best_for"])
                bad_html  = "".join(f'<span class="tg-bad">{t}</span>'  for t in card["not_ideal_for"])
                st.markdown(f"**Best for:** {best_html}", unsafe_allow_html=True)
                st.markdown(f"**Skip if:** {bad_html}", unsafe_allow_html=True)
                st.markdown(f"[Apply ↗]({card['ref_link']})")

    # ── Deep Dive ─────────────────────────────────────────────────────────────
    with dive_tab:
        choice = st.selectbox(
            "Choose a card",
            options=[c["id"] for c in _CARDS],
            format_func=lambda x: next(c["name"] for c in _CARDS if c["id"] == x),
            key="cc_dive_sel",
        )
        card = next(c for c in _CARDS if c["id"] == choice)
        _card_header(card)
        st.markdown(f"""
**Welcome Bonus:** {card['welcome_bonus']}
**Spend Requirement:** {card['welcome_spend']}
**Reward Rate:** {card['reward_rate']}
**Points:** {card['points_currency']}
""")
        best_html = "".join(f'<span class="tg-good">{t}</span>' for t in card["best_for"])
        bad_html  = "".join(f'<span class="tg-bad">{t}</span>'  for t in card["not_ideal_for"])
        st.markdown(f"**Best for:** {best_html}", unsafe_allow_html=True)
        st.markdown(f"**Skip if:** {bad_html}", unsafe_allow_html=True)
        st.markdown("---")
        for category in card["benefits"]:
            st.markdown(
                f'<div style="background:linear-gradient(90deg,#1e3a5f,#2d5986);color:#e8f4ff;'
                f'font-size:13px;font-weight:700;padding:5px 13px;border-radius:8px;'
                f'margin:10px 0 6px;">🏷️ {category}</div>',
                unsafe_allow_html=True,
            )
            _benefit_block(card, category)

    # ── Fine Print ────────────────────────────────────────────────────────────
    with fp_tab:
        st.markdown("#### ⚠️ Gotchas That Cost People Money")
        st.caption("These are the most common fine-print traps. Read before using your benefits.")
        for card in _CARDS:
            fp_items = [
                (cat, b["name"], b["value"], b["notes"])
                for cat, items in card["benefits"].items()
                for b in items
                if b.get("fp") and b.get("notes")
            ]
            if not fp_items:
                continue
            st.markdown(
                f'<div style="background:{card["color"]};color:{card["text_color"]};'
                f'border-radius:10px;padding:8px 14px;margin-top:10px;margin-bottom:4px;">'
                f'<span style="font-size:14px;font-weight:800;">{card["name"]}</span> '
                f'<span style="font-size:11px;opacity:.75;">— ${card["annual_fee"]}/yr</span></div>',
                unsafe_allow_html=True,
            )
            for cat, name, value, note in fp_items:
                st.markdown(
                    f'<div class="ben-row" style="border-left:4px solid #f59e0b;">'
                    f'<span class="ben-name">⚠ {name}</span>'
                    f'<span class="ben-val">{value}</span>'
                    f'<div class="ben-notes"><b>[{cat}]</b> {note}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── References ────────────────────────────────────────────────────────────
    with ref_tab:
        st.markdown("#### 🔗 Official Pages & Research Links")
        st.caption("Always apply at the official issuer page for the current offer. Third-party links are for research only.")
        _refs = [
            ("Amex Platinum — Official", "https://www.americanexpress.com/us/credit-cards/card/platinum/",
             "Current offer, benefit guide, select airline"),
            ("Chase Sapphire Reserve — Official", "https://creditcards.chase.com/rewards-credit-cards/sapphire/reserve",
             "Current bonus and full protections guide"),
            ("Capital One Venture X — Official", "https://capitalone.com/credit-cards/venture-x/",
             "Current offer, AU card details, lounge map"),
            ("Amex Gold — Official", "https://www.americanexpress.com/us/credit-cards/card/gold-card/",
             "Verify current dining credit merchant list (changes frequently)"),
            ("Chase Sapphire Preferred — Official", "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
             "Current bonus, 10% anniversary bonus terms"),
            ("The Points Guy — Card Comparisons", "https://thepointsguy.com/credit-cards/compare/",
             "Independent valuations, current offers, CPP table"),
            ("NerdWallet — Premium Travel Cards", "https://www.nerdwallet.com/best/credit-cards/premium-travel",
             "Side-by-side editor reviews"),
            ("Doctor of Credit — Fine Print Database", "https://www.doctorofcredit.com",
             "Deep data points, Amex offer tracking, fine print research"),
            ("Amex FHR vs THC Explainer", "https://thepointsguy.com/guide/amex-fine-hotels-resorts-hotel-collection/",
             "Critical: explains difference between Fine Hotels+Resorts and Hotel Collection"),
            ("Centurion Lounge Guest Policy (2024+)", "https://thepointsguy.com/news/amex-centurion-lounge-new-guest-policy/",
             "$50/guest unless $75k/yr spend — new policy details"),
            ("Amex Delta SkyClub Access (2025)", "https://thepointsguy.com/news/amex-delta-sky-club-access-changes/",
             "10 visit cap/yr unless $75k spend on Amex"),
            ("Capital One Lounge Locations", "https://www.capitalone.com/credit-cards/venture-x/lounge/",
             "Current C1 Lounge airports and hours"),
        ]
        for name, url, desc in _refs:
            st.markdown(f"**[{name}]({url})**  \n{desc}")
        st.markdown("---")
        st.caption("Data verified June 2026. Not financial advice. Credit card terms change — verify before relying on values shown.")

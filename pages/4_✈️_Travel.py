"""Travel — Points Optimizer · Deal Scanner · Hawaii 2026 Planner."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(page_title="AiPi360 · Travel", page_icon="✈️", layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css, inject_global_nav_css
require_auth(); check_maintenance(); check_page_access("travel")
inject_3d_tab_css(); inject_global_nav_css()
from components.metric_card import section_header

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
.partner-card{background:#fff;border-radius:12px;padding:14px;border:1px solid #e2e8f0;
  margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.partner-card:hover{box-shadow:0 4px 14px rgba(0,0,0,.1)}
.badge-great{background:#dcfce7;color:#166534;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-good {background:#dbeafe;color:#1d4ed8;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-fair {background:#fef9c3;color:#92400e;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-poor {background:#fee2e2;color:#b91c1c;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.hero-blue{background:linear-gradient(135deg,#1e3a5f,#0369a1,#0891b2);
  border-radius:16px;padding:26px 30px;color:#fff;margin-bottom:18px}
.hero-teal{background:linear-gradient(135deg,#0e7490,#0891b2,#06b6d4);
  border-radius:16px;padding:26px 30px;color:#fff;margin-bottom:18px}
.hero-blue h2,.hero-teal h2{font-size:21px;font-weight:800;margin:0 0 5px 0}
.hero-blue p,.hero-teal p{font-size:13px;opacity:.85;margin:0}
.result-row{display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;background:#fff;border-radius:10px;border:1px solid #e2e8f0;margin-bottom:8px}
.result-prog{font-size:13px;font-weight:700;color:#0f172a}
.result-meta{font-size:11px;color:#64748b}
.result-pts{font-size:14px;font-weight:800;color:#0369a1;text-align:right}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

section_header("✈️", "Travel", "Points optimizer · Deal scanner · Hawaii 2026 planner")

# ── Helpers ───────────────────────────────────────────────────────────────────
def cpp_badge(cpp):
    if cpp is None: return ""
    if cpp >= 2.0: return '<span class="badge-great">⭐ GREAT ≥2¢</span>'
    if cpp >= 1.5: return '<span class="badge-good">✅ GOOD ≥1.5¢</span>'
    if cpp >= 1.0: return '<span class="badge-fair">⚠️ FAIR ≥1¢</span>'
    return '<span class="badge-poor">❌ POOR <1¢</span>'

def cpp_color(cpp):
    if cpp is None: return "#94a3b8"
    if cpp >= 2.0: return "#16a34a"
    if cpp >= 1.5: return "#2563eb"
    if cpp >= 1.0: return "#d97706"
    return "#dc2626"

# ── Partner Data ──────────────────────────────────────────────────────────────
C1_PARTNERS = [
    {"prog":"Air Canada Aeroplan",       "code":"AC","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":2.0,"hawaii_ow":12500,"hawaii_fees":30,"domestic_ow":None,
     "link":"https://www.aircanada.com/aeroplan",
     "note":"Books UA, Air Canada. Best Hawaii value for C1 VX."},
    {"prog":"Turkish Miles & Smiles",    "code":"TK","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":2.5,"hawaii_ow":12500,"hawaii_fees":10,"domestic_ow":7500,
     "link":"https://www.turkishairlines.com/en-us/miles-and-smiles/",
     "note":"Lowest fees. Domestic US on UA 7,500 mi OW. Hawaii 12,500."},
    {"prog":"Avianca LifeMiles",         "code":"AV","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":2.2,"hawaii_ow":17500,"hawaii_fees":5,"domestic_ow":10000,
     "link":"https://www.lifemiles.com",
     "note":"No fuel surcharges. Books UA flights. Good domestic value."},
    {"prog":"Air France/KLM Flying Blue","code":"AF","alliance":"SkyTeam","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":20000,"hawaii_fees":30,"domestic_ow":None,
     "link":"https://flyingblue.com",
     "note":"Monthly Flash Sales. Dynamic pricing — check often."},
    {"prog":"British Airways Avios",     "code":"BA","alliance":"Oneworld","ratio":1.0,
     "cpp_est":1.5,"hawaii_ow":17500,"hawaii_fees":20,"domestic_ow":7500,
     "link":"https://www.britishairways.com",
     "note":"Distance-based. AA short hops from 7,500 Avios OW."},
    {"prog":"Singapore KrisFlyer",       "code":"SQ","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":17500,"hawaii_fees":20,"domestic_ow":None,
     "link":"https://www.singaporeair.com",
     "note":"Good for Star Alliance premium cabins."},
    {"prog":"Emirates Skywards",         "code":"EK","alliance":"None","ratio":1.0,
     "cpp_est":1.4,"hawaii_ow":None,"hawaii_fees":None,"domestic_ow":None,
     "link":"https://www.emirates.com",
     "note":"High fees. Best for Emirates own flights only."},
    {"prog":"Etihad Guest",              "code":"EY","alliance":"None","ratio":1.0,
     "cpp_est":1.5,"hawaii_ow":17500,"hawaii_fees":10,"domestic_ow":None,
     "link":"https://www.etihad.com",
     "note":"Books American Airlines at Oneworld partner rates."},
]

CHASE_PARTNERS = [
    {"prog":"United MileagePlus",        "code":"UA","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":1.5,"hawaii_ow":12500,"hawaii_fees":35,"domestic_ow":12500,
     "link":"https://www.united.com/ual/en/us/mileageplus/",
     "note":"Direct Hawaii flights from most hubs. 12,500 mi saver OW."},
    {"prog":"Southwest Rapid Rewards",   "code":"WN","alliance":"None","ratio":1.0,
     "cpp_est":1.5,"hawaii_ow":13500,"hawaii_fees":5,"domestic_ow":7500,
     "link":"https://www.southwest.com/rapidrewards/",
     "note":"Flies to Hawaii! No change fees. Great group flexibility."},
    {"prog":"Air Canada Aeroplan",       "code":"AC","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":2.0,"hawaii_ow":12500,"hawaii_fees":30,"domestic_ow":None,
     "link":"https://www.aircanada.com/aeroplan",
     "note":"Best Hawaii value via Chase UR. 12,500 mi OW saver."},
    {"prog":"Air France/KLM Flying Blue","code":"AF","alliance":"SkyTeam","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":20000,"hawaii_fees":30,"domestic_ow":None,
     "link":"https://flyingblue.com",
     "note":"Flash Sales often include Hawaii. Watch monthly promos."},
    {"prog":"British Airways Avios",     "code":"BA","alliance":"Oneworld","ratio":1.0,
     "cpp_est":1.5,"hawaii_ow":17500,"hawaii_fees":20,"domestic_ow":7500,
     "link":"https://www.britishairways.com",
     "note":"Short AA hops < 650 mi from 7,500 Avios."},
    {"prog":"Iberia Avios",              "code":"IB","alliance":"Oneworld","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":17500,"hawaii_fees":10,"domestic_ow":None,
     "link":"https://www.iberia.com",
     "note":"Avios pool with BA but lower fuel surcharges."},
    {"prog":"Singapore KrisFlyer",       "code":"SQ","alliance":"Star Alliance","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":17500,"hawaii_fees":20,"domestic_ow":None,
     "link":"https://www.singaporeair.com",
     "note":"Good Star Alliance partner rates."},
    {"prog":"Virgin Atlantic",           "code":"VS","alliance":"None","ratio":1.0,
     "cpp_est":1.8,"hawaii_ow":None,"hawaii_fees":None,"domestic_ow":None,
     "link":"https://www.virginatlantic.com",
     "note":"Books Delta at distance-based rates. No fuel surcharges."},
    {"prog":"World of Hyatt",            "code":"HY","alliance":"Hotel","ratio":1.0,
     "cpp_est":2.5,"hawaii_ow":None,"hawaii_fees":None,"domestic_ow":None,
     "link":"https://world.hyatt.com",
     "note":"Best hotel value. Hawaii Hyatt resorts 15-28k pts/night."},
    {"prog":"Marriott Bonvoy",           "code":"MR","alliance":"Hotel","ratio":1.0,
     "cpp_est":0.8,"hawaii_ow":None,"hawaii_fees":None,"domestic_ow":None,
     "link":"https://www.marriott.com",
     "note":"Lower CPP. 60k → 25k airline miles with bonus."},
]

# ─────────────────────────────────────────────────────────────────────────────
tab_scanner, tab_hawaii, tab_partners, tab_dom, tab_intl, tab_hotels, tab_perks, tab_tips = st.tabs([
    "🎯 Points Optimizer", "🌺 Hawaii 2026", "🔗 Transfer Partners",
    "🛫 Domestic", "🌍 Int'l Flights", "🏨 Hotels", "🛋️ Lounge & Perks", "💡 Tips",
])

# ═══════════════════════════════════════ TAB 1 — POINTS OPTIMIZER ═══════════
with tab_scanner:
    st.markdown('<div class="hero-blue"><h2>🎯 Points Optimizer & Deal Scanner</h2>'
                '<p>Enter points balances + cash price → see which program gives best value</p></div>',
                unsafe_allow_html=True)

    # Points balances
    st.markdown("#### 💳 Your Points Balances")
    b1, b2, b3, b4 = st.columns(4)
    c1_bal    = b1.number_input("Capital One VX (pts)", 0, 10_000_000, st.session_state.get("c1_bal",150000), 5000, key="c1_bal")
    chase_bal = b2.number_input("Chase UR (pts)",        0, 10_000_000, st.session_state.get("chase_bal",120000), 5000, key="chase_bal")
    b3.metric("C1 Portal Value (1.85¢)", f"${c1_bal*0.0185:,.0f}")
    b4.metric("Chase CSR Value (1.5¢)",  f"${chase_bal*0.015:,.0f}")
    st.divider()

    # Flight details
    st.markdown("#### ✈️ Flight Details")
    fc1,fc2,fc3,fc4,fc5 = st.columns([2,2,1.5,1.2,1.5])
    origin  = fc1.text_input("From", "Dallas (DFW)", key="sc_org")
    dest    = fc2.text_input("To",   "Honolulu (HNL)", key="sc_dst")
    pax     = fc3.number_input("Travelers", 1, 20, 2, key="sc_pax")
    is_rt   = fc4.checkbox("Round Trip", True, key="sc_rt")
    cabin   = fc5.selectbox("Cabin", ["Economy","Premium Economy","Business","First"], key="sc_cab")
    cash_ow = st.number_input("💵 Cash price ONE-WAY per person ($) — from Google Flights",
                               0, 10000, 450, 10, key="sc_cash",
                               help="Look up on Google Flights, enter here")

    cabin_mult = {"Economy":1.0,"Premium Economy":1.6,"Business":3.5,"First":5.0}[cabin]
    cash_rt_pp = cash_ow * (2 if is_rt else 1)
    cash_total = cash_rt_pp * pax

    mc1,mc2,mc3 = st.columns(3)
    mc1.metric("Cash per person", f"${cash_rt_pp:,.0f}")
    mc2.metric(f"Cash for {pax} traveler{'s' if pax>1 else ''}", f"${cash_total:,.0f}")
    mc3.metric("Break-even CPP threshold", f"{cash_rt_pp/(cash_rt_pp/0.015):,.1f}¢" if cash_rt_pp else "—")

    if st.button("🔍  Find Best Redemption", type="primary", key="sc_go"):
        st.session_state["sc_done"] = True

    if st.session_state.get("sc_done"):
        is_hi = any(k in dest.upper() for k in ["HAWAII","HNL","OGG","KOA","LIH","ITO"])
        award_key = "hawaii_ow" if is_hi else "domestic_ow"

        results = []
        for plist, card_label, card_bal in [
            (C1_PARTNERS,    "💜 Capital One VX", c1_bal),
            (CHASE_PARTNERS, "🔵 Chase UR",       chase_bal),
        ]:
            for p in plist:
                if p.get("alliance") == "Hotel": continue
                base = p.get(award_key)
                if not base: continue
                m_ow = int(base * cabin_mult)
                m_pp = m_ow * (2 if is_rt else 1)
                f_pp = (p.get("hawaii_fees") or 0) * (2 if is_rt else 1) if is_hi else 5
                m_trip = m_pp * pax
                f_trip = f_pp * pax
                cpp = round((cash_rt_pp - f_pp) / m_pp * 100, 2) if m_pp else None
                results.append({"card":card_label,"prog":p["prog"],"code":p["code"],
                    "m_pp":m_pp,"f_pp":f_pp,"m_trip":m_trip,"f_trip":f_trip,
                    "cpp":cpp,"can_afford":card_bal>=m_trip,
                    "link":p["link"],"note":p["note"]})

        # Portal options
        for label, bal, rate, link in [
            ("💜 Capital One VX", c1_bal,    1.85, "https://travel.capitalone.com"),
            ("🔵 Chase CSR",      chase_bal, 1.50, "https://ultimaterewards.com"),
        ]:
            m_pp  = int(cash_rt_pp / (rate/100)) if cash_rt_pp else 0
            results.append({"card":label,"prog":f"{label.split()[1]} Travel Portal ({rate}¢/pt)",
                "code":"PORTAL","m_pp":m_pp,"f_pp":0,"m_trip":m_pp*pax,"f_trip":0,
                "cpp":rate,"can_afford":bal>=m_pp*pax,
                "link":link,"note":f"Redeem directly. No transfer needed. {rate}¢/pt."})

        results = [r for r in results if r["cpp"] is not None]
        results.sort(key=lambda x: x["cpp"], reverse=True)

        st.markdown(f"#### 🏆 Results: {origin} → {dest} · {pax} pax · {'RT' if is_rt else 'OW'} · {cabin}")
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        for i, r in enumerate(results[:10]):
            afford = "✅ Affordable" if r["can_afford"] else f"⚠️ Need {r['m_trip']:,} pts"
            st.markdown(f"""
<div class="result-row">
  <div style="font-size:22px;width:34px">{medals[i] if i<len(medals) else str(i+1)}</div>
  <div style="flex:1;padding:0 12px">
    <div class="result-prog">{r['card']} → {r['prog']}</div>
    <div class="result-meta">{afford} · {r['note'][:65]}…</div>
  </div>
  <div style="text-align:right;min-width:170px">
    <div class="result-pts">{r['m_pp']:,} pts/person</div>
    <div class="result-meta">{r['m_trip']:,} pts total · +${r['f_trip']} fees</div>
    <div style="margin-top:4px">{cpp_badge(r['cpp'])}</div>
  </div>
  <div style="margin-left:14px;min-width:55px;text-align:center">
    <div style="font-size:19px;font-weight:800;color:{cpp_color(r['cpp'])}">{r['cpp']:.1f}¢</div>
    <div style="font-size:10px;color:#94a3b8">per pt</div>
  </div>
</div>""", unsafe_allow_html=True)

        best = results[0]
        st.success(f"**Best:** {best['prog']} · **{best['cpp']:.2f}¢/pt** · "
                   f"{best['m_trip']:,} pts for {pax} people  \n💡 {best['note']}")

        # Coverage check
        st.markdown("#### 💳 Points Coverage")
        pc1, pc2 = st.columns(2)
        c1_min  = min((r["m_trip"] for r in results if "Capital One" in r["card"]), default=0)
        ch_min  = min((r["m_trip"] for r in results if "Chase" in r["card"]), default=0)
        with pc1:
            p = min(c1_bal/c1_min*100, 100) if c1_min else 100
            st.metric("Capital One VX", f"{c1_bal:,} pts")
            st.progress(p/100)
            st.caption(f"Best option needs {c1_min:,} pts · {'✅ Sufficient' if c1_bal>=c1_min else f'⚠️ Short {c1_min-c1_bal:,}'}")
        with pc2:
            p2 = min(chase_bal/ch_min*100, 100) if ch_min else 100
            st.metric("Chase UR", f"{chase_bal:,} pts")
            st.progress(p2/100)
            st.caption(f"Best option needs {ch_min:,} pts · {'✅ Sufficient' if chase_bal>=ch_min else f'⚠️ Short {ch_min-chase_bal:,}'}")
    else:
        st.info("👆 Fill in flight details above and click **Find Best Redemption**")

# ═══════════════════════════════════════ TAB 2 — HAWAII 2026 ════════════════
with tab_hawaii:
    st.markdown('<div class="hero-teal"><h2>🌺 Hawaii 2026 — Group Flight Planner</h2>'
                '<p>December 2026 · 7–8 Families · 15–18 Travelers · Maximize Capital One VX + Chase UR</p></div>',
                unsafe_allow_html=True)

    days_left = (datetime(2026,12,20) - datetime.now()).days
    h1,h2,h3,h4 = st.columns(4)
    h1.metric("⏳ Days to Go", f"{days_left:,}")
    h2.metric("👨‍👩‍👧 Families", "7–8")
    h3.metric("👥 Travelers", "15–18")
    h4.metric("🏝️ Islands", "Maui + Kauai")
    st.divider()

    gc1,gc2,gc3 = st.columns(3)
    num_pax  = gc1.slider("Total travelers", 10, 20, 17)
    origin_h = gc2.selectbox("Departing from", ["Dallas (DFW/DAL)","Houston (IAH/HOU)","Los Angeles (LAX)","Other"])
    cabin_h  = gc3.selectbox("Cabin", ["Economy","Business"])
    c_mult   = 1.0 if cabin_h == "Economy" else 3.5

    st.markdown("#### 🏆 Best Programs for Your Hawaii Group")
    hawaii_options = [
        ("🥇","Both",  "Air Canada Aeroplan → UA/AC",       int(12500*c_mult),30, 2.0,
         "Best value. Both C1 VX & Chase UR transfer 1:1. Low fees $30/pp.",
         "https://www.aircanada.com/aeroplan"),
        ("🥈","C1 VX", "Turkish Miles & Smiles → United",   int(12500*c_mult),10, 2.5,
         "Lowest fees ($10 pp). Books UA metal. C1→TK transfer 1:1.",
         "https://www.turkishairlines.com/en-us/miles-and-smiles/"),
        ("🥉","Chase", "United MileagePlus → United",        int(12500*c_mult),70, 1.5,
         "Straightforward. 12,500 mi OW saver. Best award availability.",
         "https://www.united.com/ual/en/us/mileageplus/"),
        ("4️⃣","Chase", "Southwest Rapid Rewards",            int(13500*c_mult),5,  1.5,
         "No change fees. Flies HNL/OGG from DAL/HOU. Great for group flexibility.",
         "https://www.southwest.com"),
        ("5️⃣","C1 VX", "Capital One Travel Portal (1.85¢)", int(450/0.0185),  0,  1.85,
         "No transfer needed. Book any airline. 1.85¢ per point.",
         "https://travel.capitalone.com"),
        ("6️⃣","Chase", "Chase Travel Portal (1.5¢/CSR)",    int(450/0.015),   0,  1.50,
         "Easy. No transfer. 1.5¢/pt in portal. Less value than transfers.",
         "https://ultimaterewards.com"),
    ]

    for medal, card, prog, m_ow, f_ow, cpp, note, link in hawaii_options:
        m_rt    = m_ow * 2
        f_rt    = f_ow * 2
        g_pts   = m_rt * num_pax
        g_fees  = f_rt * num_pax
        equiv   = g_pts * (cpp/100)
        ro1,ro2,ro3,ro4 = st.columns([1,3,2,2])
        ro1.markdown(f"<div style='font-size:26px;text-align:center;padding-top:8px'>{medal}</div>",unsafe_allow_html=True)
        with ro2:
            st.markdown(f"**{prog}**")
            st.caption(f"Card: {card} · {note}")
        with ro3:
            st.metric("Per person (RT)", f"{m_rt:,} pts")
            st.caption(f"+${f_rt} fees/person")
        with ro4:
            st.metric(f"Group ({num_pax} pax)", f"{g_pts:,} pts")
            st.caption(f"+${g_fees:,} fees · ≈${equiv:,.0f} value")
        st.markdown(f"<a href='{link}' target='_blank' style='font-size:11px;color:#0369a1'>🔗 Check availability ↗</a>",unsafe_allow_html=True)
        st.divider()

    # Sufficiency
    c1b  = st.session_state.get("c1_bal",150000)
    chb  = st.session_state.get("chase_bal",120000)
    comb = c1b + chb
    need = int(12500 * c_mult) * 2 * num_pax  # Aeroplan benchmark
    st.markdown("#### 💳 Can Your Cards Cover the Whole Group?")
    sg1,sg2,sg3 = st.columns(3)
    sg1.metric("Combined Points",          f"{comb:,}")
    sg2.metric("Group RT via Aeroplan",    f"{need:,}", delta=f"{comb-need:+,}")
    sg3.metric("Coverage %", f"{min(comb/need*100,100):.0f}%")
    st.progress(min(comb/need,1.0))
    if comb >= need:
        st.success(f"✅ Your combined {comb:,} pts cover economy RT for all {num_pax} via Aeroplan/UA!")
    else:
        st.warning(f"⚠️ {need-comb:,} pts short. Earn more, use fewer travelers, or mix cash+points.")

    # Timeline
    st.markdown("#### 📅 Booking Timeline")
    for when, ico, action in [
        ("Now–Jan 2026",  "🎯", "Decide islands, budget, earmark points."),
        ("Feb–Mar 2026",  "✈️", "Book flights — 9 months out = best award space. Set award alerts."),
        ("Mar–Apr 2026",  "🏨", "Book hotels/VRBO — December fills FAST."),
        ("May–Jun 2026",  "🚗", "Book 3–4 rental cars. December peak — vehicles sell out."),
        ("Sep–Oct 2026",  "🎟️", "Book luau, whale watch, helicopter tours."),
        ("Nov 2026",      "📋", "Confirm everything. Purchase travel insurance."),
    ]:
        st.markdown(f"**{ico} {when}** — {action}")

# ═══════════════════════════════════════ TAB 3 — TRANSFER PARTNERS ══════════
with tab_partners:
    st.markdown("### 🔗 Transfer Partner Reference Guide")
    show = st.radio("Show:", ["Both Cards","Capital One VX Only","Chase UR Only"], horizontal=True)

    def render_partners(plist, label, color):
        st.markdown(f"<div style='font-weight:700;font-size:14px;color:{color};margin:12px 0 8px'>{label}</div>",
                    unsafe_allow_html=True)
        airline_p = [p for p in plist if p.get("alliance") not in ("Hotel",)]
        hotel_p   = [p for p in plist if p.get("alliance") == "Hotel"]
        cols = st.columns(3)
        for i, p in enumerate(airline_p):
            with cols[i % 3]:
                cpp = p["cpp_est"]
                ha  = f"Hawaii: {p['hawaii_ow']:,} mi OW" if p.get("hawaii_ow") else "Hawaii: varies"
                st.markdown(f"""
<div class="partner-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="font-weight:700;font-size:13px">{p['prog']}</div>
      <div style="font-size:11px;color:#64748b">{p['alliance']} · {p['code']} · {p['ratio']}:1</div>
    </div>
    <div style="font-size:17px;font-weight:800;color:{cpp_color(cpp)}">{cpp:.1f}¢</div>
  </div>
  <div style="font-size:11px;color:#0369a1;margin:5px 0">{ha}</div>
  <div style="font-size:11px;color:#64748b">{p['note'][:72]}</div>
  <div style="margin-top:6px">{cpp_badge(cpp)}</div>
  <div style="margin-top:6px"><a href="{p['link']}" target="_blank" style="font-size:11px;color:#0369a1">🔗 Portal ↗</a></div>
</div>""", unsafe_allow_html=True)
        if hotel_p:
            st.markdown("**Hotel Partners**")
            hc = st.columns(3)
            for i, p in enumerate(hotel_p):
                with hc[i%3]:
                    st.markdown(f"""
<div class="partner-card">
  <div style="font-weight:700;font-size:13px">{p['prog']}</div>
  <div style="font-size:11px;color:#64748b">{p['ratio']}:1 · Est {p['cpp_est']:.1f}¢/pt</div>
  <div style="font-size:11px;color:#64748b;margin-top:4px">{p['note'][:72]}</div>
  <div style="margin-top:6px">{cpp_badge(p['cpp_est'])}</div>
</div>""", unsafe_allow_html=True)

    if show in ("Both Cards","Capital One VX Only"):
        render_partners(C1_PARTNERS, "💜 Capital One Venture X", "#7c3aed")
    if show in ("Both Cards","Chase UR Only"):
        render_partners(CHASE_PARTNERS, "🔵 Chase Sapphire (Ultimate Rewards)", "#1d4ed8")

    st.divider()
    st.markdown("""
#### ⚡ Key Transfer Rules
- **Never transfer without confirmed award space** — points are non-refundable
- **Aeroplan** (both cards): instant transfer · 12,500 mi Hawaii OW economy saver
- **Turkish** (C1 VX only): 7,500 mi domestic US on United · 2–3 day transfer time
- **Southwest** (Chase only): no change fees · flies Hawaii from DAL/HOU
- **Flying Blue**: monthly Flash Sales — 25–50% off selected routes
- **Check award space**: use [Seats.aero](https://seats.aero) or [Point.me](https://point.me) before transferring
""")

# ═══════════════════════════════════════ TAB 4 — DOMESTIC ════════════════════
with tab_dom:
    st.markdown("### 🛫 Domestic Travel — Best Points Value")
    st.markdown("""
<div style="background:#eff6ff;border-radius:12px;padding:18px;border:1px solid #bfdbfe;margin-bottom:16px">

| Program | Miles OW (Econ) | Cards | Sweet Spot |
|---|---|---|---|
| **Turkish Miles → UA** | 7,500 | C1 VX | Best domestic US rate. Very low fees. |
| **BA Avios → AA** | 7,500 | Chase UR | Distance-based. Short hops < 650 mi. |
| **Southwest** | 7,500–15,000 | Chase UR | No change fees. Great flexibility. |
| **United** | 12,500 | Chase UR | Plenty of saver space. Straightforward. |
| **Avianca → UA** | 10,000 | C1 VX | No fuel surcharges on UA flights. |
| **C1 Travel Portal** | ~13,500 @ 1.85¢ | C1 VX | No transfer. Any airline. Simple. |

</div>""", unsafe_allow_html=True)

    st.markdown("#### 🔢 Quick Domestic Calculator")
    dc1,dc2,dc3 = st.columns(3)
    d_cash = dc1.number_input("Cash price OW ($)", 0, 5000, 250, key="d_cash")
    d_prog = dc2.selectbox("Program", ["Turkish M&S → UA (C1 VX)","Southwest (Chase)","United (Chase)",
                                        "BA Avios → AA (Chase)","Avianca → UA (C1 VX)",
                                        "C1 Travel Portal (1.85¢)","Chase Portal (1.5¢)"], key="d_prog")
    d_pax  = dc3.number_input("Passengers", 1, 20, 1, key="d_pax")

    rates = {"Turkish M&S → UA (C1 VX)":7500,"Southwest (Chase)":10000,"United (Chase)":12500,
             "BA Avios → AA (Chase)":7500,"Avianca → UA (C1 VX)":10000,
             "C1 Travel Portal (1.85¢)":int(d_cash/0.0185) if d_cash else 0,
             "Chase Portal (1.5¢)":int(d_cash/0.015) if d_cash else 0}
    m_ow   = rates[d_prog]
    m_trip = m_ow * d_pax
    cpp_d  = round((d_cash / m_ow * 100), 2) if m_ow else 0
    dr1,dr2,dr3,dr4 = st.columns(4)
    dr1.metric("Miles per person", f"{m_ow:,}")
    dr2.metric(f"Miles for {d_pax}", f"{m_trip:,}")
    dr3.metric("CPP", f"{cpp_d:.2f}¢")
    dr4.markdown(cpp_badge(cpp_d), unsafe_allow_html=True)

# ═══════════════════════════════════════ TAB 5 — INTERNATIONAL ═══════════════
with tab_intl:
    st.markdown("### 🌍 International Travel — Points Maximization")
    st.markdown("""
<div style="background:#f0fdf4;border-radius:12px;padding:18px;border:1px solid #bbf7d0;margin-bottom:16px">

| Destination | Best Program | Miles RT (Econ) | Cards | Notes |
|---|---|---|---|---|
| **Europe Economy** | Flying Blue | 40,000–50,000 | Both | Watch Flash Sales |
| **Europe Business** | Turkish / Aeroplan | 50,000–70,000 | Both | Turkish → Lufthansa rates |
| **Asia Economy** | Singapore KrisFlyer | 40,000–55,000 | Both | Book months ahead |
| **Japan Business** | ANA/JAL via Chase | 60,000–85,000 | Chase | Among best biz values |
| **Caribbean** | United / Southwest | 20,000–35,000 | Chase | Easy redemptions |
| **South America** | Avianca LifeMiles | 30,000–45,000 | C1 VX | Consistent pricing |
| **Middle East** | Emirates Skywards | 35,000–60,000 | Both | High fees |

</div>""", unsafe_allow_html=True)
    st.info("💡 **International business class secret:** Transfer C1 VX → Turkish Miles & Smiles to book **Star Alliance business class** (Lufthansa, Swiss, United) at Zonal rates — often 60–80% fewer miles than booking direct.")

# ═══════════════════════════════════════ TAB 6 — HOTELS ══════════════════════
with tab_hotels:
    st.markdown("### 🏨 Hotel Points — Best Programs")
    st.markdown("""
| Program | Transfer From | CPP | Sweet Spot |
|---|---|---|---|
| **World of Hyatt** | Chase UR (1:1) | ~2.5¢ | Cat 1–7 properties. Hawaii: Hyatt Regency Maui 20k/night |
| **Marriott Bonvoy** | Chase UR (1:1) | ~0.8¢ | 60k Marriott → 25k airline miles (bonus) |
| **IHG One Rewards** | Chase UR (1:1) | ~0.5¢ | 4th night free redemptions only |
| **Wyndham Rewards** | C1 VX (1:1) | ~0.8¢ | All-inclusive resorts 30k/night flat |
| **Choice Privileges** | C1 VX (1:1) | ~0.6¢ | Limited premium properties |

**Hawaii Hyatt Sweet Spots (via Chase UR):**
- 🌴 Andaz Maui at Wailea — ~28,000 pts/night (Category 6)
- 🌊 Hyatt Regency Maui — ~20,000 pts/night (Category 5)
- 🏖️ Grand Hyatt Kauai — ~20,000 pts/night (Category 5)
- 🌺 Andaz Kauai — ~25,000 pts/night (Category 6)
""")
    st.success("🏆 **Best hotel use of Chase UR:** Transfer to World of Hyatt. Hawaii Hyatt properties deliver ~2.5¢/pt consistently.")

# ═══════════════════════════════════════ TAB 7 — LOUNGE & PERKS ══════════════
with tab_perks:
    st.markdown("### 🛋️ Lounge Access & Card Perks")
    st.markdown("""
**💜 Capital One Venture X**
- ✅ **Capital One Lounges** (DFW T-D, DEN, IAD) — premium, free food/drinks
- ✅ **Plaza Premium + Priority Pass** — unlimited guests free
- ✅ $300/year travel credit (statement credit, automatic)
- ✅ Global Entry / TSA Pre — $100 credit every 4 years
- ✅ 10,000 bonus miles every anniversary year
- ✅ Earn: 10× hotels & cars, 5× flights, 2× everything (via portal)

**🔵 Chase Sapphire Reserve**
- ✅ **Priority Pass** — 1,400+ lounges worldwide, unlimited guests
- ✅ $300/year travel credit (auto-applied to any travel purchase)
- ✅ Global Entry / TSA Pre — $100 credit
- ✅ 1.5¢/pt in Chase Travel portal (vs 1¢ base)
- ✅ Earn: 10× hotels & cars, 5× flights, 3× dining & travel (via portal)

**DFW Lounge Access:**
| Terminal | Lounge | Access |
|---|---|---|
| Terminal D | **Capital One Lounge** | C1 Venture X ✅ |
| All Terminals | Priority Pass lounges | Both cards ✅ |
| Terminal A (AA) | Admirals Club | AA status/paid |
""")

# ═══════════════════════════════════════ TAB 8 — TIPS ════════════════════════
with tab_tips:
    st.markdown("### 💡 Points Strategy Tips")
    st.markdown("""
**Redemption value ladder (best → worst):**

| Rank | Strategy | CPP | Cards |
|---|---|---|---|
| 🥇 | Intl Business via Turkish/Aeroplan | 3–5¢ | Both |
| 🥈 | Hawaii flights via Aeroplan | ~2¢ | Both |
| 🥉 | Hyatt hotel redemptions | ~2.5¢ | Chase UR |
| 4️⃣ | Domestic via Turkish M&S → UA | 1.8–2¢ | C1 VX |
| 5️⃣ | Capital One Travel Portal | 1.85¢ | C1 VX |
| 6️⃣ | Chase Travel Portal (CSR) | 1.5¢ | Chase UR |
| 7️⃣ | Standard domestic saver awards | 1–1.5¢ | Either |
| ❌ | Gift cards / merchandise | 0.5–1¢ | Never |

**Earning tips:**
- Always book hotels/cars through the card's travel portal when paying cash (up to 10×)
- Both cards earn bonus on their own portal — use it for award-search then book direct
- C1 VX signup: 75,000 pts · Chase Sapphire Preferred: 60,000 pts

**Useful Tools:**
🔍 [Seats.aero](https://seats.aero) — award seat availability search
🗺️ [Point.me](https://point.me) — multi-program award search
✈️ [Google Flights](https://flights.google.com) — cash price benchmark
📊 [The Points Guy](https://thepointsguy.com/guide/monthly-valuations/) — monthly CPP valuations
""")

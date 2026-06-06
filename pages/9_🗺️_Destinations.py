"""Destinations — multi-year trip planning vault."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="AiPi360 · Destinations", page_icon="🗺️", layout="wide")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance
from components.styles import inject_3d_tab_css
require_auth()
check_maintenance()
inject_3d_tab_css()

from components.metric_card import section_header

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.trip-card {
    background: #fff; border-radius: 16px; padding: 0;
    border: 1px solid #e2e8f0; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
    cursor: pointer;
}
.trip-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.12); transform: translateY(-2px); }
.trip-card-hero {
    height: 120px; display: flex; align-items: center; justify-content: center;
    font-size: 56px; position: relative;
}
.trip-card-body { padding: 16px; }
.trip-card-title { font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 2px 0; }
.trip-card-sub { font-size: 12px; color: #64748b; margin: 0 0 10px 0; }
.status-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.03em;
}
.status-Planning   { background: #dbeafe; color: #1d4ed8; }
.status-Researching{ background: #fef9c3; color: #92400e; }
.status-Booked     { background: #dcfce7; color: #166534; }
.status-Completed  { background: #f1f5f9; color: #475569; }
.status-Wishlist   { background: #f3e8ff; color: #7c3aed; }
.tag-pill {
    display: inline-block; background: #f1f5f9; color: #475569;
    border-radius: 6px; padding: 2px 8px; font-size: 10px; font-weight: 600;
    margin: 2px 2px 0 0;
}
.vault-stats {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    border-radius: 16px; padding: 20px 28px; margin-bottom: 24px; color: #fff;
}
.stat-num { font-size: 28px; font-weight: 800; }
.stat-lbl { font-size: 11px; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.08em; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/4_✈️_Travel.py", label="✈️ Points & Deals", use_container_width=True)

section_header("🗺️", "Destinations", "Multi-year trip planning vault for the family")

# ── Trip Data ──────────────────────────────────────────────────────────────────
TRIPS = [
    {
        "id": "hawaii_2026",
        "name": "Hawaii 🌺",
        "emoji": "🌺",
        "year": 2026, "month": "December",
        "status": "Planning",
        "families": "7–8", "travelers": "15–18",
        "budget": "Moderate–Premium",
        "islands": "Maui · Kauai · Big Island",
        "tags": ["Group", "Family", "Beach", "Nature", "Food"],
        "color": "#0891b2",
        "hero_bg": "linear-gradient(135deg,#0891b2,#0e7490,#164e63)",
        "has_detail": True,
        "detail_file": "travel/hawaii_2026.html",
        "note": "December 2026 · 7–8 families · 15–18 travelers",
    },
    {
        "id": "japan_2027",
        "name": "Japan 🗾",
        "emoji": "🗾",
        "year": 2027, "month": "TBD",
        "status": "Wishlist",
        "families": "TBD", "travelers": "TBD",
        "budget": "TBD",
        "islands": "",
        "tags": ["Culture", "Food", "Cities", "Nature"],
        "color": "#dc2626",
        "hero_bg": "linear-gradient(135deg,#dc2626,#991b1b,#450a0a)",
        "has_detail": False,
        "note": "Cherry blossom or fall foliage season",
    },
    {
        "id": "europe_2027",
        "name": "Europe 🏰",
        "emoji": "🏰",
        "year": 2027, "month": "TBD",
        "status": "Wishlist",
        "families": "TBD", "travelers": "TBD",
        "budget": "TBD",
        "islands": "",
        "tags": ["History", "Culture", "Food", "Art"],
        "color": "#7c3aed",
        "hero_bg": "linear-gradient(135deg,#7c3aed,#5b21b6,#2e1065)",
        "has_detail": False,
        "note": "Italy · France · Spain — TBD",
    },
    {
        "id": "costa_rica_2026",
        "name": "Costa Rica 🌴",
        "emoji": "🌴",
        "year": 2026, "month": "TBD",
        "status": "Researching",
        "families": "TBD", "travelers": "TBD",
        "budget": "Moderate",
        "islands": "",
        "tags": ["Adventure", "Nature", "Wildlife", "Beach"],
        "color": "#16a34a",
        "hero_bg": "linear-gradient(135deg,#16a34a,#15803d,#14532d)",
        "has_detail": False,
        "note": "Rainforest + beach combo",
    },
]

# ── Summary Stats ──────────────────────────────────────────────────────────────
planned   = sum(1 for t in TRIPS if t["status"] in ("Planning","Researching","Booked"))
wishlist  = sum(1 for t in TRIPS if t["status"] == "Wishlist")
completed = sum(1 for t in TRIPS if t["status"] == "Completed")
years     = sorted(set(t["year"] for t in TRIPS))

st.markdown(f"""
<div class="vault-stats">
  <div style="display:flex;gap:48px;align-items:center">
    <div>
      <div class="stat-num">{len(TRIPS)}</div>
      <div class="stat-lbl">Destinations</div>
    </div>
    <div>
      <div class="stat-num">{planned}</div>
      <div class="stat-lbl">In Planning</div>
    </div>
    <div>
      <div class="stat-num">{wishlist}</div>
      <div class="stat-lbl">Wishlist</div>
    </div>
    <div>
      <div class="stat-num">{completed}</div>
      <div class="stat-lbl">Completed</div>
    </div>
    <div style="margin-left:auto;text-align:right">
      <div style="font-size:13px;opacity:0.8">Planning horizons</div>
      <div style="font-size:20px;font-weight:700">{" · ".join(str(y) for y in years)}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Trip Vault Grid ────────────────────────────────────────────────────────────
st.markdown("### 🗃️ Trip Vault")

cols = st.columns(4)
for i, trip in enumerate(TRIPS):
    with cols[i % 4]:
        tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in trip["tags"])
        st.markdown(f"""
<div class="trip-card">
  <div class="trip-card-hero" style="background:{trip['hero_bg']}">
    <span>{trip['emoji']}</span>
  </div>
  <div class="trip-card-body">
    <div class="trip-card-title">{trip['name']}</div>
    <div class="trip-card-sub">{trip['month']} {trip['year']}</div>
    <span class="status-badge status-{trip['status']}">{trip['status']}</span>
    <div style="margin-top:8px">{tags_html}</div>
    <div style="margin-top:10px;font-size:11px;color:#64748b">{trip['note']}</div>
  </div>
</div>
""", unsafe_allow_html=True)
        if trip["has_detail"]:
            if st.button(f"📋 Open {trip['name'].split()[0]} Plan", key=f"btn_{trip['id']}", use_container_width=True):
                st.session_state["active_destination"] = trip["id"]
        elif trip["status"] == "Wishlist":
            st.button("➕ Start Planning", key=f"btn_{trip['id']}", use_container_width=True, disabled=True)
        else:
            st.button("🔜 Detail Coming Soon", key=f"btn_{trip['id']}", use_container_width=True, disabled=True)

# ── Destination Detail Panel ───────────────────────────────────────────────────
active = st.session_state.get("active_destination")

if active:
    trip_map = {t["id"]: t for t in TRIPS}
    trip = trip_map.get(active)
    if trip and trip.get("has_detail") and trip.get("detail_file"):
        st.markdown("---")
        st.markdown(f"### {trip['emoji']} {trip['name']} — Full Planning Guide")
        col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
        col_meta1.metric("Target Date", f"{trip['month']} {trip['year']}")
        col_meta2.metric("Families", trip["families"])
        col_meta3.metric("Travelers", trip["travelers"])
        col_meta4.metric("Budget", trip["budget"])

        html_path = Path(__file__).parent.parent / trip["detail_file"]
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            st.components.v1.html(html_content, height=5800, scrolling=True)
        else:
            st.warning(f"Detail file not found: {html_path}")

        if st.button("✖ Close Detail", key="close_detail"):
            del st.session_state["active_destination"]
            st.rerun()

# ── Add Destination ────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("➕ Add a New Destination to the Vault"):
    c1, c2, c3 = st.columns(3)
    dest_name = c1.text_input("Destination Name")
    dest_year = c2.number_input("Target Year", min_value=2025, max_value=2035, value=2027)
    dest_status = c3.selectbox("Status", ["Wishlist", "Researching", "Planning", "Booked"])
    dest_note = st.text_area("Notes / Ideas", height=80)
    if st.button("💾 Save to Vault"):
        st.success(f"✅ {dest_name} ({dest_year}) added to vault! (Connect Google Sheets to persist)")

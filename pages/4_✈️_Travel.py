"""Travel — best deals on flights, hotels & points travel."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
st.set_page_config(page_title="AiPi360 · Travel", page_icon="✈️", layout="wide")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css
require_auth()
check_maintenance()
check_page_access("travel")
inject_3d_tab_css()

from components.metric_card import section_header, coming_soon

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

section_header("✈️", "Travel", "Best points deals on flights, hotels & more")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛫 Domestic Flights", "🌍 Int'l Flights", "🏨 Hotels",
    "🛋️ Lounge & Perks", "💡 Tips & Deals"
])

with tab1:
    st.markdown("#### 🛫 Domestic Travel — Best Points Value")
    st.markdown("""
<div style="background:#eff6ff;border-radius:12px;padding:20px;border:1px solid #bfdbfe;margin-bottom:16px;">

**Top domestic sweet spots:**
| Route Type | Best Points Program | Typical Cost |
|-----------|-------------------|--------------|
| Short-haul (< 500mi) | Southwest / Delta Skymiles | 5,000-10,000 pts |
| Medium-haul | United / AA | 12,500-25,000 pts |
| Long-haul domestic | Alaska / American | 20,000-30,000 pts |
| Last-minute | Southwest (refundable) | Flexible |

</div>""", unsafe_allow_html=True)
    coming_soon("Dynamic domestic deal scanner — nightly GitHub Actions job")

with tab2:
    st.markdown("#### 🌍 International Travel — Points Maximization")
    st.markdown("""
<div style="background:#f0fdf4;border-radius:12px;padding:20px;border:1px solid #bbf7d0;margin-bottom:16px;">

**Best international transfer partners:**
| Destination | Program | Points Needed (RT/person) |
|------------|---------|--------------------------|
| Europe (Business) | Air France / Turkish | 50,000-70,000 |
| Asia (Business) | ANA / JAL via Chase | 55,000-85,000 |
| Caribbean | AA / JetBlue | 20,000-35,000 |
| South America | Avianca LifeMiles | 30,000-45,000 |

</div>""", unsafe_allow_html=True)
    coming_soon("International deal alerts — set destinations and get notified on award availability")

with tab3:
    coming_soon("Hotel points deals — Marriott, Hilton, Hyatt sweet spots tracker")

with tab4:
    st.markdown("#### 🛋️ Lounge Access & Premium Perks")
    st.markdown("""
**Maximize card perks when traveling:**
- ✅ Always access lounges — saves $50+ in food/drinks per visit
- ✅ Use travel credits before year-end (Amex $200, CSR $300)
- ✅ Clear / TSA Pre via card benefit
- ✅ Global Entry credit ($100) — renew every 5 years
- ✅ Checked bag free with airline co-brand card
""")

with tab5:
    st.markdown("#### 💡 Travel Tips & Best Practices")
    st.markdown("""
**Points redemption hierarchy (best to worst value):**
1. 🥇 Business/First class international transfers (~2+ cpp)
2. 🥈 Transfer to hotel for premium properties (Hyatt > Hilton > Marriott)
3. 🥉 Domestic premium cabin upgrades
4. 💵 Pay yourself back (if card offers > 1.25 cpp)
5. ❌ Gift cards / merchandise (worst value)

**Cash transfers & useful credits:**
- Amex Platinum: $200 airline fee, $200 hotel, $240 digital, $200 Uber
- Chase Sapphire Reserve: $300 travel, $5/month DoorDash
- Capital One Venture X: $300 travel portal, $100 experience credit
""")
    coming_soon("AI-powered itinerary builder using your points balances")

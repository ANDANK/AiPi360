"""
Premium Credit Card Comparison — AiPi360
Compares top 5 premium cards across all benefit categories with fine-print callouts.
Data last verified: June 2026. Links to official card pages for live updates.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

_authenticated = st.session_state.get("authenticated", False)
st.set_page_config(
    page_title="AiPi360 · Card Compare",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded" if _authenticated else "collapsed",
)

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css, inject_global_nav_css
require_auth()
check_maintenance()
check_page_access("card_compare")
inject_3d_tab_css()
inject_global_nav_css()

# ─────────────────────────────────────────────────────────────────────────────
#  CARD DATA  (update values here when issuers change terms)
# ─────────────────────────────────────────────────────────────────────────────

CARDS = [
    # ── Amex Platinum ────────────────────────────────────────────────────────
    {
        "id": "amex_plat",
        "name": "Amex Platinum",
        "issuer": "American Express",
        "network": "Amex",
        "color": "#B8A06A",
        "text_color": "#2c1a00",
        "annual_fee": 695,
        "welcome_bonus": "80,000–175,000 MR pts",
        "welcome_spend": "$8,000 in 6 months",
        "reward_rate": "5x flights (direct/Amex Travel), 5x hotels (Amex Travel), 1x all else",
        "points_currency": "Membership Rewards",
        "cpp_estimate": "1.8–2.1¢",
        "ref_link": "https://www.americanexpress.com/us/credit-cards/card/platinum/",
        "benefits": {
            "Travel Credits": [
                {"name": "$200 Airline Fee Credit", "value": "$200/yr", "notes": "Select ONE airline at enrollment. Covers incidental fees only — NOT ticket purchases. Must re-select airline each Jan 1.", "fine_print": True},
                {"name": "$200 Uber Cash", "value": "$200/yr", "notes": "Loaded as $15/month + $35 in Dec. Must add Amex Plat as payment in Uber app. Uber Eats counts. Does NOT roll over.", "fine_print": True},
                {"name": "$200 Hotel Credit", "value": "$200/yr", "notes": "Valid ONLY at The Hotel Collection (2-night min stay) and Fine Hotels + Resorts via Amex Travel. NOT usable at hotel.com directly.", "fine_print": True},
                {"name": "$189 CLEAR Plus Credit", "value": "$189/yr", "notes": "Reimburses CLEAR Plus membership. Family plan not covered — only primary cardholder."},
                {"name": "$155 Walmart+ Credit", "value": "$155/yr", "notes": "Covers Walmart+ membership (~$12.95/mo). Must pay monthly with Amex Plat — annual prepay does NOT qualify.", "fine_print": True},
                {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "notes": "Once every 4 years (GE) or 4.5 years (TSA Pre). Can pay for another person's fee.", "fine_print": True},
                {"name": "Centurion Lounge Access", "value": "Unlimited", "notes": "2 free guests. Must spend $75k+ on card in prior year OR have no guests for free access from 2024 policy update. Guests $50 each after.", "fine_print": True},
                {"name": "Priority Pass Select", "value": "Unlimited", "notes": "Unlimited visits + 2 guests. Restaurant credit at some PP restaurants ($28/person). Enrollment required."},
                {"name": "Delta SkyClub (when flying Delta)", "value": "Limited", "notes": "From Feb 2025: limited to 10 visits/yr unless you spend $75k+ on card (unlimited then). Guest fees apply.", "fine_print": True},
            ],
            "Hotel & Lifestyle": [
                {"name": "Fine Hotels + Resorts (FHR)", "value": "Elite perks", "notes": "Room upgrade, noon check-in, 4pm late checkout, daily breakfast for 2, $100 property credit, guaranteed 12pm early check-in. Book via Amex Travel only.", "fine_print": True},
                {"name": "The Hotel Collection (THC)", "value": "2-night min", "notes": "$100 experience credit (food/spa/etc), room upgrade when available. Requires 2-night minimum. NOT FHR — fewer guarantees.", "fine_print": True},
                {"name": "Hilton Honors Gold Status", "value": "Complimentary", "notes": "Gold = 80% bonus points, free breakfast at some properties (not all). Must enroll via card benefits portal.", "fine_print": True},
                {"name": "Marriott Bonvoy Gold Elite", "value": "Complimentary", "notes": "Gold = 25% bonus points, enhanced room upgrade, 2pm checkout (request basis). Enroll via benefits portal.", "fine_print": True},
            ],
            "Dining & Entertainment": [
                {"name": "$240 Digital Entertainment Credit", "value": "$20/mo", "notes": "Covers: Disney+, ESPN+, Hulu, Peacock, NYT, WSJ, SiriusXM, The Atlantic. Must enroll each service separately. NOT Netflix.", "fine_print": True},
                {"name": "$300 Equinox Credit", "value": "$300/yr", "notes": "For Equinox gym memberships. Equinox+ app counts. Must use Amex Plat to charge.", "fine_print": True},
                {"name": "Global Dining Access by Resy", "value": "Priority reservations", "notes": "Early access to reservations at select restaurants. Value varies by city."},
            ],
            "Protections": [
                {"name": "Trip Cancellation / Interruption", "value": "Up to $10,000/trip", "notes": "Per trip, $20k per year. Covered reasons must be listed (illness, severe weather, etc). Paid with Amex Plat.", "fine_print": True},
                {"name": "Trip Delay Insurance", "value": "$500/trip", "notes": "Kicks in after 6-hour delay. Covers meals, lodging. Must pay fare with card.", "fine_print": True},
                {"name": "Baggage Insurance", "value": "$3,000 carry-on", "notes": "Carry-on: $3k. Checked: $2k (combined $3k). Secondary to carrier coverage."},
                {"name": "Cell Phone Protection", "value": "Not included", "notes": "Amex Plat does NOT include cell phone protection — use a Chase card for this.", "fine_print": True},
                {"name": "Purchase Protection", "value": "$10,000/item", "notes": "90 days from purchase. $50k per year limit."},
                {"name": "Extended Warranty", "value": "+1 year", "notes": "Up to $10k per item, $50k per year."},
                {"name": "No Foreign Transaction Fee", "value": "✓ Yes", "notes": ""},
            ],
            "Transfer Partners": [
                {"name": "Airlines (17+)", "value": "1:1 ratio", "notes": "Delta, Air Canada Aeroplan, United (via shop), British Airways, Flying Blue, Avianca, Turkish, Singapore, ANA, Cathay, Emirates, Etihad, Hawaiian, Iberia, JetBlue, Qantas, Virgin Atlantic.", "fine_print": False},
                {"name": "Hotels (3)", "value": "varies", "notes": "Hilton (1:2), Marriott (1:1), Choice (1:1)."},
            ],
        },
        "best_for": ["Lounge access", "Hotel status", "Premium travel perks"],
        "not_ideal_for": ["Low spenders (<$10k/yr)", "Those who won't use statement credits"],
    },

    # ── Chase Sapphire Reserve ───────────────────────────────────────────────
    {
        "id": "csr",
        "name": "Chase Sapphire Reserve",
        "issuer": "Chase",
        "network": "Visa Infinite",
        "color": "#1a1a2e",
        "text_color": "#e8d5a3",
        "annual_fee": 550,
        "welcome_bonus": "60,000–75,000 UR pts",
        "welcome_spend": "$4,000 in 3 months",
        "reward_rate": "10x hotels+cars (Chase Travel), 5x flights (Chase Travel), 3x dining+travel, 1x else",
        "points_currency": "Ultimate Rewards",
        "cpp_estimate": "1.5–2.0¢",
        "ref_link": "https://creditcards.chase.com/rewards-credit-cards/sapphire/reserve",
        "benefits": {
            "Travel Credits": [
                {"name": "$300 Travel Credit", "value": "$300/yr", "notes": "Broadest travel credit in the industry — auto-applies to ANY travel: airlines, hotels, Airbnb, Uber, Lyft, parking, tolls, transit, cruises. Resets on card anniversary.", "fine_print": False},
                {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "notes": "Once every 4 years. Can use for authorized user.", "fine_print": True},
                {"name": "Priority Pass Select", "value": "Unlimited", "notes": "Unlimited visits + 2 guests. PP restaurant credit $28/person at select airport restaurants.", "fine_print": True},
                {"name": "Chase Sapphire Lounge by The Club", "value": "Included", "notes": "New CSR-exclusive lounges at select airports (BOS, HKG, LGA, LAS, LHR, PHX, SFO, more coming). 2 guests free."},
                {"name": "DashPass (DoorDash)", "value": "Complimentary", "notes": "DashPass for free delivery. Activate by Dec 31, 2027.", "fine_print": True},
                {"name": "Instacart+", "value": "Complimentary", "notes": "Free delivery, 5% credit back. Activate by July 2025.", "fine_print": True},
            ],
            "Hotel & Lifestyle": [
                {"name": "The Luxury Hotel & Resort Collection", "value": "Elite perks", "notes": "Similar to Amex FHR — room upgrade, early check-in/late checkout, daily breakfast, $100 property credit. Must book via Chase Travel.", "fine_print": True},
                {"name": "Complimentary Lyft Pink", "value": "1 year free", "notes": "Auto-enrolls annually. 15% off rides, priority pickup."},
            ],
            "Dining & Entertainment": [
                {"name": "3x on Dining", "value": "3x UR", "notes": "All restaurants worldwide including delivery apps."},
            ],
            "Protections": [
                {"name": "Trip Cancellation / Interruption", "value": "Up to $10,000/trip", "notes": "$20k per year. Covered reasons must be listed. Pay fare with card.", "fine_print": True},
                {"name": "Trip Delay Insurance", "value": "$500/trip", "notes": "After 6 hours. Covers meals, lodging."},
                {"name": "Baggage Delay", "value": "$100/day (5 days)", "notes": "After 6-hour delay."},
                {"name": "Lost Luggage", "value": "$3,000/passenger", "notes": "Includes checked and carry-on. Primary coverage on rental cars."},
                {"name": "Primary Rental Car Insurance", "value": "Up to car value", "notes": "Decline CDW at rental counter. Primary — doesn't touch your personal auto policy. Most comprehensive in class.", "fine_print": False},
                {"name": "Cell Phone Protection", "value": "$800/claim", "notes": "Up to $1,600/year (2 claims). $50 deductible. Must pay monthly bill with card. Added 2024.", "fine_print": True},
                {"name": "Purchase Protection", "value": "$10,000/item", "notes": "120 days (longest in class)."},
                {"name": "Extended Warranty", "value": "+1 year", "notes": "Up to $10k per item."},
                {"name": "No Foreign Transaction Fee", "value": "✓ Yes", "notes": ""},
            ],
            "Transfer Partners": [
                {"name": "Airlines (11)", "value": "1:1 ratio", "notes": "United, Southwest, British Airways, Air Canada Aeroplan, Flying Blue, Iberia, Singapore, Virgin Atlantic, JetBlue, Emirates.", "fine_print": False},
                {"name": "Hotels (3)", "value": "1:1 ratio", "notes": "Hyatt (best value — 1:1), IHG, Marriott."},
            ],
        },
        "best_for": ["Flexible travel credit", "Primary rental car coverage", "Hyatt transfers", "Cell phone protection"],
        "not_ideal_for": ["Amex lounge access seekers", "High Marriott/Hilton spenders"],
    },

    # ── Capital One Venture X ────────────────────────────────────────────────
    {
        "id": "venture_x",
        "name": "Capital One Venture X",
        "issuer": "Capital One",
        "network": "Visa Infinite",
        "color": "#c8102e",
        "text_color": "#ffffff",
        "annual_fee": 395,
        "welcome_bonus": "75,000 miles",
        "welcome_spend": "$4,000 in 3 months",
        "reward_rate": "10x hotels+cars (C1 Travel), 5x flights (C1 Travel), 2x all else",
        "points_currency": "Capital One Miles",
        "cpp_estimate": "1.0–1.7¢",
        "ref_link": "https://capitalone.com/credit-cards/venture-x/",
        "benefits": {
            "Travel Credits": [
                {"name": "$300 Capital One Travel Credit", "value": "$300/yr", "notes": "ONLY for bookings through Capital One Travel portal. NOT redeemable for travel booked directly with airlines/hotels. Resets on anniversary.", "fine_print": True},
                {"name": "10,000 Bonus Miles on Anniversary", "value": "~$100 value", "notes": "10k miles credited on each account anniversary. Worth at least $100 toward Capital One Travel. Effectively offsets $100 of the $395 fee.", "fine_print": False},
                {"name": "Global Entry / TSA Pre✓", "value": "$100/$85", "notes": "Once every 4 years per account."},
                {"name": "Priority Pass Select", "value": "Unlimited", "notes": "Unlimited visits for primary cardholder + 2 guests. Authorized users each get their own PP membership."},
                {"name": "Capital One Lounge Access", "value": "Unlimited", "notes": "C1 Lounges at DFW, DEN, IAD (more opening). 2 free guests per visit."},
                {"name": "Plaza Premium Lounge Access", "value": "Unlimited", "notes": "Newer benefit — access to Plaza Premium lounges via PP Select membership."},
            ],
            "Hotel & Lifestyle": [
                {"name": "Premier Collection Hotels", "value": "Elite perks", "notes": "$100 experience credit, room upgrade, early/late checkout, daily breakfast for 2. Must book through Capital One Travel portal.", "fine_print": True},
                {"name": "Lifestyle Collection Hotels", "value": "Perks", "notes": "$50 experience credit + upgrades/breakfast at select properties. 2-night minimum NOT required (unlike Amex THC).", "fine_print": True},
            ],
            "Dining & Entertainment": [
                {"name": "2x on Everything", "value": "2x miles", "notes": "Highest unlimited baseline earn rate among premium cards. Great for non-category spending."},
                {"name": "Authorized Users", "value": "$0 fee (up to 4)", "notes": "Add up to 4 AUs free. Each AU gets their own Priority Pass membership. Massive value multiplier.", "fine_print": False},
            ],
            "Protections": [
                {"name": "Trip Cancellation / Interruption", "value": "Up to $2,000/trip", "notes": "Lower cap than Amex/Chase ($2k vs $10k). Pay fare with card.", "fine_print": True},
                {"name": "Trip Delay Insurance", "value": "$500/trip", "notes": "After 6 hours."},
                {"name": "Primary Rental Car Insurance", "value": "Up to car value", "notes": "Primary coverage — same as CSR."},
                {"name": "Cell Phone Protection", "value": "$800/claim", "notes": "Up to 2 claims/year. $50 deductible. Must pay phone bill with card."},
                {"name": "Purchase Protection", "value": "$500/item", "notes": "90 days. Lower than Amex/Chase ($500 vs $10k).", "fine_print": True},
                {"name": "Extended Warranty", "value": "+2 years", "notes": "Up to $10k per item. Extra year vs Amex/Chase."},
                {"name": "No Foreign Transaction Fee", "value": "✓ Yes", "notes": ""},
            ],
            "Transfer Partners": [
                {"name": "Airlines (15+)", "value": "1:1 mostly", "notes": "Turkish Miles&Smiles, Air Canada Aeroplan, Avianca LifeMiles, Flying Blue (AF/KLM), British Airways, Singapore, Emirates, Etihad, Finnair, TAP, Cathay. Some at 2:1.5.", "fine_print": True},
                {"name": "Hotels (2)", "value": "varies", "notes": "Wyndham (1:1), Choice Hotels (1:1)."},
            ],
        },
        "best_for": ["Best fee-to-value ratio", "Free authorized users with PP", "2x on all purchases"],
        "not_ideal_for": ["Those who need Hyatt/Marriott/Hilton status", "Portal-averse travelers (C1 Travel required for $300 credit)"],
    },

    # ── Amex Gold ────────────────────────────────────────────────────────────
    {
        "id": "amex_gold",
        "name": "Amex Gold",
        "issuer": "American Express",
        "network": "Amex",
        "color": "#CFB271",
        "text_color": "#2c1a00",
        "annual_fee": 325,
        "welcome_bonus": "60,000–100,000 MR pts",
        "welcome_spend": "$6,000 in 6 months",
        "reward_rate": "4x dining (worldwide), 4x US supermarkets (up to $25k/yr), 3x flights (direct/Amex Travel), 1x else",
        "points_currency": "Membership Rewards",
        "cpp_estimate": "1.8–2.1¢",
        "ref_link": "https://www.americanexpress.com/us/credit-cards/card/gold-card/",
        "benefits": {
            "Travel Credits": [
                {"name": "$100 Airline Fee Credit", "value": "$100/yr", "notes": "Same rules as Amex Plat — ONE pre-selected airline, incidental fees only (not tickets). Resets Jan 1.", "fine_print": True},
                {"name": "$120 Uber Cash", "value": "$10/mo", "notes": "$10/month loaded to Uber account (Uber or Uber Eats). Does NOT roll over. Must add Amex Gold to Uber app.", "fine_print": True},
                {"name": "Global Entry / TSA Pre✓", "value": "Not included", "notes": "Amex Gold does NOT offer GE/TSA credit. Use CSR or Venture X for this.", "fine_print": True},
                {"name": "No Lounge Access", "value": "None", "notes": "Gold card does not include any lounge access. Upgrade to Amex Plat if this matters.", "fine_print": True},
            ],
            "Hotel & Lifestyle": [
                {"name": "The Hotel Collection (THC)", "value": "2-night min", "notes": "$100 experience credit + room upgrade at The Hotel Collection properties. 2-night minimum. Same THC as Amex Plat, NOT the premium FHR.", "fine_print": True},
                {"name": "Marriott/Hilton Status", "value": "Not included", "notes": "No complimentary hotel status — that's Amex Plat only.", "fine_print": True},
            ],
            "Dining & Entertainment": [
                {"name": "$120 Dining Credit", "value": "$10/mo", "notes": "At Grubhub, The Cheesecake Factory, Goldbelly, Wine.com, Milk Bar, select Shake Shack. NOT all restaurants — specific merchants only.", "fine_print": True},
                {"name": "$100 Resy Credit", "value": "$50 semi-annual", "notes": "At US restaurants on Resy — $50 Jan–Jun, $50 Jul–Dec. Must book and dine via Resy.", "fine_print": True},
                {"name": "4x on Dining", "value": "4x MR", "notes": "At restaurants worldwide including delivery. Best dining earn rate among all premium cards."},
                {"name": "4x on US Supermarkets", "value": "4x MR (cap $25k)", "notes": "Capped at $25k/yr spend, then 1x. Grocery delivery (Instacart, FreshDirect) may qualify. Does NOT include warehouse clubs.", "fine_print": True},
            ],
            "Protections": [
                {"name": "Trip Delay Insurance", "value": "Not included", "notes": "Amex Gold does NOT have trip delay insurance. Major gap vs CSR/C1VX.", "fine_print": True},
                {"name": "Trip Cancellation", "value": "Not included", "notes": "Not on Gold card.", "fine_print": True},
                {"name": "Baggage Insurance", "value": "$1,250 carry-on", "notes": "Carry-on $1.25k, checked $500. Secondary to airline."},
                {"name": "Purchase Protection", "value": "$10,000/item", "notes": "90 days, $50k/yr."},
                {"name": "Extended Warranty", "value": "+1 year", "notes": "Up to $10k per item."},
                {"name": "No Foreign Transaction Fee", "value": "✓ Yes", "notes": ""},
            ],
            "Transfer Partners": [
                {"name": "Airlines (17+)", "value": "1:1 ratio", "notes": "Same Amex MR partners as Platinum — see Amex Plat row above."},
                {"name": "Hotels (3)", "value": "varies", "notes": "Hilton (1:2), Marriott (1:1), Choice (1:1)."},
            ],
        },
        "best_for": ["Foodies (4x dining)", "Grocery shoppers (4x supermarkets)", "MR earners on a budget"],
        "not_ideal_for": ["Travelers who need lounge access or trip protections", "Infrequent diners"],
    },

    # ── Chase Sapphire Preferred ─────────────────────────────────────────────
    {
        "id": "csp",
        "name": "Chase Sapphire Preferred",
        "issuer": "Chase",
        "network": "Visa Signature",
        "color": "#2e5fa3",
        "text_color": "#ffffff",
        "annual_fee": 95,
        "welcome_bonus": "60,000–100,000 UR pts",
        "welcome_spend": "$4,000 in 3 months",
        "reward_rate": "5x Chase Travel, 3x dining+online grocery+streaming, 2x other travel, 1x else",
        "points_currency": "Ultimate Rewards",
        "cpp_estimate": "1.25–2.0¢",
        "ref_link": "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
        "benefits": {
            "Travel Credits": [
                {"name": "$50 Annual Hotel Credit", "value": "$50/yr", "notes": "For hotels booked through Chase Travel only. Applied as statement credit. Resets on card anniversary.", "fine_print": True},
                {"name": "DashPass (DoorDash)", "value": "Complimentary", "notes": "Free DashPass through Dec 31, 2027. Activate required.", "fine_print": True},
                {"name": "No Lounge Access", "value": "None", "notes": "No lounge access on CSP. Upgrade to CSR for Priority Pass."},
                {"name": "No Global Entry Credit", "value": "None", "notes": "CSP does not include GE/TSA credit."},
            ],
            "Hotel & Lifestyle": [
                {"name": "The Luxury Hotel & Resort Collection", "value": "Elite perks", "notes": "Same as CSR — room upgrade, breakfast, property credit, late checkout. Must book via Chase Travel.", "fine_print": True},
                {"name": "Complimentary Lyft Pink", "value": "1 year", "notes": "15% off Lyft rides."},
            ],
            "Dining & Entertainment": [
                {"name": "10% Anniversary Bonus", "value": "10% of pts earned", "notes": "Each anniversary, Chase adds 10% of all points earned in the prior year. On $10k dining = 30k pts earned → 3k bonus pts.", "fine_print": True},
                {"name": "3x on Dining", "value": "3x UR", "notes": "All restaurants including delivery."},
                {"name": "3x on Online Groceries", "value": "3x UR", "notes": "Includes Instacart, Amazon Fresh. NOT physical grocery stores (use Amex Gold for that).", "fine_print": True},
                {"name": "3x on Streaming", "value": "3x UR", "notes": "Netflix, Hulu, Spotify, Disney+, etc."},
            ],
            "Protections": [
                {"name": "Trip Cancellation / Interruption", "value": "Up to $10,000/trip", "notes": "$20k per year. Same coverage as CSR. Pay fare with card.", "fine_print": True},
                {"name": "Trip Delay Insurance", "value": "$500/trip", "notes": "After 12 hours (CSR: 6 hours). CSP is stricter trigger.", "fine_print": True},
                {"name": "Baggage Delay", "value": "$100/day (5 days)", "notes": "After 6-hour delay."},
                {"name": "Primary Rental Car Insurance", "value": "Up to car value", "notes": "Primary — same as CSR. Unusual for a $95 card.", "fine_print": False},
                {"name": "No Cell Phone Protection", "value": "Not included", "notes": "CSP does not include cell phone protection."},
                {"name": "Purchase Protection", "value": "$500/item", "notes": "120 days, up to $50k/yr."},
                {"name": "Extended Warranty", "value": "+1 year", "notes": "Up to $10k per item."},
                {"name": "No Foreign Transaction Fee", "value": "✓ Yes", "notes": ""},
            ],
            "Transfer Partners": [
                {"name": "Airlines (11)", "value": "1:1 ratio", "notes": "Same Chase UR partners as CSR — United, Southwest, BA, Aeroplan, Flying Blue, Iberia, Singapore, Virgin Atlantic, JetBlue, Emirates."},
                {"name": "Hotels (3)", "value": "1:1 ratio", "notes": "Hyatt (best value), IHG, Marriott. Transfer to Hyatt is same as CSR — massive value unlock."},
            ],
        },
        "best_for": ["Entry-level premium travel card", "Hyatt transfers at $95", "Primary rental car insurance on budget", "Dining + streaming rewards"],
        "not_ideal_for": ["Frequent lounge visitors", "Those who can maximize CSR credits"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  COMPARISON MATRIX DATA
# ─────────────────────────────────────────────────────────────────────────────

COMPARE_ROWS = [
    ("Annual Fee",         ["$695", "$550", "$395", "$325", "$95"]),
    ("Network",            ["Amex", "Visa Infinite", "Visa Infinite", "Amex", "Visa Signature"]),
    ("Points Currency",    ["Membership Rewards", "Ultimate Rewards", "C1 Miles", "Membership Rewards", "Ultimate Rewards"]),
    ("Est. CPP",           ["1.8–2.1¢", "1.5–2.0¢", "1.0–1.7¢", "1.8–2.1¢", "1.25–2.0¢"]),
    ("Welcome Bonus",      ["80k–175k MR", "60k–75k UR", "75k miles", "60k–100k MR", "60k–100k UR"]),
    ("Min Spend (Bonus)",  ["$8k / 6mo", "$4k / 3mo", "$4k / 3mo", "$6k / 6mo", "$4k / 3mo"]),
    ("Travel Credit",      ["$200 airline\n(incidentals only)", "$300 any travel\n(broadest)", "$300 C1 Travel\n(portal only)", "$100 airline\n(incidentals only)", "$50 Chase Travel\n(hotels only)"]),
    ("Dining Credit",      ["—", "—", "—", "$120/yr (select merchants)", "$0"]),
    ("Lounge Access",      ["Centurion + PP\n+ Delta (10x)", "CSR Lounge + PP\n+ Sapphire Lounges", "C1 Lounge + PP\n+ Plaza Premium", "None", "None"]),
    ("Hotel Status",       ["Hilton Gold\n+ Marriott Gold", "None (LHRC perks)", "Premier Collection\nperks", "THC perks\n(2-night min)", "LHRC perks"]),
    ("GE / TSA Pre✓",      ["✓ GE ($100)", "✓ GE ($100)", "✓ GE ($100)", "✗ None", "✗ None"]),
    ("Trip Cancel / Int.", ["✓ $10k/trip", "✓ $10k/trip", "✓ $2k/trip", "✗ Not included", "✓ $10k/trip"]),
    ("Trip Delay",         ["✓ 6 hrs / $500", "✓ 6 hrs / $500", "✓ 6 hrs / $500", "✗ Not included", "✓ 12 hrs / $500"]),
    ("Primary Rental Car", ["✗ Secondary", "✓ Primary", "✓ Primary", "✗ Secondary", "✓ Primary"]),
    ("Cell Phone Prot.",   ["✗ None", "✓ $800/claim", "✓ $800/claim", "✗ None", "✗ None"]),
    ("AU Lounge Benefit",  ["$175/additional AU", "$75/additional AU", "Free (PP each AU)", "N/A", "N/A"]),
    ("No FX Fee",          ["✓", "✓", "✓", "✓", "✓"]),
    ("Best Transfer Partner", ["Aeroplan (2¢+)", "Hyatt (2.5¢+)", "Aeroplan (2¢+)", "Aeroplan (2¢+)", "Hyatt (2.5¢+)"]),
]

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
<style>
/* Card header pill */
.card-header {
    border-radius: 16px;
    padding: 18px 20px 14px 20px;
    margin-bottom: 6px;
    min-height: 140px;
    display: flex; flex-direction: column; justify-content: space-between;
}
.card-name { font-size: 17px; font-weight: 800; letter-spacing: 0.5px; }
.card-issuer { font-size: 11px; opacity: 0.75; margin-top: 2px; }
.card-fee { font-size: 26px; font-weight: 900; margin-top: 10px; }
.card-fee-label { font-size: 11px; opacity: 0.65; }
.card-network { font-size: 11px; opacity: 0.80; margin-top: 4px; font-style: italic; }

/* Benefit category headers */
.benefit-cat {
    background: linear-gradient(90deg,#1e3a5f,#2d5986);
    color:#e8f4ff; font-size:13px; font-weight:700;
    padding: 5px 14px; border-radius: 8px; margin: 10px 0 6px 0;
    letter-spacing: 0.5px;
}

/* Benefit row */
.benefit-row {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 8px 12px; margin-bottom: 5px;
}
.benefit-name { font-size: 13px; font-weight: 700; color: #1e3a5f; }
.benefit-value { font-size: 13px; font-weight: 800; color: #059669; }
.benefit-notes { font-size: 11.5px; color: #475569; margin-top: 3px; line-height: 1.4; }
.fine-print-badge {
    background: #fef3c7; color: #92400e; font-size: 10px;
    padding: 1px 7px; border-radius: 10px; font-weight: 700;
    display: inline-block; margin-left: 6px; vertical-align: middle;
}

/* Compare table */
.cmp-table { width:100%; border-collapse:collapse; font-size:12.5px; }
.cmp-table th {
    padding: 10px 12px; color: #fff; font-size: 12px; font-weight: 800;
    text-align: center; border-bottom: 3px solid #fff;
}
.cmp-table td {
    padding: 8px 12px; border-bottom: 1px solid #e2e8f0;
    text-align: center; vertical-align: middle; color: #334155;
}
.cmp-table tr:hover td { background: #f0f9ff; }
.cmp-table td:first-child { text-align: left; font-weight: 700; color: #1e3a5f; background: #f8fafc; }
.cmp-table th:first-child { text-align: left; background: #1e3a5f; }
.tick { color: #059669; font-weight: 900; font-size: 15px; }
.cross { color: #dc2626; font-weight: 900; font-size: 15px; }
.highlight-cell { background: #ecfdf5 !important; }

/* Best for tags */
.tag-good { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; display:inline-block; margin:2px; }
.tag-bad  { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; display:inline-block; margin:2px; }

/* Source note */
.source-note { font-size: 11px; color: #94a3b8; font-style: italic; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER RENDERERS
# ─────────────────────────────────────────────────────────────────────────────

def render_card_header(card: dict):
    bg = card["color"]
    fg = card["text_color"]
    st.markdown(f"""
<div class="card-header" style="background:{bg}; color:{fg};">
  <div>
    <div class="card-name">{card['name']}</div>
    <div class="card-issuer">{card['issuer']} · {card['network']}</div>
  </div>
  <div>
    <div class="card-fee">${card['annual_fee']:,}</div>
    <div class="card-fee-label">annual fee</div>
    <div class="card-network">{card['points_currency']} · ~{card['cpp_estimate']}/pt</div>
  </div>
</div>""", unsafe_allow_html=True)


def render_benefit_block(card: dict, category: str):
    items = card["benefits"].get(category, [])
    if not items:
        st.markdown('<div style="color:#94a3b8;font-size:12px;padding:6px 0;">—</div>', unsafe_allow_html=True)
        return
    for b in items:
        fp_badge = '<span class="fine-print-badge">⚠ fine print</span>' if b.get("fine_print") else ""
        notes_html = f'<div class="benefit-notes">{b["notes"]}</div>' if b["notes"] else ""
        st.markdown(f"""
<div class="benefit-row">
  <span class="benefit-name">{b['name']}</span>
  <span style="float:right;" class="benefit-value">{b['value']}</span>
  {fp_badge}
  {notes_html}
</div>""", unsafe_allow_html=True)


def render_compare_table(selected_ids: list):
    selected = [c for c in CARDS if c["id"] in selected_ids]
    if not selected:
        return

    # Build header
    header = '<tr><th style="min-width:140px;">Feature</th>'
    for c in selected:
        header += f'<th style="background:{c["color"]};color:{c["text_color"]};">{c["name"]}</th>'
    header += "</tr>"

    rows_html = ""
    for label, values in COMPARE_ROWS:
        # Only include values for selected cards (by order in CARDS list)
        sel_indices = [i for i, c in enumerate(CARDS) if c["id"] in selected_ids]
        sel_values = [values[i] for i in sel_indices]

        row = f'<tr><td>{label}</td>'
        for v in sel_values:
            # Highlight ✓ green, ✗ red
            display = v.replace("✓", '<span class="tick">✓</span>').replace("✗", '<span class="cross">✗</span>')
            display = display.replace("\n", "<br>")
            row += f'<td>{display}</td>'
        row += "</tr>"
        rows_html += row

    st.markdown(f"""
<div style="overflow-x:auto;">
<table class="cmp-table">
  <thead>{header}</thead>
  <tbody>{rows_html}</tbody>
</table>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────

_inject_css()

st.title("🃏 Premium Card Comparison")
st.markdown(
    "<div class='source-note'>Data verified June 2026 · Benefits change frequently — always confirm at issuer's site before applying · "
    "⚠ fine print badges highlight gotchas that catch people off-guard</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_overview, tab_detail, tab_fine_print, tab_refs = st.tabs([
    "📊 Side-by-Side Compare",
    "🔍 Card Deep Dive",
    "⚠️ Fine Print Summary",
    "🔗 References & Apply",
])

# ─── Tab 1: Side-by-Side ────────────────────────────────────────────────────
with tab_overview:
    st.subheader("Select cards to compare")
    card_names = {c["id"]: c["name"] for c in CARDS}
    default_ids = [c["id"] for c in CARDS]

    sel_cols = st.columns(len(CARDS))
    selected_ids = []
    for i, card in enumerate(CARDS):
        with sel_cols[i]:
            if st.checkbox(card["name"], value=True, key=f"sel_{card['id']}"):
                selected_ids.append(card["id"])

    if selected_ids:
        st.markdown("<br>", unsafe_allow_html=True)
        render_compare_table(selected_ids)
    else:
        st.info("Select at least one card above.")

    # Card header summaries
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Card Profiles")
    cols = st.columns(len(CARDS))
    for i, card in enumerate(CARDS):
        with cols[i]:
            render_card_header(card)
            # Best for
            best_html = "".join(f'<span class="tag-good">{t}</span>' for t in card["best_for"])
            bad_html = "".join(f'<span class="tag-bad">{t}</span>' for t in card["not_ideal_for"])
            st.markdown(f"**Best for:** {best_html}", unsafe_allow_html=True)
            st.markdown(f"**Skip if:** {bad_html}", unsafe_allow_html=True)
            st.markdown(f"[Apply / Learn More ↗]({card['ref_link']})")


# ─── Tab 2: Card Deep Dive ───────────────────────────────────────────────────
with tab_detail:
    card_choice = st.selectbox(
        "Choose a card to deep dive",
        options=[c["id"] for c in CARDS],
        format_func=lambda x: next(c["name"] for c in CARDS if c["id"] == x),
    )
    card = next(c for c in CARDS if c["id"] == card_choice)

    render_card_header(card)
    st.markdown(f"""
**Welcome Bonus:** {card['welcome_bonus']}
**Spend Requirement:** {card['welcome_spend']}
**Reward Rate:** {card['reward_rate']}
**Transfer Partners:** {card['points_currency']}
""")
    best_html = "".join(f'<span class="tag-good">{t}</span>' for t in card["best_for"])
    bad_html = "".join(f'<span class="tag-bad">{t}</span>' for t in card["not_ideal_for"])
    st.markdown(f"**Best for:** {best_html}", unsafe_allow_html=True)
    st.markdown(f"**Skip if:** {bad_html}", unsafe_allow_html=True)

    st.markdown("---")
    for category, items in card["benefits"].items():
        st.markdown(f'<div class="benefit-cat">🏷️ {category}</div>', unsafe_allow_html=True)
        render_benefit_block(card, category)


# ─── Tab 3: Fine Print Summary ───────────────────────────────────────────────
with tab_fine_print:
    st.subheader("⚠️ Most Common Gotchas — Fine Print You Need to Know")
    st.markdown("These are the top misunderstandings that cost cardholders value. Read before you use your benefits.")

    # Collect all fine-print items across all cards
    for card in CARDS:
        fp_items = []
        for category, items in card["benefits"].items():
            for b in items:
                if b.get("fine_print") and b["notes"]:
                    fp_items.append((category, b["name"], b["value"], b["notes"]))

        if fp_items:
            st.markdown(
                f'<div class="card-header" style="background:{card["color"]};color:{card["text_color"]};padding:10px 16px;min-height:auto;">'
                f'<span class="card-name">{card["name"]}</span> '
                f'<span class="card-issuer">— ${card["annual_fee"]}/yr</span></div>',
                unsafe_allow_html=True,
            )
            for cat, name, value, note in fp_items:
                st.markdown(f"""
<div class="benefit-row" style="border-left: 4px solid #f59e0b;">
  <span class="benefit-name">⚠ {name}</span>
  <span style="float:right;" class="benefit-value">{value}</span>
  <div class="benefit-notes"><b>[{cat}]</b> {note}</div>
</div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


# ─── Tab 4: References ───────────────────────────────────────────────────────
with tab_refs:
    st.subheader("🔗 Official Card Pages & Deep-Dive Resources")
    st.markdown(
        "Always verify current offer terms at issuer pages — welcome bonuses, annual fees, and credit amounts change. "
        "Third-party sites below are for research only; apply at official bank sites."
    )

    ref_data = [
        ("Amex Platinum", "https://www.americanexpress.com/us/credit-cards/card/platinum/",
         "Official Amex Platinum page with current offer and benefits"),
        ("Chase Sapphire Reserve", "https://creditcards.chase.com/rewards-credit-cards/sapphire/reserve",
         "Official CSR page with current bonus and protections guide"),
        ("Capital One Venture X", "https://capitalone.com/credit-cards/venture-x/",
         "Official Venture X page — check AU card count limits"),
        ("Amex Gold", "https://www.americanexpress.com/us/credit-cards/card/gold-card/",
         "Official Amex Gold — verify dining credit merchant list (changes)"),
        ("Chase Sapphire Preferred", "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
         "Official CSP page — current 10% anniversary bonus terms"),
        ("The Points Guy — Card Comparisons", "https://thepointsguy.com/credit-cards/compare/",
         "Independent research, valuation tables, current offers"),
        ("NerdWallet — Premium Card Comparison", "https://www.nerdwallet.com/best/credit-cards/premium-travel",
         "Side-by-side benefit breakdowns with editor reviews"),
        ("Doctor of Credit — Fine Print Database", "https://www.doctorofcredit.com",
         "Deep fine-print research, data points, Amex offer tracking"),
        ("Amex FHR vs THC Explainer (TPG)", "https://thepointsguy.com/guide/amex-fine-hotels-resorts-hotel-collection/",
         "Critical: explains difference between FHR and THC benefits"),
        ("Chase Priority Pass Restaurant Credits", "https://thepointsguy.com/news/chase-priority-pass-changes/",
         "Explains the $28/person restaurant credit and recent changes"),
        ("Centurion Lounge Guest Policy (2024+)", "https://thepointsguy.com/news/amex-centurion-lounge-new-guest-policy/",
         "Updated policy: $50/guest unless you spend $75k/yr on Amex"),
        ("Capital One Lounge Locations", "https://www.capitalone.com/credit-cards/venture-x/lounge/",
         "Current C1 Lounge airports and hours"),
        ("Amex Delta SkyClub Access Policy (2025)", "https://thepointsguy.com/news/amex-delta-sky-club-access-changes/",
         "10 visit cap per year unless $75k spend on Amex"),
    ]

    for name, url, desc in ref_data:
        st.markdown(f"**[{name}]({url})**  \n{desc}")
        st.markdown("")

    st.markdown("---")
    st.markdown("""
**Data Sources Used for This Page:**
- Official card benefit guides (Amex, Chase, Capital One) — verified June 2026
- The Points Guy card valuation table (June 2026)
- NerdWallet editorial card reviews
- Doctor of Credit data points

*This page is informational only. Not financial advice. Credit card terms change — verify before relying on any value shown here.*
""")

"""Credit card & points service."""
import uuid
import pandas as pd
from datetime import date
from backend.gsheet import read_sheet, append_row, overwrite_sheet

TAB = "cc_cards"

BANK_ICONS = {
    "chase": "🔵", "amex": "🟦", "citi": "🔴", "capital one": "💜",
    "discover": "🟠", "bank of america": "🔴", "wells fargo": "🟡",
    "other": "💳",
}


def icon(bank: str) -> str:
    return BANK_ICONS.get(bank.lower(), "💳")


def list_cards(active_only: bool = True) -> pd.DataFrame:
    df = read_sheet(TAB)
    if df.empty:
        return df
    if active_only:
        df = df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
    return df


def add_card(name: str, bank: str, last4: str, annual_fee: float,
             fee_due_date: date, credit_limit: float, perks: str = "") -> str:
    cid = str(uuid.uuid4())[:8]
    append_row(TAB, [cid, name, bank, last4, annual_fee,
                     fee_due_date.isoformat(), credit_limit, perks, "TRUE"])
    return cid


def update_card(card_id: str, **kwargs) -> None:
    df = list_cards(active_only=False)
    for k, v in kwargs.items():
        if k in df.columns:
            df.loc[df["id"] == card_id, k] = v
    overwrite_sheet(TAB, df)


def delete_card(card_id: str) -> None:
    df = list_cards(active_only=False)
    df.loc[df["id"] == card_id, "active"] = "FALSE"
    overwrite_sheet(TAB, df)


def total_annual_fees(df: pd.DataFrame | None = None) -> float:
    if df is None:
        df = list_cards()
    if df.empty:
        return 0.0
    return float(df["annual_fee"].apply(pd.to_numeric, errors="coerce").fillna(0).sum())


def fees_due_soon(days: int = 30, df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = list_cards()
    if df.empty:
        return df
    df = df.copy()
    df["fee_due_date"] = pd.to_datetime(df["fee_due_date"], errors="coerce").dt.date
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=days)
    return df[df["fee_due_date"] <= cutoff]


# ── Spend categories (UI label, internal key) ─────────────────────────────────
SPEND_CATEGORIES = [
    ("✈️ Travel",    "travel"),
    ("🍽️ Dining",   "dining"),
    ("🛒 Grocery",   "grocery"),
    ("⛽ Gas",        "gas"),
    ("📺 Streaming", "streaming"),
    ("💊 Pharmacy",  "pharmacy"),
    ("🚇 Transit",   "transit"),
    ("🛍️ Other",    "other"),
]

# ── Card rewards knowledge base ───────────────────────────────────────────────
# categories: points per $1 spent
# point_value: conservative cents per point via travel portal
# transfer_value: estimated cpp via airline/hotel transfer partners
CARD_REWARDS: dict[str, dict] = {
    "chase sapphire preferred": {
        "display": "Chase Sapphire Preferred", "bank": "chase",
        "annual_fee": 95, "point_value": 1.25, "transfer_value": 1.8,
        "network": "Chase Ultimate Rewards",
        "categories": {"travel":3,"dining":3,"streaming":3,"grocery":3,"transit":3,"gas":1,"pharmacy":1,"other":1},
        "lounge_networks": [],
        "credits": ["$50 hotel credit (Chase portal)"],
    },
    "chase sapphire reserve": {
        "display": "Chase Sapphire Reserve", "bank": "chase",
        "annual_fee": 550, "point_value": 1.5, "transfer_value": 2.0,
        "network": "Chase Ultimate Rewards",
        "categories": {"travel":10,"dining":3,"streaming":1,"grocery":1,"transit":10,"gas":1,"pharmacy":1,"other":1},
        "lounge_networks": ["Priority Pass", "Chase Sapphire Lounge"],
        "credits": ["$300 travel credit", "$100 Global Entry/TSA Pre✓"],
    },
    "chase freedom unlimited": {
        "display": "Chase Freedom Unlimited", "bank": "chase",
        "annual_fee": 0, "point_value": 1.0, "transfer_value": 1.5,
        "network": "Chase Ultimate Rewards",
        "categories": {"travel":5,"dining":3,"pharmacy":3,"grocery":1,"gas":1,"streaming":1,"transit":1,"other":1.5},
        "lounge_networks": [], "credits": [],
    },
    "chase freedom flex": {
        "display": "Chase Freedom Flex", "bank": "chase",
        "annual_fee": 0, "point_value": 1.0, "transfer_value": 1.5,
        "network": "Chase Ultimate Rewards",
        "categories": {"travel":5,"dining":3,"pharmacy":3,"grocery":1,"gas":1,"streaming":1,"transit":1,"other":1},
        "lounge_networks": [], "credits": ["5% rotating quarterly categories (up to $1,500/qtr)"],
    },
    "amex platinum": {
        "display": "Amex Platinum", "bank": "amex",
        "annual_fee": 695, "point_value": 1.0, "transfer_value": 2.0,
        "network": "Amex Membership Rewards",
        "categories": {"travel":5,"airlines":5,"hotels":5,"dining":1,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1},
        "lounge_networks": ["Centurion", "Priority Pass", "Escape Lounges", "Delta Sky Club"],
        "credits": ["$200 airline fee credit","$200 hotel credit","$240 digital entertainment","$155 Walmart+","$100 Saks","$189 CLEAR","$300 Equinox"],
    },
    "amex gold": {
        "display": "Amex Gold", "bank": "amex",
        "annual_fee": 250, "point_value": 1.0, "transfer_value": 2.0,
        "network": "Amex Membership Rewards",
        "categories": {"dining":4,"grocery":4,"travel":3,"airlines":3,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1},
        "lounge_networks": [],
        "credits": ["$120 dining credit ($10/mo)","$120 Uber Cash ($10/mo)"],
    },
    "amex blue cash preferred": {
        "display": "Amex Blue Cash Preferred", "bank": "amex",
        "annual_fee": 95, "point_value": 1.0, "transfer_value": 1.0,
        "network": "Cash Back",
        "categories": {"grocery":6,"streaming":6,"transit":3,"gas":3,"dining":1,"travel":1,"pharmacy":1,"other":1},
        "lounge_networks": [], "credits": [],
    },
    "capital one venture x": {
        "display": "Capital One Venture X", "bank": "capital one",
        "annual_fee": 395, "point_value": 1.0, "transfer_value": 1.7,
        "network": "Capital One Miles",
        "categories": {"travel":10,"hotels":10,"rental":10,"dining":2,"grocery":2,"gas":2,"streaming":2,"transit":2,"pharmacy":1,"other":2},
        "lounge_networks": ["Capital One Lounge", "Priority Pass"],
        "credits": ["$300 travel credit (portal)","10,000 bonus miles/year"],
    },
    "capital one venture": {
        "display": "Capital One Venture", "bank": "capital one",
        "annual_fee": 95, "point_value": 1.0, "transfer_value": 1.5,
        "network": "Capital One Miles",
        "categories": {"travel":5,"hotels":5,"rental":5,"dining":2,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":2},
        "lounge_networks": [],
        "credits": ["$100 Global Entry/TSA Pre✓"],
    },
    "citi double cash": {
        "display": "Citi Double Cash", "bank": "citi",
        "annual_fee": 0, "point_value": 1.0, "transfer_value": 1.6,
        "network": "Cash Back / Citi ThankYou",
        "categories": {"travel":1,"dining":1,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":2},
        "lounge_networks": [], "credits": [],
    },
    "citi custom cash": {
        "display": "Citi Custom Cash", "bank": "citi",
        "annual_fee": 0, "point_value": 1.0, "transfer_value": 1.6,
        "network": "Cash Back / Citi ThankYou",
        "categories": {"travel":1,"dining":1,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1},
        "lounge_networks": [], "credits": ["5% auto on top category (up to $500/mo)"],
    },
    "citi aadvantage executive": {
        "display": "Citi AAdvantage Executive", "bank": "citi",
        "annual_fee": 595, "point_value": 1.5, "transfer_value": 1.5,
        "network": "AA AAdvantage",
        "categories": {"airlines":10,"travel":4,"dining":4,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1},
        "lounge_networks": ["Admirals Club"],
        "credits": ["Admirals Club membership (~$650 value)"],
    },
    "discover it": {
        "display": "Discover it Cash Back", "bank": "discover",
        "annual_fee": 0, "point_value": 1.0, "transfer_value": 1.0,
        "network": "Cash Back",
        "categories": {"travel":1,"dining":1,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1},
        "lounge_networks": [], "credits": ["5% rotating quarterly categories","Cash back match yr 1"],
    },
    "bank of america premium rewards": {
        "display": "BofA Premium Rewards", "bank": "bank of america",
        "annual_fee": 95, "point_value": 1.0, "transfer_value": 1.0,
        "network": "Cash Back",
        "categories": {"travel":2,"dining":2,"grocery":1,"gas":1,"streaming":1,"transit":1,"pharmacy":1,"other":1.5},
        "lounge_networks": [],
        "credits": ["$100 airline incidental credit"],
    },
}

# ── Airport lounge data ────────────────────────────────────────────────────────
# network values must match strings used in CARD_REWARDS["lounge_networks"]
LOUNGE_DATA: dict[str, dict] = {
    "DFW": {"name": "Dallas/Fort Worth International", "city": "Dallas, TX", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "D",           "network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "D",           "network": "Capital One Lounge"},
        {"name": "American Airlines Admirals Club", "terminal": "A/B/C/D/E", "network": "Admirals Club"},
        {"name": "The Club DFW (Priority Pass)","terminal": "D",           "network": "Priority Pass"},
    ]},
    "DAL": {"name": "Dallas Love Field", "city": "Dallas, TX", "lounges": [
        {"name": "Southwest Airlines Business Select Lounge", "terminal": "Main", "network": "None (status only)"},
    ]},
    "LAX": {"name": "Los Angeles International", "city": "Los Angeles, CA", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "TBIT (B40)",  "network": "Centurion"},
        {"name": "United Club",                 "terminal": "TBIT",        "network": "United Club"},
        {"name": "Delta Sky Club",              "terminal": "3",           "network": "Delta Sky Club"},
        {"name": "Admirals Club",               "terminal": "4 & 5",      "network": "Admirals Club"},
        {"name": "Alaska Lounge",               "terminal": "6",           "network": "Alaska Lounge"},
        {"name": "Star Alliance Business (Lufthansa)", "terminal": "TBIT", "network": "Priority Pass"},
    ]},
    "JFK": {"name": "John F. Kennedy International", "city": "New York, NY", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "4",           "network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "4",           "network": "Capital One Lounge"},
        {"name": "Delta Sky Club",              "terminal": "4",           "network": "Delta Sky Club"},
        {"name": "Chase Sapphire Lounge",       "terminal": "4",           "network": "Chase Sapphire Lounge"},
        {"name": "Admirals Club",               "terminal": "8",           "network": "Admirals Club"},
        {"name": "United Club",                 "terminal": "7",           "network": "United Club"},
        {"name": "Air France Lounge (PP)",      "terminal": "1",           "network": "Priority Pass"},
    ]},
    "LGA": {"name": "LaGuardia Airport", "city": "New York, NY", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "C",           "network": "Centurion"},
        {"name": "Chase Sapphire Lounge",       "terminal": "C",           "network": "Chase Sapphire Lounge"},
        {"name": "Delta Sky Club",              "terminal": "C",           "network": "Delta Sky Club"},
        {"name": "Admirals Club",               "terminal": "B",           "network": "Admirals Club"},
    ]},
    "EWR": {"name": "Newark Liberty International", "city": "Newark, NJ", "lounges": [
        {"name": "United Club",                 "terminal": "C",           "network": "United Club"},
        {"name": "Escape Lounge (PP)",          "terminal": "A",           "network": "Priority Pass"},
    ]},
    "ORD": {"name": "Chicago O'Hare International", "city": "Chicago, IL", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "3",           "network": "Centurion"},
        {"name": "United Club",                 "terminal": "1 (C/E/F)",   "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "3",           "network": "Admirals Club"},
        {"name": "Escape Lounge (PP)",          "terminal": "3",           "network": "Priority Pass"},
    ]},
    "ATL": {"name": "Hartsfield-Jackson Atlanta", "city": "Atlanta, GA", "lounges": [
        {"name": "Delta Sky Club",              "terminal": "A/B/C/D/F/S", "network": "Delta Sky Club"},
        {"name": "Admirals Club",               "terminal": "T (A15)",     "network": "Admirals Club"},
        {"name": "The Plane Club (PP)",         "terminal": "International","network": "Priority Pass"},
    ]},
    "MIA": {"name": "Miami International", "city": "Miami, FL", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "D",           "network": "Centurion"},
        {"name": "Admirals Club",               "terminal": "D",           "network": "Admirals Club"},
        {"name": "LATAM VIP Lounge (PP)",       "terminal": "E",           "network": "Priority Pass"},
    ]},
    "MCO": {"name": "Orlando International", "city": "Orlando, FL", "lounges": [
        {"name": "Capital One Lounge",          "terminal": "C",           "network": "Capital One Lounge"},
        {"name": "The Club MCO (PP)",           "terminal": "B",           "network": "Priority Pass"},
    ]},
    "SFO": {"name": "San Francisco International", "city": "San Francisco, CA", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "3",           "network": "Centurion"},
        {"name": "Chase Sapphire Lounge",       "terminal": "B",           "network": "Chase Sapphire Lounge"},
        {"name": "United Club",                 "terminal": "3",           "network": "United Club"},
        {"name": "Alaska Lounge",               "terminal": "2",           "network": "Alaska Lounge"},
        {"name": "Air France Lounge (PP)",      "terminal": "International","network": "Priority Pass"},
    ]},
    "SEA": {"name": "Seattle-Tacoma International", "city": "Seattle, WA", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "Central",     "network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "Central",     "network": "Capital One Lounge"},
        {"name": "Alaska Lounge",               "terminal": "N/S Satellite","network": "Alaska Lounge"},
        {"name": "Delta Sky Club",              "terminal": "S Satellite", "network": "Delta Sky Club"},
        {"name": "United Club",                 "terminal": "Central A",   "network": "United Club"},
    ]},
    "DEN": {"name": "Denver International", "city": "Denver, CO", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "B",           "network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "B",           "network": "Capital One Lounge"},
        {"name": "United Club",                 "terminal": "B",           "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "C",           "network": "Admirals Club"},
        {"name": "Delta Sky Club",              "terminal": "C",           "network": "Delta Sky Club"},
    ]},
    "PHX": {"name": "Phoenix Sky Harbor International", "city": "Phoenix, AZ", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "4",           "network": "Centurion"},
        {"name": "Chase Sapphire Lounge",       "terminal": "4",           "network": "Chase Sapphire Lounge"},
        {"name": "Admirals Club",               "terminal": "4",           "network": "Admirals Club"},
        {"name": "The Club PHX (PP)",           "terminal": "4",           "network": "Priority Pass"},
    ]},
    "LAS": {"name": "Harry Reid International", "city": "Las Vegas, NV", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "3",           "network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "1",           "network": "Capital One Lounge"},
        {"name": "Chase Sapphire Lounge",       "terminal": "3",           "network": "Chase Sapphire Lounge"},
        {"name": "United Club",                 "terminal": "3",           "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "3 (D gate)", "network": "Admirals Club"},
        {"name": "The Centurion Studio (PP)",   "terminal": "1",           "network": "Priority Pass"},
    ]},
    "BOS": {"name": "Boston Logan International", "city": "Boston, MA", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "E",           "network": "Centurion"},
        {"name": "Chase Sapphire Lounge",       "terminal": "E",           "network": "Chase Sapphire Lounge"},
        {"name": "Delta Sky Club",              "terminal": "A",           "network": "Delta Sky Club"},
        {"name": "United Club",                 "terminal": "B",           "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "B",           "network": "Admirals Club"},
    ]},
    "IAH": {"name": "Houston Bush Intercontinental", "city": "Houston, TX", "lounges": [
        {"name": "United Club",                 "terminal": "C/E",         "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "A",           "network": "Admirals Club"},
        {"name": "The Club IAH (PP)",           "terminal": "E",           "network": "Priority Pass"},
    ]},
    "CLT": {"name": "Charlotte Douglas International", "city": "Charlotte, NC", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "Main (E)",    "network": "Centurion"},
        {"name": "Admirals Club",               "terminal": "B/C/D/E",    "network": "Admirals Club"},
        {"name": "Delta Sky Club",              "terminal": "B",           "network": "Delta Sky Club"},
    ]},
    "IAD": {"name": "Washington Dulles International", "city": "Washington, DC", "lounges": [
        {"name": "Amex Centurion Lounge",      "terminal": "Main (Gate D9)","network": "Centurion"},
        {"name": "Capital One Lounge",          "terminal": "Concourse A", "network": "Capital One Lounge"},
        {"name": "United Club",                 "terminal": "C/D",         "network": "United Club"},
        {"name": "Admirals Club",               "terminal": "D",           "network": "Admirals Club"},
    ]},
    "DCA": {"name": "Reagan National Airport", "city": "Washington, DC", "lounges": [
        {"name": "Admirals Club",               "terminal": "B/C",         "network": "Admirals Club"},
        {"name": "Delta Sky Club",              "terminal": "C",           "network": "Delta Sky Club"},
        {"name": "United Club",                 "terminal": "C",           "network": "United Club"},
    ]},
    "HNL": {"name": "Honolulu Daniel K. Inouye Intl", "city": "Honolulu, HI", "lounges": [
        {"name": "Chase Sapphire Lounge",       "terminal": "Main",        "network": "Chase Sapphire Lounge"},
        {"name": "United Club",                 "terminal": "Main",        "network": "United Club"},
        {"name": "Alaska Lounge",               "terminal": "Main",        "network": "Alaska Lounge"},
        {"name": "The Centurion (PP)",          "terminal": "Main",        "network": "Priority Pass"},
    ]},
}

# ── Current top card offers (verify at issuer — offers change frequently) ──────
TOP_OFFERS: list[dict] = [
    {
        "card": "Chase Sapphire Preferred", "bank": "chase", "annual_fee": 95,
        "category": "Best for Travel Beginners",
        "offer": "60,000–80,000 Chase UR points", "spend_req": "$4,000 in 3 months",
        "est_value": "$750–$1,500", "cpp": 1.25,
        "highlight": "3x dining, travel & streaming; transfer to United, Hyatt, Southwest; $50 hotel credit",
        "url_hint": "chase.com/sapphire/preferred",
    },
    {
        "card": "Amex Gold", "bank": "amex", "annual_fee": 250,
        "category": "Best for Dining & Groceries",
        "offer": "60,000–90,000 Amex MR points", "spend_req": "$6,000 in 6 months",
        "est_value": "$1,200–$1,800", "cpp": 2.0,
        "highlight": "4x dining & U.S. groceries; $120 dining credit; $120 Uber Cash; transfer to Delta, Marriott",
        "url_hint": "americanexpress.com/gold",
    },
    {
        "card": "Amex Platinum", "bank": "amex", "annual_fee": 695,
        "category": "Best Premium Card",
        "offer": "80,000–150,000 Amex MR points", "spend_req": "$8,000 in 6 months",
        "est_value": "$1,600–$3,000", "cpp": 2.0,
        "highlight": "Centurion + Priority Pass lounge access; $200 airline + $200 hotel credits; 5x on flights",
        "url_hint": "americanexpress.com/platinum",
    },
    {
        "card": "Capital One Venture X", "bank": "capital one", "annual_fee": 395,
        "category": "Best All-Around Premium",
        "offer": "75,000 Capital One miles", "spend_req": "$4,000 in 3 months",
        "est_value": "$1,275–$1,500", "cpp": 1.7,
        "highlight": "10x hotels & rentals; Capital One + Priority Pass lounges; $300 travel credit; 10k bonus miles/yr",
        "url_hint": "capitalone.com/venturex",
    },
    {
        "card": "Chase Sapphire Reserve", "bank": "chase", "annual_fee": 550,
        "category": "Best for Frequent Travelers",
        "offer": "60,000 Chase UR points", "spend_req": "$4,000 in 3 months",
        "est_value": "$1,200–$1,500", "cpp": 2.0,
        "highlight": "Priority Pass + Chase Sapphire Lounge; $300 travel credit; 10x travel via portal; 3x dining",
        "url_hint": "chase.com/sapphire/reserve",
    },
    {
        "card": "Chase Freedom Unlimited", "bank": "chase", "annual_fee": 0,
        "category": "Best No-Fee Card",
        "offer": "$200 cash bonus", "spend_req": "$500 in 3 months",
        "est_value": "$200+", "cpp": 1.0,
        "highlight": "1.5% on everything; 3x dining & pharmacy; 5x travel via Chase portal; pairs well with CSP/CSR",
        "url_hint": "chase.com/freedom-unlimited",
    },
    {
        "card": "Citi Double Cash", "bank": "citi", "annual_fee": 0,
        "category": "Best No-Fee Cash Back",
        "offer": "$200 cash back", "spend_req": "$1,500 in 6 months",
        "est_value": "$200+", "cpp": 1.0,
        "highlight": "2% on everything (1% purchase + 1% payment); convert to ThankYou points; simple and consistent",
        "url_hint": "citi.com/doublecash",
    },
    {
        "card": "Capital One Venture", "bank": "capital one", "annual_fee": 95,
        "category": "Best Mid-Tier Travel",
        "offer": "75,000 Capital One miles", "spend_req": "$4,000 in 3 months",
        "est_value": "$1,125–$1,500", "cpp": 1.5,
        "highlight": "2x on everything; $100 Global Entry/TSA Pre✓; transfer to 15+ airline partners",
        "url_hint": "capitalone.com/venture",
    },
    {
        "card": "Amex Blue Cash Preferred", "bank": "amex", "annual_fee": 95,
        "category": "Best for Families (Groceries)",
        "offer": "$250 statement credit", "spend_req": "$3,000 in 6 months",
        "est_value": "$250+", "cpp": 1.0,
        "highlight": "6% U.S. supermarkets (up to $6k/yr); 6% streaming; 3% transit & gas; strong for everyday spend",
        "url_hint": "americanexpress.com/bluecash-preferred",
    },
    {
        "card": "Citi AAdvantage Executive", "bank": "citi", "annual_fee": 595,
        "category": "Best for AA Flyers",
        "offer": "70,000 AA miles", "spend_req": "$7,000 in 3 months",
        "est_value": "$1,050–$1,400", "cpp": 1.5,
        "highlight": "Full Admirals Club membership; 10x AA flights; 4x dining & travel; Loyalty points boost",
        "url_hint": "citi.com/aadvantage-executive",
    },
]

# ── Helper functions ──────────────────────────────────────────────────────────

def match_card(name: str) -> str | None:
    """Fuzzy-match a card name string to a CARD_REWARDS key. Returns key or None."""
    nl = name.lower().strip()
    if nl in CARD_REWARDS:
        return nl
    # Substring: key inside name or name inside key
    for key in CARD_REWARDS:
        if key in nl or nl in key:
            return key
    # Word overlap (need ≥2 matching words)
    name_words = set(nl.split())
    best_key, best_score = None, 0
    for key in CARD_REWARDS:
        overlap = len(name_words & set(key.split()))
        if overlap > best_score:
            best_score, best_key = overlap, key
    return best_key if best_score >= 2 else None


def best_card_per_category(user_keys: list[str]) -> dict[str, tuple[str, float]]:
    """Return {category: (best_card_key, effective_cpp)} from a list of card keys."""
    result: dict[str, tuple[str, float]] = {}
    for cat_label, cat_key in SPEND_CATEGORIES:
        best_key, best_cpp = None, 0.0
        for key in user_keys:
            card = CARD_REWARDS[key]
            mult = card["categories"].get(cat_key, card["categories"].get("other", 1))
            cpp  = mult * card["point_value"] / 100
            if cpp > best_cpp:
                best_cpp, best_key = cpp, key
        if best_key:
            result[cat_key] = (best_key, best_cpp)
    return result


def calc_annual_rewards(monthly_spend: dict[str, float], card_key: str) -> float:
    """Estimate annual rewards value ($) for a card given monthly spend by category."""
    card = CARD_REWARDS[card_key]
    total = 0.0
    for cat_label, cat_key in SPEND_CATEGORIES:
        spend = monthly_spend.get(cat_key, 0.0)
        mult  = card["categories"].get(cat_key, card["categories"].get("other", 1))
        total += spend * mult * (card["point_value"] / 100)
    return total * 12


def user_lounge_networks(user_keys: list[str]) -> set[str]:
    """Return all lounge networks accessible from the given card keys."""
    networks: set[str] = set()
    for key in user_keys:
        networks.update(CARD_REWARDS[key].get("lounge_networks", []))
    return networks

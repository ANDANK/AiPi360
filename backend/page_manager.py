"""
Page visibility, feature flags, and maintenance mode for AiPi360.

Settings are stored in Google Sheets tab "AppSettings" (key, value columns)
and fall back to data/app_settings.json when GSheets is unavailable.

Key schema
──────────
  page:{page_key}:user            "true" / "false"
  feature:{page_key}:{feat}:user  "true" / "false"
  maintenance:enabled             "true" / "false"
  maintenance:message             any string

Role rules (hardcoded, not configurable)
─────────────────────────────────────────
  admin  → always sees everything (all pages, all features)
  user   → sees pages/features gated by settings above
  kid    → sees ONLY the Kids page (all others blocked)
"""
import os
import json

import pandas as pd
import streamlit as st

_DATA_DIR      = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_SETTINGS_FILE = os.path.join(_DATA_DIR, "app_settings.json")
_GS_TAB        = "AppSettings"
_CACHE_KEY     = "_app_settings_cache"

_MAINT_DEFAULT = "🚧 We're updating AiPi360. Check back soon!"


# ── Page & feature registry ───────────────────────────────────────────────────

PAGES = [
    {"key": "kids",      "label": "🧒 Kids",           "kid_required": True},
    {"key": "insurance", "label": "🛡️ Insurance",       "kid_required": False},
    {"key": "cc_points", "label": "💳 CC & Points",     "kid_required": False},
    {"key": "travel",    "label": "✈️ Travel",          "kid_required": False},
    {"key": "calendar",  "label": "📅 Calendar",        "kid_required": False},
    {"key": "accounts",      "label": "📊 Account Tracker", "kid_required": False},
    {"key": "portfolio",     "label": "💼 Portfolio",       "kid_required": False},
    {"key": "destinations",  "label": "🗺️ Destinations",   "kid_required": False},
]

PAGE_FEATURES: dict[str, list[tuple[str, str]]] = {
    "kids": [
        ("syllabus",   "📚 Syllabus & Curriculum Plan"),
        ("staar",      "📝 STAAR Practice Tests"),
        ("math_rocks", "🏆 Math Rocks Competitions"),
        ("calendar",   "📅 School Calendar"),
        ("reminders",  "🔔 Reminders"),
    ],
    "insurance": [
        ("policies",       "📋 Policy List"),
        ("renewal_alerts", "🔔 Renewal Alerts"),
        ("comparison",     "📊 Policy Comparison"),
    ],
    "cc_points": [
        ("cards",   "💳 Card List"),
        ("offers",  "🎁 Offers Tracker"),
        ("rewards", "💰 Rewards Summary"),
        ("lounge",  "🛋️ Lounge Access"),
    ],
    "travel": [
        ("trips",    "✈️ My Trips"),
        ("deals",    "🔍 Deal Finder"),
        ("hotels",   "🏨 Hotels"),
        ("points",   "💎 Points Redemption"),
    ],
    "calendar": [
        ("reminders", "🔔 All Reminders"),
        ("events",    "📅 Events View"),
        ("school",    "🏫 School Calendar"),
    ],
    "accounts": [
        ("balance",     "📥 Balance Input"),
        ("analytics",   "📊 Analytics"),
        ("projections", "🔮 Projections"),
        ("management",  "🏦 Account Management"),
        ("alerts",      "🔔 Market Alerts"),
    ],
}


# ── Defaults ──────────────────────────────────────────────────────────────────

def _defaults() -> dict:
    d: dict[str, str] = {}
    for p in PAGES:
        # User role: all pages on by default
        d[f"page:{p['key']}:user"] = "true"
        for fk, _ in PAGE_FEATURES.get(p["key"], []):
            d[f"feature:{p['key']}:{fk}:user"] = "true"
    d["maintenance:enabled"] = "false"
    d["maintenance:message"] = _MAINT_DEFAULT
    return d


# ── GSheets backend ───────────────────────────────────────────────────────────

def _gs_read() -> dict | None:
    try:
        from backend.gsheet import read_sheet
        df = read_sheet(_GS_TAB)
        if df.empty or "key" not in df.columns or "value" not in df.columns:
            return None
        return {str(r["key"]).strip(): str(r["value"])
                for _, r in df.iterrows()
                if str(r.get("key", "")).strip()}
    except Exception:
        return None


def _gs_save(data: dict) -> bool:
    try:
        from backend.gsheet import overwrite_sheet, refresh_cache
        rows = [{"key": k, "value": str(v)} for k, v in data.items()]
        df   = pd.DataFrame(rows, columns=["key", "value"])
        overwrite_sheet(_GS_TAB, df)
        refresh_cache()
        return True
    except Exception:
        return False


# ── Local JSON backend ────────────────────────────────────────────────────────

def _disk_read() -> dict:
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _disk_save(data: dict) -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Unified load / save ───────────────────────────────────────────────────────

def load_settings() -> dict:
    if _CACHE_KEY in st.session_state:
        return st.session_state[_CACHE_KEY]
    data = _defaults()
    gs = _gs_read()
    if gs is not None:
        data.update(gs)
    else:
        data.update(_disk_read())
    st.session_state[_CACHE_KEY] = data
    return data


def save_settings(data: dict) -> None:
    merged = _defaults()
    merged.update(data)
    if not _gs_save(merged):
        _disk_save(merged)
    st.session_state[_CACHE_KEY] = merged


def invalidate_cache() -> None:
    st.session_state.pop(_CACHE_KEY, None)


# ── Public API — runtime checks ───────────────────────────────────────────────

def is_page_visible(page_key: str) -> bool:
    role = st.session_state.get("role", "user")
    if role == "admin":
        return True
    if role == "kid":
        return page_key == "kids"
    s = load_settings()
    return s.get(f"page:{page_key}:user", "true").lower() not in ("false", "0", "no")


def get_feature_flag(page_key: str, feature_key: str) -> bool:
    role = st.session_state.get("role", "user")
    if role == "admin":
        return True
    if role == "kid":
        return page_key == "kids"
    s = load_settings()
    return s.get(f"feature:{page_key}:{feature_key}:user", "true").lower() not in ("false", "0", "no")


def is_maintenance_mode() -> bool:
    s = load_settings()
    return s.get("maintenance:enabled", "false").lower() in ("true", "1", "yes")


def get_maintenance_message() -> str:
    s = load_settings()
    return s.get("maintenance:message", _MAINT_DEFAULT)


def check_maintenance() -> None:
    """Show maintenance page and stop if maintenance is on (admin is exempt)."""
    role = st.session_state.get("role", "user")
    if role == "admin":
        return
    if is_maintenance_mode():
        msg = get_maintenance_message()
        # Hide sidebar on maintenance screen
        st.markdown(
            "<style>[data-testid='stSidebar'],[data-testid='stSidebarNav'],"
            "[data-testid='collapsedControl']{display:none!important}</style>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="max-width:560px;margin:80px auto;text-align:center;'
            f'background:#fef3c7;border:2px solid #f59e0b;border-radius:16px;padding:48px 40px;">'
            f'<div style="font-size:52px;margin-bottom:16px">🚧</div>'
            f'<div style="font-size:22px;font-weight:800;color:#92400e;margin-bottom:12px;'
            f'letter-spacing:-0.02em">Site Under Maintenance</div>'
            f'<div style="font-size:14px;color:#78350f;line-height:1.6">{msg}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.stop()


def check_page_access(page_key: str) -> None:
    """Block access if role doesn't have permission to view this page."""
    role = st.session_state.get("role", "user")
    if role == "admin":
        return
    if role == "kid" and page_key != "kids":
        st.markdown(
            '<div style="max-width:500px;margin:80px auto;text-align:center;'
            'background:#f0fdf4;border:2px solid #86efac;border-radius:16px;padding:40px;">'
            '<div style="font-size:48px;margin-bottom:12px">🧒</div>'
            '<div style="font-size:20px;font-weight:800;color:#166534;margin-bottom:8px">'
            'Kids Mode Active</div>'
            '<div style="font-size:14px;color:#15803d">This page is not part of Kids mode.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="← Back to Home")
        st.stop()
    if not is_page_visible(page_key):
        st.warning("🔒 This page has been disabled by the administrator.")
        st.page_link("app.py", label="← Back to Home")
        st.stop()

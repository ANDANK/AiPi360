"""
Password-based auth with three roles.

  ADMIN_PASSWORD  → role "admin"  — full access + Admin page
  USER_PASSWORD   → role "user"   — all pages, respects page settings
  KID_PASSWORD    → role "kid"    — Kids page only
  PASSWORD        → role "user"   — legacy single-password fallback

Session state keys:  authenticated (bool), role (str)
"""
import streamlit as st


# ── CSS ───────────────────────────────────────────────────────────────────────

_LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
/* Hide sidebar entirely on login screen */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"] { display: none !important; }
.login-wrap {
    max-width: 380px; margin: 80px auto 0 auto;
    padding: 40px 36px; background: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
}
.login-logo {
    font-family: 'Inter', sans-serif;
    font-size: 28px; font-weight: 800;
    color: #0f172a; letter-spacing: -0.04em;
    text-align: center; margin-bottom: 4px;
}
.login-logo span { color: #2563eb; }
.login-sub {
    font-family: 'Inter', sans-serif;
    font-size: 13px; color: #64748b;
    text-align: center; margin-bottom: 28px;
}
</style>
"""

# Base: hide ALL nav items immediately — prevents any flash of restricted pages.
# Role CSS then explicitly shows only what is permitted.
_NAV_HIDE_ALL = (
    "<style>[data-testid='stSidebarNav'] ul li{display:none!important}</style>"
)

# Maps page_key → the href fragment Streamlit uses in the sidebar nav
_PAGE_HREF = {
    "kids":         "Kids",
    "insurance":    "Insurance",
    "cc_points":    "CC_Points",
    "travel":       "Travel",
    "calendar":     "Calendar",
    "accounts":     "Account_Tracker",
    "portfolio":    "Portfolio",
    "destinations": "Destinations",
}

ROLE_LABELS = {
    "admin": ("🔒", "Admin",  "#7c3aed", "#ede9fe"),
    "user":  ("👤", "User",   "#2563eb", "#eff6ff"),
    "kid":   ("🧒", "Kid",    "#059669", "#f0fdf4"),
}


# ── Public helpers ────────────────────────────────────────────────────────────

def get_role() -> str:
    """Return the current user's role: 'admin', 'user', or 'kid'."""
    return st.session_state.get("role", "user")


def _inject_role_css() -> None:
    role = get_role()

    # Step 1 — hide ALL nav items (applied atomically with step 2, prevents flash)
    st.markdown(_NAV_HIDE_ALL, unsafe_allow_html=True)

    if role == "admin":
        # Admin sees everything — un-hide all items
        st.markdown(
            "<style>[data-testid='stSidebarNav'] ul li{display:flex!important}</style>",
            unsafe_allow_html=True,
        )
        return

    if role == "kid":
        # Kid sees only Home + Kids
        st.markdown("""<style>
[data-testid="stSidebarNav"] ul li:first-child,
[data-testid="stSidebarNav"] ul li:has(a[href*="Kids"]) { display: flex !important; }
</style>""", unsafe_allow_html=True)
        return

    # User role — hardcoded allowed pages (safe default; expand when needed)
    # Pattern mirrors kid role. Change _USER_ALLOWED_HREFS to grant more pages.
    _USER_ALLOWED_HREFS = ["Destinations"]   # ← add hrefs here to grant access
    show_selectors = (
        ["[data-testid='stSidebarNav'] ul li:first-child"]  # always show Home
        + [
            f'[data-testid="stSidebarNav"] ul li:has(a[href*="{href}"])'
            for href in _USER_ALLOWED_HREFS
        ]
    )
    st.markdown(
        f"<style>{', '.join(show_selectors)} {{ display: flex !important; }}</style>",
        unsafe_allow_html=True,
    )


# ── Role badge in sidebar ─────────────────────────────────────────────────────

def render_role_badge() -> None:
    role = get_role()
    icon, label, color, bg = ROLE_LABELS.get(role, ("👤", "User", "#2563eb", "#eff6ff"))
    st.markdown(
        f'<div style="background:{bg};border-radius:8px;padding:6px 12px;'
        f'font-size:12px;font-weight:600;color:{color};margin-bottom:4px;">'
        f'{icon} {label}</div>',
        unsafe_allow_html=True,
    )


# ── Core auth ─────────────────────────────────────────────────────────────────

def require_auth() -> None:
    """Show login gate if not authenticated; inject role CSS if authenticated."""
    if st.session_state.get("authenticated"):
        _inject_role_css()
        return

    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="login-wrap">'
        '<div class="login-logo">Ai<span>Pi</span>360</div>'
        '<div class="login-sub">Family Command Center</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    col = st.columns([1, 2, 1])[1]
    with col:
        pwd = st.text_input("Password", type="password",
                            label_visibility="collapsed",
                            placeholder="Enter password…")
        if st.button("Sign In", use_container_width=True, type="primary"):
            _check_password(pwd)
    st.stop()


def _check_password(pwd: str) -> None:
    s = st.secrets
    # Preference order: ADMIN > USER > KID > legacy PASSWORD
    if pwd and pwd == s.get("ADMIN_PASSWORD", ""):
        _login("admin")
    elif pwd and pwd == s.get("USER_PASSWORD", ""):
        _login("user")
    elif pwd and pwd == s.get("KID_PASSWORD", ""):
        _login("kid")
    elif pwd and pwd == s.get("PASSWORD", ""):
        _login("user")   # legacy fallback
    else:
        st.error("Incorrect password.")


def _login(role: str) -> None:
    st.session_state.authenticated = True
    st.session_state.role = role
    # Clear page-settings cache so fresh load happens after login
    st.session_state.pop("_app_settings_cache", None)
    st.rerun()


def require_admin() -> None:
    """Call at the top of admin-only pages."""
    require_auth()
    if get_role() != "admin":
        st.warning("🔒 This page requires Admin access.")
        st.page_link("app.py", label="← Back to Home")
        st.stop()


def sign_out() -> None:
    for key in ("authenticated", "role", "_app_settings_cache"):
        st.session_state.pop(key, None)
    st.rerun()

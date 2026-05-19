"""Password-based auth using Streamlit secrets."""
import streamlit as st


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
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


def require_auth():
    if st.session_state.get("authenticated"):
        return
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="login-wrap">'
        '<div class="login-logo">Ai<span>Pi</span>360</div>'
        '<div class="login-sub">Family Command Center</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    col = st.columns([1, 2, 1])[1]
    with col:
        pwd = st.text_input("Password", type="password", label_visibility="collapsed",
                            placeholder="Enter password…")
        if st.button("Sign In", use_container_width=True, type="primary"):
            if pwd == st.secrets.get("PASSWORD", ""):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()


def sign_out():
    st.session_state.authenticated = False
    st.rerun()

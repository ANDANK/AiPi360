"""Shared CSS helpers injected via st.markdown."""
import streamlit as st


_3D_TAB_CSS = """
<style>
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border-radius: 10px 10px 0 0 !important;
    border: 1px solid #b8c8d8 !important;
    border-bottom: 3px solid #e2e8f0 !important;
    background: linear-gradient(180deg, #f1f5f9 0%, #dde6ef 100%) !important;
    padding: 10px 22px !important;
    margin-right: 4px !important;
    box-shadow: 1px -2px 5px rgba(0,0,0,0.09),
                inset 0 1px 1px rgba(255,255,255,0.80) !important;
    transform: translateY(2px) !important;
    transition: all 0.12s ease !important;
    color: #64748b !important;
    position: relative !important;
}
button[data-baseweb="tab"]:hover {
    background: linear-gradient(180deg, #ffffff 0%, #c8d8e8 100%) !important;
    transform: translateY(1px) !important;
    color: #334155 !important;
    border-color: #94a3b8 !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%) !important;
    border: 1px solid rgba(16,185,129,0.45) !important;
    border-bottom: 3px solid #ffffff !important;
    color: #059669 !important;
    font-weight: 700 !important;
    box-shadow: 2px -3px 8px rgba(0,0,0,0.13),
                inset 0 2px 2px rgba(255,255,255,1) !important;
    transform: translateY(0px) !important;
    z-index: 10 !important;
}
</style>
"""


def inject_3d_tab_css() -> None:
    """Inject 3D-raised tab styling site-wide."""
    st.markdown(_3D_TAB_CSS, unsafe_allow_html=True)

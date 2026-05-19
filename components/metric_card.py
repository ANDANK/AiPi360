"""Reusable metric card and nav card components."""
import streamlit as st


def metric_card(
    label: str,
    value: str,
    sub: str = "",
    icon: str = "",
    color: str = "#2563eb",
    bg: str = "#eff6ff",
) -> None:
    st.markdown(
        f"""<div style="background:{bg};border-radius:12px;padding:16px 20px;
            border-left:4px solid {color};margin-bottom:8px;">
          <div style="font-size:12px;color:#64748b;font-weight:500;margin-bottom:4px;">
            {icon} {label}
          </div>
          <div style="font-size:24px;font-weight:700;color:#0f172a;letter-spacing:-0.03em;">
            {value}
          </div>
          {"<div style='font-size:12px;color:#64748b;margin-top:2px;'>" + sub + "</div>" if sub else ""}
        </div>""",
        unsafe_allow_html=True,
    )


def nav_card(
    icon: str,
    title: str,
    description: str,
    badge: str = "",
    badge_color: str = "#dc2626",
) -> bool:
    """Renders a clickable navigation card. Returns True if clicked."""
    badge_html = (
        f"<span style='background:{badge_color};color:#fff;border-radius:10px;"
        f"padding:2px 8px;font-size:11px;font-weight:600;margin-left:8px;'>{badge}</span>"
        if badge else ""
    )
    st.markdown(
        f"""<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;
            padding:20px;cursor:pointer;transition:box-shadow 0.2s;
            box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
          <div style="font-size:16px;font-weight:700;color:#0f172a;">
            {title}{badge_html}
          </div>
          <div style="font-size:13px;color:#64748b;margin-top:4px;">{description}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    return st.button(f"Open {title}", key=f"nav_{title}", use_container_width=True,
                     label_visibility="collapsed")


def section_header(icon: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""<div style="margin-bottom:20px;">
          <div style="font-size:26px;font-weight:800;color:#0f172a;letter-spacing:-0.04em;">
            {icon} {title}
          </div>
          {"<div style='font-size:13px;color:#64748b;margin-top:2px;'>" + subtitle + "</div>" if subtitle else ""}
        </div>""",
        unsafe_allow_html=True,
    )


def coming_soon(feature: str) -> None:
    st.markdown(
        f"""<div style="text-align:center;padding:60px 20px;background:#f8fafc;
            border-radius:16px;border:2px dashed #e2e8f0;">
          <div style="font-size:40px;margin-bottom:12px;">🚧</div>
          <div style="font-size:18px;font-weight:700;color:#0f172a;">{feature}</div>
          <div style="font-size:14px;color:#64748b;margin-top:6px;">
            This section is being built. Check back soon.
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

"""Reusable reminder banner — shows urgent/upcoming reminders from the sheet."""
import streamlit as st
import pandas as pd
from datetime import date, timedelta


_URGENCY_COLORS = {
    "overdue":  ("#fef2f2", "#dc2626", "🚨"),
    "today":    ("#fff7ed", "#ea580c", "🔔"),
    "soon":     ("#fefce8", "#ca8a04", "⏰"),
    "upcoming": ("#f0fdf4", "#16a34a", "📅"),
}


def _classify(due: date) -> str:
    today = date.today()
    delta = (due - today).days
    if delta < 0:        return "overdue"
    elif delta == 0:     return "today"
    elif delta <= 3:     return "soon"
    else:                return "upcoming"


def render_reminder_banner(df: pd.DataFrame, max_show: int = 5) -> None:
    """
    df must have columns: title, message, due_date, section, status
    Renders a compact banner for active reminders due within 7 days.
    """
    if df.empty:
        return

    df = df.copy()
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    cutoff = date.today() + timedelta(days=7)
    active = df[
        (df["status"].str.upper() != "DONE") &
        (df["due_date"].notna()) &
        (df["due_date"] <= cutoff)
    ].sort_values("due_date")

    if active.empty:
        return

    st.markdown("#### 🔔 Reminders")
    shown = active.head(max_show)
    cols = st.columns(min(len(shown), 3))
    for i, (_, row) in enumerate(shown.iterrows()):
        urgency = _classify(row["due_date"])
        bg, color, icon = _urgency_colors = _URGENCY_COLORS[urgency]
        delta = (row["due_date"] - date.today()).days
        if delta < 0:
            when = f"{abs(delta)}d overdue"
        elif delta == 0:
            when = "Today"
        elif delta == 1:
            when = "Tomorrow"
        else:
            when = f"In {delta} days"

        with cols[i % 3]:
            st.markdown(
                f"""<div style="background:{bg};border-left:4px solid {color};
                    border-radius:8px;padding:10px 14px;margin-bottom:8px;">
                  <div style="font-size:12px;color:{color};font-weight:600;margin-bottom:2px;">
                    {icon} {row.get('section','').upper()} · {when}
                  </div>
                  <div style="font-size:14px;font-weight:600;color:#0f172a;">{row['title']}</div>
                  <div style="font-size:12px;color:#64748b;margin-top:2px;">{row.get('message','')}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    if len(active) > max_show:
        st.caption(f"+ {len(active) - max_show} more reminders — see Calendar page for full list.")


def render_section_reminders(df: pd.DataFrame, section: str) -> None:
    """Filter by section and render compact banner."""
    if df.empty:
        return
    sec_df = df[df["section"].str.lower() == section.lower()]
    render_reminder_banner(sec_df)

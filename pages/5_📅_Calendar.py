"""Calendar & Reminders — consolidated across all sections."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="AiPi360 · Calendar", page_icon="📅", layout="wide")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
require_auth()
check_maintenance()
check_page_access("calendar")

from components.metric_card import section_header
from services.reminders import get_all, add, mark_done, delete
from backend.gsheet import read_sheet

SECTIONS   = ["All", "kids", "fisd", "school", "insurance", "cc", "travel", "accounts", "tamil", "general"]
FREQ_OPTS  = ["once", "daily", "weekly", "monthly", "yearly"]
CHAN_OPTS  = ["push", "email", "push,email"]
REMIND_DAYS = [0, 1, 3, 7, 14, 30]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.rem-row {
    display:flex; align-items:center; gap:12px;
    padding:10px 14px; background:#fff;
    border:1px solid #e2e8f0; border-radius:10px; margin-bottom:6px;
}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.markdown("---")
    st.markdown("**Filter by Section**")
    sel_section = st.selectbox("Section", SECTIONS, label_visibility="collapsed")

section_header("📅", "Calendar & Reminders", "All reminders, events & important dates in one place")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Timeline", "📋 All Reminders", "➕ Add Reminder", "📆 7-Day View", "📚 Class Schedule"])

# ── Timeline ──────────────────────────────────────────────────────────────────
with tab1:
    import plotly.graph_objects as go

    today     = date.today()
    tl_start  = today - timedelta(days=3)
    tl_end    = today + timedelta(days=30)

    CAT_ORDER  = ["SCHOOL", "MONEY", "TRAVEL", "FAMILY", "ADMIN"]
    CAT_FILL   = {"SCHOOL": "#ff7675", "MONEY": "#fdcb6e", "TRAVEL": "#55efc4",
                  "FAMILY": "#74b9ff", "ADMIN": "#c77dff"}
    CAT_BORDER = {"SCHOOL": "#d63031", "MONEY": "#e17055", "TRAVEL": "#00b894",
                  "FAMILY": "#2980b9", "ADMIN": "#6c5ce7"}
    SEC_TO_CAT = {
        "school": "SCHOOL", "fisd": "SCHOOL", "kids": "SCHOOL", "tamil": "SCHOOL",
        "insurance": "MONEY", "cc": "MONEY", "accounts": "MONEY",
        "travel": "TRAVEL", "family": "FAMILY",
        "general": "ADMIN", "admin": "ADMIN",
    }

    # Gather events
    tl_events = []

    # From reminders
    try:
        rem_all = read_sheet("reminders")
        if not rem_all.empty:
            rem_all["due_date"] = pd.to_datetime(rem_all["due_date"], errors="coerce").dt.date
            active = rem_all[
                (rem_all["status"].str.upper() != "DONE") &
                rem_all["due_date"].notna()
            ]
            for _, r in active.iterrows():
                d = r["due_date"]
                if tl_start <= d <= tl_end:
                    cat = SEC_TO_CAT.get(str(r.get("section", "")).lower(), "ADMIN")
                    tl_events.append({"date": d, "label": str(r["title"])[:14],
                                      "cat": cat, "tip": str(r["title"])})
    except Exception:
        pass

    # From upcoming class sessions
    try:
        from services.kids import upcoming_sessions as _uc
        for s in _uc(days_ahead=30):
            tl_events.append({"date": s["date"],
                               "label": s["class"][:12],
                               "cat": "SCHOOL",
                               "tip": f"{s['class']} ({s['child']})"})
    except Exception:
        pass

    # STAAR exam dates
    try:
        from services.staar_prep import STAAR_DATES_2026
        for sd in STAAR_DATES_2026:
            d = sd["date"]
            if tl_start <= d <= tl_end:
                tl_events.append({"date": d,
                                   "label": f"★{sd['label']} G{sd['grades']}",
                                   "cat": "SCHOOL", "tip": sd["full"]})
    except Exception:
        pass

    # ── Build Plotly figure ────────────────────────────────────────────────────
    fig = go.Figure()

    # Invisible scatter to set axis ranges
    fig.add_trace(go.Scatter(
        x=[pd.Timestamp(tl_start), pd.Timestamp(tl_end)],
        y=[0, len(CAT_ORDER) - 1],
        mode="markers", marker_opacity=0,
        showlegend=False, hoverinfo="skip",
    ))

    # Category row bands
    for i, cat in enumerate(CAT_ORDER):
        fig.add_shape(type="rect", layer="below",
                      x0=pd.Timestamp(tl_start), x1=pd.Timestamp(tl_end),
                      y0=i - 0.45, y1=i + 0.45,
                      fillcolor="#161b22" if i % 2 == 0 else "#0d1117",
                      line_width=0)
        fig.add_annotation(x=pd.Timestamp(tl_start), y=i,
                           text=cat, showarrow=False,
                           font=dict(size=10, color="#8b949e", family="monospace"),
                           xanchor="right", xshift=-6)

    # Today line
    fig.add_shape(type="line",
                  x0=pd.Timestamp(today), x1=pd.Timestamp(today),
                  y0=-0.6, y1=len(CAT_ORDER) - 0.4,
                  line=dict(color="#58a6ff", width=1, dash="dot"))
    fig.add_annotation(x=pd.Timestamp(today), y=-0.58,
                       text="today", showarrow=False,
                       font=dict(size=9, color="#58a6ff", family="monospace"),
                       yanchor="top")

    # Event boxes
    for ev in tl_events:
        cat_y  = CAT_ORDER.index(ev["cat"])
        label  = ev["label"]
        box_w  = max(1.2, len(label) * 0.18)   # days wide
        x0_ts  = pd.Timestamp(ev["date"])
        x1_ts  = x0_ts + pd.Timedelta(days=box_w)
        fig.add_shape(type="rect", layer="above",
                      x0=x0_ts, x1=x1_ts,
                      y0=cat_y - 0.28, y1=cat_y + 0.28,
                      fillcolor=CAT_FILL[ev["cat"]],
                      line_color=CAT_BORDER[ev["cat"]], line_width=1)
        fig.add_trace(go.Scatter(
            x=[(x0_ts + (x1_ts - x0_ts) / 2)],
            y=[cat_y],
            mode="text",
            text=[label],
            textfont=dict(size=9, color="#0d1117", family="monospace"),
            showlegend=False,
            hovertext=[ev["tip"]],
            hoverinfo="text",
        ))

    tl_filter = st.selectbox("Filter category", ["all sources"] + CAT_ORDER,
                             key="tl_filter", label_visibility="collapsed")
    mo_label = today.strftime("%m")

    fig.update_layout(
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(family="monospace", color="#c9d1d9", size=11),
        height=280,
        margin=dict(l=90, r=20, t=46, b=28),
        title=dict(
            text=f"{mo_label} · 30-DAY TIMELINE · WEIGHTED"
                 f"<span style='float:right;font-size:10px;color:#444;'>  {tl_filter}</span>",
            font=dict(size=12, color="#8b949e", family="monospace"),
            x=0, y=0.98,
        ),
        xaxis=dict(
            type="date",
            range=[pd.Timestamp(tl_start), pd.Timestamp(tl_end)],
            showgrid=True, gridcolor="#21262d", gridwidth=1,
            tickformat="%d", tickfont=dict(size=10, color="#8b949e"),
            dtick=86400000 * 2,   # every 2 days
            zeroline=False, showline=False,
        ),
        yaxis=dict(
            range=[-0.7, len(CAT_ORDER) - 0.3],
            showgrid=False, showticklabels=False,
            zeroline=False,
        ),
        showlegend=False,
        hovermode="closest",
    )

    # Apply category filter
    if tl_filter != "all sources":
        filtered = [e for e in tl_events if e["cat"] == tl_filter]
        tl_events[:] = filtered

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── STAAR dates callout ─────────────────────────────────────────────────────
    try:
        from services.staar_prep import STAAR_DATES_2026 as _SD
        upcoming_staar = [s for s in _SD if today <= s["date"] <= tl_end]
        if upcoming_staar:
            st.markdown("**★ STAAR Dates in this window**")
            for s in upcoming_staar:
                delta = (s["date"] - today).days
                badge = f"🔔 Today" if delta == 0 else f"📅 in {delta}d — {s['date'].strftime('%b %d')}"
                st.markdown(
                    f"""<div style="background:#1c2128;border:1px solid #ffd700;border-radius:8px;
                        padding:8px 14px;margin-bottom:4px;display:flex;gap:12px;align-items:center;">
                      <span style="color:#ffd700;font-weight:700;font-size:12px;">{badge}</span>
                      <span style="font-size:13px;color:#e6edf3;">{s['full']}</span>
                    </div>""", unsafe_allow_html=True)
            if st.button("➕ Add STAAR dates to Reminders", key="add_staar_rem"):
                from services.reminders import add as _radd
                for s in _SD:
                    _radd("school", s["full"], f"STAAR {s['subject']} — Grades {s['grades']}",
                          s["date"], 7, "once", "push,email")
                st.success("STAAR exam dates added to reminders!")
                st.rerun()
    except Exception:
        pass

# ── All Reminders ─────────────────────────────────────────────────────────────
with tab2:
    try:
        df = read_sheet("reminders")
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.info("No reminders yet. Add your first in the 'Add Reminder' tab.")
    else:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date

        if sel_section != "All":
            df = df[df["section"].str.lower() == sel_section.lower()]

        show_done = st.checkbox("Show completed reminders", value=False)
        if not show_done:
            df = df[df["status"].str.upper() != "DONE"]

        df = df.sort_values("due_date", na_position="last")

        if df.empty:
            st.success("✅ All clear — no active reminders in this section.")
        else:
            today = date.today()
            for _, r in df.iterrows():
                due = r.get("due_date")
                if due:
                    delta = (due - today).days
                    if delta < 0:
                        color, badge = "#dc2626", f"🚨 {abs(delta)}d overdue"
                    elif delta == 0:
                        color, badge = "#ea580c", "🔔 Today"
                    elif delta <= 3:
                        color, badge = "#ca8a04", f"⏰ {delta}d"
                    else:
                        color, badge = "#16a34a", f"📅 {delta}d"
                else:
                    color, badge = "#94a3b8", "No date"

                c1, c2, c3, c4, c5 = st.columns([0.8, 2.5, 1.5, 1, 1])
                with c1:
                    st.markdown(f"<span style='color:{color};font-weight:600;font-size:12px;'>{badge}</span>",
                                unsafe_allow_html=True)
                with c2:
                    st.markdown(f"**{r['title']}**")
                    if r.get("message"):
                        st.caption(r["message"])
                with c3:
                    st.caption(f"{r.get('section','').upper()} · {r.get('frequency','once')}")
                with c4:
                    if st.button("✅ Done", key=f"done_{r['id']}"):
                        mark_done(r["id"])
                        st.rerun()
                with c5:
                    if st.button("🗑️", key=f"del_{r['id']}", help="Delete"):
                        delete(r["id"])
                        st.rerun()

# ── Add Reminder ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### ➕ Add New Reminder")
    with st.form("add_reminder_form"):
        c1, c2 = st.columns(2)
        with c1:
            r_section  = st.selectbox("Section", SECTIONS[1:])
            r_title    = st.text_input("Title *")
            r_message  = st.text_area("Details / Message", height=80)
        with c2:
            r_due      = st.date_input("Due Date", value=date.today())
            r_remind   = st.selectbox("Remind me (days before)", REMIND_DAYS, index=1)
            r_freq     = st.selectbox("Frequency", FREQ_OPTS)
            r_channels = st.selectbox("Notify via", CHAN_OPTS)

        submitted = st.form_submit_button("➕ Add Reminder", type="primary")
        if submitted:
            if r_title:
                add(r_section, r_title, r_message, r_due, r_remind, r_freq, r_channels)
                st.success(f"✅ Reminder added: {r_title}")
                st.rerun()
            else:
                st.error("Title is required.")

    st.markdown("---")
    st.markdown("#### 🔔 Notification Settings")
    with st.expander("Test notifications"):
        if st.button("📧 Send test notification"):
            try:
                from backend.notifications import test_notifications
                result = test_notifications()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

# ── 7-Day View ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("#### 📆 Next 7 Days")
    try:
        all_df = read_sheet("reminders")
        if all_df.empty:
            st.info("No reminders to show.")
        else:
            all_df["due_date"] = pd.to_datetime(all_df["due_date"], errors="coerce").dt.date
            today   = date.today()
            cutoff  = today + timedelta(days=7)

            # Include STAAR dates in 7-day view
            staar_items = []
            try:
                from services.staar_prep import STAAR_DATES_2026
                for sd in STAAR_DATES_2026:
                    if today <= sd["date"] <= cutoff:
                        staar_items.append({"due_date": sd["date"], "title": sd["full"],
                                            "section": "school", "message": f"Grades {sd['grades']}"})
            except Exception:
                pass

            week_df = all_df[
                (all_df["status"].str.upper() != "DONE") &
                (all_df["due_date"].notna()) &
                (all_df["due_date"] >= today) &
                (all_df["due_date"] <= cutoff)
            ].sort_values("due_date")

            all_items = list(week_df.to_dict("records")) + staar_items
            all_items.sort(key=lambda x: x["due_date"])

            if not all_items:
                st.success("✅ Nothing due in the next 7 days!")
            else:
                current_day = None
                today_dt = date.today()
                for r in all_items:
                    d = r["due_date"]
                    if d != current_day:
                        current_day = d
                        delta = (d - today_dt).days
                        day_label = "Today" if delta == 0 else ("Tomorrow" if delta == 1
                                    else d.strftime("%A, %b %d"))
                        st.markdown(f"**{day_label}**")
                    is_staar = "STAAR" in str(r.get("title", ""))
                    bg_staar = "background:#1c2128;border:1px solid #ffd700;" if is_staar else "background:#fff;border:1px solid #e2e8f0;"
                    sec_color = "#ffd700" if is_staar else "#1d4ed8"
                    sec_bg    = "#3d2e00" if is_staar else "#dbeafe"
                    st.markdown(
                        f"""<div style="margin-left:16px;padding:8px 12px;{bg_staar}border-radius:8px;
                            margin-bottom:4px;display:flex;gap:12px;align-items:center;">
                          <span style="font-size:12px;background:{sec_bg};color:{sec_color};
                            border-radius:10px;padding:2px 8px;">{r.get('section','').upper()}</span>
                          <span style="font-size:13px;font-weight:600;color:{'#ffd700' if is_staar else '#0f172a'};">
                            {'★ ' if is_staar else ''}{r['title']}</span>
                          <span style="font-size:12px;color:#64748b;margin-left:auto;">{r.get('message','')}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.error(f"Could not load reminders: {e}")

# ── Class Schedule ─────────────────────────────────────────────────────────────
with tab5:
    st.markdown("#### 📚 Upcoming Class Schedule")
    try:
        from services.kids import upcoming_sessions, CHILDREN
        days_ahead = st.slider("Show next N days", min_value=7, max_value=60, value=21, step=7)

        child_filter = st.radio("Child", ["All"] + CHILDREN, horizontal=True, key="cal_child_filter")
        child_arg = None if child_filter == "All" else child_filter

        sessions = upcoming_sessions(child=child_arg, days_ahead=days_ahead)

        if not sessions:
            st.info("No class sessions found. Add classes with day/time in the Kids section.")
        else:
            today = date.today()
            cur_date = None
            CHILD_COLOR = {"Son": ("#eff6ff", "#2563eb"), "Daughter": ("#fdf4ff", "#9333ea")}

            for s in sessions:
                if s["date"] != cur_date:
                    cur_date = s["date"]
                    delta = (cur_date - today).days
                    dlabel = "Today" if delta == 0 else (
                        "Tomorrow" if delta == 1 else cur_date.strftime("%A, %b %d"))
                    st.markdown(f"**{dlabel}**")

                bg, color = CHILD_COLOR.get(s["child"], ("#f8fafc", "#64748b"))
                time_str = f"🕐 {s['time_start']}–{s['time_end']}" if s["time_start"] else ""
                loc_str  = f"📍 {s['location']}"               if s["location"]  else ""
                child_badge = f'<span style="font-size:11px;background:{color};color:#fff;border-radius:10px;padding:2px 8px;margin-right:6px;">{s["child"]}</span>'

                st.markdown(
                    f"""<div style="margin-left:16px;padding:9px 14px;background:{bg};
                        border-left:3px solid {color};border-radius:8px;margin-bottom:5px;
                        display:flex;gap:14px;align-items:center;flex-wrap:wrap;">
                      {child_badge}
                      <span style="font-size:13px;font-weight:600;color:#0f172a;">{s['class']}</span>
                      <span style="font-size:12px;color:#64748b;">{s['provider']}</span>
                      <span style="font-size:12px;color:{color};">{time_str}</span>
                      <span style="font-size:12px;color:#64748b;margin-left:auto;">{loc_str}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception as e:
        st.error(f"Could not load class schedule: {e}")

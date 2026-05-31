"""Kids section — Son (Grade 6/7/8) and Daughter."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime as _dt

st.set_page_config(page_title="AiPi360 · Kids", page_icon="🧒", layout="wide")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
from components.styles import inject_3d_tab_css
require_auth()
check_maintenance()
check_page_access("kids")
inject_3d_tab_css()

from components.metric_card import section_header, coming_soon
from components.reminder_banner import render_section_reminders
from services.kids import (list_classes, add_class, update_class, delete_class,
                           toggle_pause, monthly_cost, upcoming_sessions,
                           best_match_index,
                           FREQUENCIES, FEE_FREQUENCIES, DAYS_OF_WEEK)
from backend.gsheet import read_sheet

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.grade-badge {
    display:inline-block; background:#dbeafe; color:#1d4ed8;
    border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700;
    margin-bottom:12px;
}
.topic-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:12px;
    padding:16px; margin-bottom:8px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

section_header("🧒", "Kids", "School, activities & planning for Son and Daughter")

# ── Reminders ─────────────────────────────────────────────────────────────────
try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "kids")
except Exception:
    pass

# ── Top-level tabs ────────────────────────────────────────────────────────────
child_tab1, child_tab2 = st.tabs(["👦 Son", "👧 Daughter"])

# ═══════════════════════════════════════════════════════════════════════════════
# SON
# ═══════════════════════════════════════════════════════════════════════════════
with child_tab1:
    st.markdown('<div class="grade-badge">Currently Grade 6 · 2026-2027</div>', unsafe_allow_html=True)

    g6, g7, g8, tamil_tab, classes_tab, comp_tab, uil_tab, tests_tab, chess_tab = st.tabs(["📘 Grade 6", "📗 Grade 7", "📙 Grade 8", "🕉️ Tamil School", "📋 Classes & Fees", "🏆 Competitions", "🏅 UIL Study Center", "📝 Practice Tests", "♟️ Chess"])

    # ── Grade 6 ───────────────────────────────────────────────────────────────
    with g6:
        st.markdown("### 📘 Grade 6 — FISD")
        sub1, sub2, sub3, sub4, sub5 = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🔢 Math Rocks", "🌟 Planning Ahead", "🏆 Comp Prep"])

        with sub1:
            st.markdown("#### 📅 Syllabus & Plan — Grade 6 at Wortham Intermediate")

            # ── School info strip ─────────────────────────────────────────────
            st.markdown("""
<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;
     padding:12px 18px;margin-bottom:14px;display:flex;gap:32px;flex-wrap:wrap;font-size:13px;">
  <div><b>🏫 School</b><br>Wortham Intermediate</div>
  <div><b>📍 Address</b><br>7404 Kickapoo Dr, McKinney TX 75070</div>
  <div><b>📞 Phone</b><br>469.633.3475</div>
  <div><b>📧 Email</b><br>wortham@friscoisd.org</div>
  <div><b>🎓 Grade</b><br>6th Grade · 2026-2027</div>
  <div><b>🗓️ First Day</b><br>August 12, 2026</div>
</div>""", unsafe_allow_html=True)

            # ── Two sections: Calendar + Curriculum + Tests ───────────────────
            cal_section, curr_section, test_section = st.tabs([
                "📅 School Calendar", "📚 TEKS Curriculum", "📝 Tests & Assessments"
            ])

            with curr_section:
                import html as _html
                from services.g6_teks import (
                    MONTHLY_PACING, SUBJECT_STYLE, STAAR_INFO, TEA_CODES,
                    STAAR_STRAND_MAP, MONTHLY_RESOURCES, month_key,
                )

                st.markdown("""
<div style="background:#fefce8;border:1px solid #fde047;border-radius:10px;
     padding:10px 16px;margin-bottom:16px;font-size:13px;">
  <b>📋 Texas Essential Knowledge and Skills (TEKS)</b> — Grade 6 · FISD 2026-2027<br>
  <span style="color:#713f12;">Monthly pacing is a guide; actual classroom pace may vary by teacher.
  Source: Texas Education Agency official TEKS standards.</span>
</div>""", unsafe_allow_html=True)

                # ── View toggle ───────────────────────────────────────────────
                view_mode = st.radio(
                    "View",
                    ["📅 By Month", "📚 By Subject"],
                    horizontal=True,
                    key="teks_view_mode",
                    label_visibility="collapsed",
                )

                subjects = list(MONTHLY_PACING.keys())
                months_list = [m for m, _ in MONTHLY_PACING["Math"]]

                def _strip_topic_prefix(t: str) -> str:
                    """Strip leading ⚠️ (2 codepoints) or ★ (1 codepoint) + space."""
                    if t.startswith("⚠️"):
                        return t[2:].lstrip(" ")
                    if t.startswith("★"):
                        return t[1:].lstrip(" ")
                    return t

                if view_mode == "📅 By Month":
                    # Month selector
                    month_labels = [m.split("\n")[0] for m in months_list]
                    sel_month_idx = st.select_slider(
                        "Select Month",
                        options=list(range(len(month_labels))),
                        format_func=lambda i: month_labels[i],
                        key="teks_month_slider",
                    )
                    sel_month = months_list[sel_month_idx]
                    mk = month_key(sel_month)

                    # Show 4 subject cards side by side (2x2 grid)
                    st.markdown(f"##### {sel_month.replace(chr(10), ' — ')}")
                    col_a, col_b = st.columns(2)
                    for idx, subj in enumerate(subjects):
                        col = col_a if idx % 2 == 0 else col_b
                        style = SUBJECT_STYLE[subj]
                        # Match by month abbreviation so Science/SS labels (different subtitles) still resolve
                        topics = next(
                            (t for m, t in MONTHLY_PACING[subj] if month_key(m) == mk), []
                        )
                        # Build topic rows with escaped text
                        topic_html = ""
                        for t in topics:
                            is_warn = t.startswith("⚠️")
                            is_star = t.startswith("★")
                            icon   = "⚠️" if is_warn else ("★" if is_star else "•")
                            color  = "#b45309" if (is_warn or is_star) else "#1e293b"
                            text   = _html.escape(_strip_topic_prefix(t))
                            topic_html += (
                                f'<div style="padding:4px 0;border-bottom:1px solid #f1f5f9;'
                                f'font-size:12.5px;color:{color};">'
                                f'{icon} {text}</div>'
                            )
                        # STAAR / TEA strand badge
                        strand = STAAR_STRAND_MAP.get(subj, {}).get(mk, "")
                        strand_badge = ""
                        if strand:
                            is_staar = subj in ("Math", "ELA")
                            b_bg  = style["tag_bg"]
                            b_col = style["tag_color"]
                            label = ("★ STAAR: " if is_staar else "📋 TEA: ") + strand
                            strand_badge = (
                                f'<div style="font-size:10px;color:{b_col};background:{b_bg};'
                                f'border-radius:4px;padding:2px 7px;display:inline-block;'
                                f'margin:4px 0 6px 0;font-weight:600;">'
                                f'{_html.escape(label)}</div>'
                            )
                        card_html = (
                            f'<div style="background:{style["bg"]};border:1px solid {style["border"]};'
                            f'border-radius:12px;padding:14px;margin-bottom:12px;">'
                            f'<div style="font-size:13px;font-weight:700;color:{style["border"]};'
                            f'margin-bottom:6px;">{style["icon"]} {subj}</div>'
                            f'<div style="font-size:10px;color:{style["tag_color"]};'
                            f'background:{style["tag_bg"]};border-radius:6px;'
                            f'padding:2px 8px;display:inline-block;margin-bottom:4px;">'
                            f'{TEA_CODES[subj]}</div>'
                            + strand_badge
                            + topic_html
                            + '</div>'
                        )
                        col.markdown(card_html, unsafe_allow_html=True)

                else:  # By Subject
                    _SRC_COLORS = {
                        "Khan Academy":          ("#e0f2fe", "#0369a1", "🎓"),
                        "YouTube":               ("#fee2e2", "#b91c1c", "▶"),
                        "YouTube (Crash Course)":("#fee2e2", "#b91c1c", "▶"),
                        "TEA.gov":               ("#f0fdf4", "#15803d", "📋"),
                        "IXL":                   ("#fdf4ff", "#9333ea", "✏️"),
                        "CK-12":                 ("#f0fdf4", "#15803d", "📗"),
                        "CommonLit":             ("#fdf4ff", "#9333ea", "📖"),
                        "ReadWorks":             ("#fdf4ff", "#9333ea", "📖"),
                        "Purdue OWL":            ("#fefce8", "#92400e", "🦉"),
                        "Goodreads":             ("#fefce8", "#92400e", "📚"),
                        "Quizlet":               ("#e0f2fe", "#0369a1", "🃏"),
                    }

                    subj_tabs = st.tabs([
                        f"{SUBJECT_STYLE[s]['icon']} {s}" for s in subjects
                    ])
                    for tab, subj in zip(subj_tabs, subjects):
                        with tab:
                            style = SUBJECT_STYLE[subj]
                            st.markdown(
                                f'<div style="font-size:11px;color:{style["tag_color"]};'
                                f'background:{style["tag_bg"]};border-radius:6px;'
                                f'padding:3px 10px;display:inline-block;margin-bottom:12px;">'
                                f'{TEA_CODES[subj]}</div>',
                                unsafe_allow_html=True,
                            )
                            for month_label, topics in MONTHLY_PACING[subj]:
                                hdr = month_label.replace("\n", " — ")
                                mk  = month_key(month_label)
                                strand = STAAR_STRAND_MAP.get(subj, {}).get(mk, "")
                                with st.expander(hdr, expanded=False):
                                    # Strand badge at top
                                    if strand:
                                        is_staar = subj in ("Math", "ELA")
                                        label = ("★ STAAR: " if is_staar else "📋 TEA TEKS: ") + strand
                                        st.markdown(
                                            f'<div style="font-size:10.5px;color:{style["tag_color"]};'
                                            f'background:{style["tag_bg"]};border-radius:4px;'
                                            f'padding:2px 8px;display:inline-block;margin-bottom:8px;'
                                            f'font-weight:600;">{_html.escape(label)}</div>',
                                            unsafe_allow_html=True,
                                        )
                                    # Topics
                                    for t in topics:
                                        if t.startswith("★"):
                                            safe = _html.escape(_strip_topic_prefix(t))
                                            st.markdown(
                                                f'<div style="background:#fef9c3;border-left:3px solid #ca8a04;'
                                                f'border-radius:6px;padding:6px 10px;margin:3px 0;'
                                                f'font-size:13px;font-weight:600;">⭐ {safe}</div>',
                                                unsafe_allow_html=True,
                                            )
                                        elif t.startswith("⚠️"):
                                            safe = _html.escape(_strip_topic_prefix(t))
                                            st.markdown(
                                                f'<div style="background:#fff7ed;border-left:3px solid #ea580c;'
                                                f'border-radius:6px;padding:5px 10px;margin:3px 0;'
                                                f'font-size:12px;color:#9a3412;">⚠️ {safe}</div>',
                                                unsafe_allow_html=True,
                                            )
                                        else:
                                            st.markdown(f"• {t}")
                                    # Resources
                                    resources = MONTHLY_RESOURCES.get(subj, {}).get(mk, [])
                                    if resources:
                                        st.markdown(
                                            '<div style="margin-top:10px;padding-top:8px;'
                                            'border-top:1px solid #e2e8f0;font-size:11px;'
                                            'font-weight:700;color:#475569;margin-bottom:4px;">'
                                            '📌 Resources</div>',
                                            unsafe_allow_html=True,
                                        )
                                        chips = ""
                                        for r in resources:
                                            src = r.get("source", "")
                                            bg, fg, icon = _SRC_COLORS.get(src, ("#f1f5f9", "#334155", "🔗"))
                                            t_safe = _html.escape(r["title"])
                                            chips += (
                                                f'<a href="{r["url"]}" target="_blank" '
                                                f'style="display:inline-block;background:{bg};color:{fg};'
                                                f'border-radius:20px;padding:3px 10px;margin:3px 4px 3px 0;'
                                                f'font-size:11.5px;text-decoration:none;font-weight:500;">'
                                                f'{icon} {t_safe}</a>'
                                            )
                                        st.markdown(
                                            f'<div style="line-height:2;">{chips}</div>',
                                            unsafe_allow_html=True,
                                        )

                # ── STAAR info box ────────────────────────────────────────────
                st.markdown("---")
                st.markdown("##### ★ STAAR Tested Subjects — Grade 6")
                scol1, scol2 = st.columns(2)
                for col, (test, info) in zip([scol1, scol2], STAAR_INFO.items()):
                    col.markdown(
                        f"""<div style="background:#fefce8;border:1px solid #fde047;
                            border-radius:12px;padding:14px;height:100%;">
                          <div style="font-weight:700;font-size:13px;margin-bottom:6px;">
                            ★ {test} STAAR</div>
                          <div style="font-size:12px;color:#713f12;margin-bottom:6px;">
                            📅 {info['estimated_date']}</div>
                          <div style="font-size:12px;color:#78350f;margin-bottom:6px;">
                            📋 {info['format']}</div>
                          <div style="font-size:11px;font-weight:600;color:#92400e;margin-bottom:4px;">
                            Key Readiness Standards:</div>
                          {''.join(f'<div style="font-size:11px;color:#7c2d12;padding:2px 0;">• {s}</div>' for s in info['key_readiness_standards'])}
                        </div>""",
                        unsafe_allow_html=True,
                    )

            with cal_section:
                # ── Calendar display ──────────────────────────────────────────
                from services.fisd_calendar import (
                    get_events, upcoming_events, no_school_days,
                    seed_baseline, TYPE_STYLE
                )

                cal_tab1, cal_tab2, cal_tab3, cal_tab4 = st.tabs([
                    "📆 Upcoming", "🔴 No School Days", "📋 Full Calendar", "➕ Add / Manage"
                ])

                with cal_tab1:
                    hdr, btn_col = st.columns([5,1])
                    with hdr:
                        st.markdown("##### 📆 Next 30 Days")
                    with btn_col:
                        if st.button("🔄 Refresh", key="fisd_refresh"):
                            read_sheet.clear() if hasattr(read_sheet, "clear") else None
                            st.rerun()

                    try:
                        up_df = upcoming_events(days=30)
                        if up_df.empty:
                            seeded = seed_baseline()
                            if seeded:
                                st.success(f"✅ Seeded {seeded} baseline FISD dates. Refresh to view.")
                                st.rerun()
                            else:
                                st.info("No upcoming events. Calendar may be loading.")
                        else:
                            today_d = date.today()
                            for _, r in up_df.iterrows():
                                etype  = str(r.get("type","Other"))
                                bg, color, icon = TYPE_STYLE.get(etype, TYPE_STYLE["Other"])
                                delta  = (r["date"] - today_d).days
                                when   = "Today" if delta==0 else (f"Tomorrow" if delta==1 else f"In {delta}d — {r['date'].strftime('%a %b %d')}")
                                source = r.get("source","")
                                est    = " *(est.)*" if "estimated" in str(source) else ""
                                st.markdown(
                                    f"""<div style="background:{bg};border-left:4px solid {color};
                                        border-radius:8px;padding:9px 14px;margin-bottom:5px;
                                        display:flex;align-items:center;gap:14px;">
                                      <span style="min-width:130px;font-size:12px;color:{color};font-weight:600;">{icon} {when}</span>
                                      <span style="font-size:13px;font-weight:600;color:#0f172a;">{r['event']}{est}</span>
                                      <span style="margin-left:auto;font-size:11px;color:#94a3b8;">{etype}</span>
                                    </div>""",
                                    unsafe_allow_html=True,
                                )
                    except Exception as e:
                        st.error(f"Could not load calendar: {e}")

                with cal_tab2:
                    st.markdown("##### 🔴 All No-School Days 2026-2027")
                    try:
                        ns_df = no_school_days()
                        if ns_df.empty:
                            seed_baseline()
                            st.rerun()
                        else:
                            ns_df["date"] = pd.to_datetime(ns_df["date"], errors="coerce").dt.date
                            ns_df["day"]  = pd.to_datetime(ns_df["date"].astype(str)).dt.strftime("%A")
                            st.dataframe(
                                ns_df[["date","day","event","type","source"]].rename(
                                    columns={"date":"Date","day":"Day","event":"Event",
                                             "type":"Type","source":"Source"}
                                ),
                                use_container_width=True, hide_index=True,
                                column_config={"Date": st.column_config.DateColumn(format="MMM DD, YYYY")},
                            )
                            st.caption("*(Est.) = estimated from standard FISD pattern — verify at friscoisd.org*")
                    except Exception as e:
                        st.error(f"Could not load: {e}")

                with cal_tab3:
                    st.markdown("##### 📋 Full 2026-2027 Calendar")
                    try:
                        full_df = get_events("2026-2027")
                        if full_df.empty:
                            st.info("No events yet.")
                        else:
                            full_df["date"] = pd.to_datetime(full_df["date"], errors="coerce").dt.date
                            type_filter = st.multiselect(
                                "Filter by type",
                                options=list(TYPE_STYLE.keys()),
                                default=list(TYPE_STYLE.keys()),
                                key="fisd_type_filter",
                            )
                            filtered = full_df[full_df["type"].isin(type_filter)].sort_values("date")
                            st.dataframe(
                                filtered[["date","event","type","source"]],
                                use_container_width=True, hide_index=True,
                                column_config={"date": st.column_config.DateColumn(format="MMM DD, YYYY")},
                            )
                    except Exception as e:
                        st.error(f"Could not load: {e}")

                with cal_tab4:
                    st.markdown("##### ➕ Add Event Manually")
                    with st.form("fisd_add_event"):
                        c1, c2, c3 = st.columns(3)
                        with c1: ev_name = st.text_input("Event Name")
                        with c2: ev_date = st.date_input("Date", value=date.today())
                        with c3: ev_type = st.selectbox("Type", list(TYPE_STYLE.keys()))
                        if st.form_submit_button("Add Event", type="primary"):
                            if ev_name:
                                from services.fisd_calendar import upsert_event
                                upsert_event(ev_date.isoformat(), ev_name, ev_type, "manual")
                                st.success(f"✅ Added: {ev_name}")
                                st.rerun()

                    st.markdown("---")
                    st.markdown("##### 🔄 Force Re-seed Baseline Dates")
                    st.caption("Use this to reload the standard FISD 2026-2027 holiday pattern.")
                    if st.button("Re-seed baseline dates", type="secondary"):
                        n = seed_baseline(force=True)
                        st.success(f"✅ Re-seeded {n} baseline events.")
                        st.rerun()

                    st.markdown("---")
                    st.markdown("##### 🔔 Add FISD Reminder")
                    with st.form("school_rem_form"):
                        r_title   = st.text_input("Event / Reminder")
                        r_date    = st.date_input("Reminder Date", value=date.today())
                        r_msg     = st.text_area("Details", height=60)
                        r_allday  = st.checkbox("All Day", value=True, key="fisd_rem_allday")
                        if not r_allday:
                            fc1, fc2, fc3 = st.columns([2, 2, 1])
                            with fc1: r_hr  = st.slider("Hour", 1, 12, 9, key="fisd_rem_hr")
                            with fc2: r_min = st.selectbox("Minute", ["00","15","30","45"], key="fisd_rem_min")
                            with fc3: r_ap  = st.radio("", ["AM","PM"], key="fisd_rem_ampm", horizontal=False)
                            r_time = f"{r_hr}:{r_min} {r_ap}"
                        else:
                            r_time = ""
                        if st.form_submit_button("➕ Add Reminder", type="primary"):
                            from services.reminders import add as add_rem
                            add_rem("fisd", r_title, r_msg, r_date, due_time=r_time)
                            st.success("Reminder added!" + (f" @ {r_time}" if r_time else " (All Day)"))
                            st.rerun()

            with test_section:
                st.markdown("#### 📝 Tests & Assessments — 2026-2027")
                st.caption("FISD 6-week assessments, benchmarks, STAAR, and Tamil school unit tests in one view.")

                # ── Data ─────────────────────────────────────────────────────
                _TESTS = [
                    # (date, end_date_or_None, label, category, source, confirmed)
                    # FISD 6-week grading periods
                    ("2026-08-12","2026-09-19","1st Six Weeks",        "6-Week Period","FISD",  True),
                    ("2026-09-22","2026-10-30","2nd Six Weeks",        "6-Week Period","FISD",  True),
                    ("2026-11-02","2026-12-19","3rd Six Weeks",        "6-Week Period","FISD",  True),
                    ("2027-01-06","2027-02-13","4th Six Weeks",        "6-Week Period","FISD",  True),
                    ("2027-02-17","2027-03-26","5th Six Weeks",        "6-Week Period","FISD",  True),
                    ("2027-03-29","2027-05-28","6th Six Weeks",        "6-Week Period","FISD",  True),
                    # Report card days (approx 1 week after period end)
                    ("2026-09-25",None,        "Report Cards — 1st 6wks","Report Card","FISD",  False),
                    ("2026-11-06",None,        "Report Cards — 2nd 6wks","Report Card","FISD",  False),
                    ("2027-01-08",None,        "Report Cards — 3rd 6wks","Report Card","FISD",  False),
                    ("2027-02-19",None,        "Report Cards — 4th 6wks","Report Card","FISD",  False),
                    ("2027-04-02",None,        "Report Cards — 5th 6wks","Report Card","FISD",  False),
                    ("2027-06-04",None,        "Report Cards — 6th 6wks (Final)","Report Card","FISD", False),
                    # Benchmark / common assessments
                    ("2026-10-19","2026-10-23","Benchmark 1 Window",   "Benchmark",   "FISD",  False),
                    ("2027-02-22","2027-02-26","Benchmark 2 Window",   "Benchmark",   "FISD",  False),
                    # STAAR — Grade 6 (Math & RLA, typically late April)
                    ("2027-04-21",None,        "STAAR — Math (Gr. 6)", "STAAR",       "FISD",  False),
                    ("2027-04-23",None,        "STAAR — Reading/Language Arts","STAAR","FISD", False),
                    # Tamil school unit tests (from PTS 2026-2027 PDF)
                    ("2026-09-13",None,        "Tamil Unit Test 1",    "Unit Test",   "Tamil School", True),
                    ("2026-10-25",None,        "Tamil Unit Test 2",    "Unit Test",   "Tamil School", True),
                    ("2026-12-20",None,        "Tamil Unit Test 3 + 6th Week Presentation","Unit Test","Tamil School", True),
                    ("2027-02-14",None,        "Tamil Unit Test 4",    "Unit Test",   "Tamil School", True),
                    ("2027-04-18",None,        "Tamil Final Test",     "Final Test",  "Tamil School", True),
                ]

                _CAT_STYLE = {
                    "6-Week Period": ("#eff6ff","#2563eb","📆"),
                    "Report Card":   ("#f0fdf4","#16a34a","📋"),
                    "Benchmark":     ("#fdf4ff","#7c3aed","📊"),
                    "STAAR":         ("#fff1f2","#dc2626","⭐"),
                    "Unit Test":     ("#fef9c3","#92400e","✏️"),
                    "Final Test":    ("#fff7ed","#c2410c","🏁"),
                }

                today_d = date.today()

                # ── View toggle ───────────────────────────────────────────────
                tv1, tv2 = st.columns([3,1])
                with tv2:
                    src_filter = st.multiselect(
                        "Source", ["FISD","Tamil School"],
                        default=["FISD","Tamil School"], key="test_src_filter",
                        label_visibility="collapsed",
                    )
                with tv1:
                    cat_filter = st.multiselect(
                        "Category", list(_CAT_STYLE.keys()),
                        default=list(_CAT_STYLE.keys()), key="test_cat_filter",
                        label_visibility="collapsed",
                    )

                # ── Upcoming banner (next 3) ──────────────────────────────────
                upcoming_tests = [
                    t for t in _TESTS
                    if date.fromisoformat(t[0]) >= today_d
                    and t[3] in cat_filter and t[4] in src_filter
                ][:3]
                if upcoming_tests:
                    st.markdown("##### 🔔 Up Next")
                    uc = st.columns(len(upcoming_tests))
                    for ci, (ds, de, lbl, cat, src, conf) in enumerate(upcoming_tests):
                        bg, col_c, ico = _CAT_STYLE[cat]
                        d = date.fromisoformat(ds)
                        days_away = (d - today_d).days
                        tag = "Today!" if days_away==0 else (f"In {days_away}d" if days_away<=14 else d.strftime("%b %d"))
                        est = "" if conf else " *(est.)*"
                        uc[ci].markdown(
                            f'<div style="background:{bg};border:1px solid {col_c};border-radius:10px;'
                            f'padding:10px;text-align:center;">'
                            f'<div style="font-size:18px">{ico}</div>'
                            f'<div style="font-size:11px;color:{col_c};font-weight:700;">{tag}</div>'
                            f'<div style="font-size:11px;font-weight:600;margin-top:2px;">{lbl}{est}</div>'
                            f'<div style="font-size:10px;color:#64748b;">{src}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown("")

                # ── Full list ─────────────────────────────────────────────────
                st.markdown("##### 📋 Full Assessment Schedule")
                for ds, de, lbl, cat, src, conf in _TESTS:
                    if cat not in cat_filter or src not in src_filter:
                        continue
                    d       = date.fromisoformat(ds)
                    bg, col_c, ico = _CAT_STYLE[cat]
                    is_past = (date.fromisoformat(de) if de else d) < today_d
                    opacity = "0.5" if is_past else "1"
                    est     = " *(est.)*" if not conf else ""
                    if de:
                        date_str = f"{d.strftime('%b %d')} – {date.fromisoformat(de).strftime('%b %d, %Y')}"
                    else:
                        date_str = d.strftime("%a, %b %d, %Y")
                    src_badge = (
                        f'<span style="font-size:10px;background:#f1f5f9;color:#475569;'
                        f'border-radius:4px;padding:1px 6px;margin-left:6px;">{src}</span>'
                    )
                    st.markdown(
                        f'<div style="background:{bg};border-left:3px solid {col_c};'
                        f'border-radius:6px;padding:7px 12px;margin-bottom:4px;opacity:{opacity};">'
                        f'<span style="font-size:12px;font-weight:600;color:{col_c};">{ico} {date_str}</span>'
                        f'<span style="font-size:12px;color:#1e293b;margin-left:8px;">{lbl}{est}</span>'
                        f'{src_badge}'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                st.caption("FISD report cards & benchmark windows are estimated — verify at portal.friscoisd.org. STAAR dates are est. late April; official dates posted by TEA ~January.")

        with sub2:
            st.markdown("#### 🎯 STAAR Exam Preparation — Grade 6")
            from services.staar_prep import RESOURCES, FLASHCARDS, MINI_TESTS, STUDY_PLAN_G6

            _sp_tabs = st.tabs(["📋 Study Plan", "🃏 Flashcards", "🌐 Resources", "✏️ Mini Tests", "📝 Official Tests"])

            # ── Study Plan ────────────────────────────────────────────────────
            with _sp_tabs[0]:
                st.markdown("##### 📋 Monthly STAAR Prep Schedule — Grade 6")
                st.caption("Aligned to TEKS pacing · STAAR Math & RLA typically in April")
                for mo in STUDY_PLAN_G6:
                    is_staar = "April" in mo["month"]
                    label = f"📅 {mo['month']} — {mo['label']}{' ★ STAAR MONTH' if is_staar else ''}"
                    with st.expander(label, expanded=is_staar):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Math Topics**")
                            for t in mo["math"]:
                                st.markdown(f"• {t}")
                        with c2:
                            st.markdown("**ELA / Reading Topics**")
                            for t in mo["ela"]:
                                st.markdown(f"• {t}")
                        st.info(f"💡 {mo['tip']}")

            # ── Flashcards ────────────────────────────────────────────────────
            with _sp_tabs[1]:
                st.markdown("##### 🃏 Interactive Flashcards")
                fc_sets = list(FLASHCARDS.keys())
                fc_set  = st.selectbox("Flashcard Set", fc_sets, key="g6_fc_set")
                cards   = FLASHCARDS[fc_set]
                total   = len(cards)
                if st.session_state.get("g6_fc_last_set") != fc_set:
                    st.session_state["g6_fc_idx"] = 0
                    st.session_state["g6_fc_revealed"] = False
                    st.session_state["g6_fc_last_set"] = fc_set
                idx  = st.session_state.get("g6_fc_idx", 0)
                card = cards[idx]
                st.markdown(
                    f"""<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:14px;
                        padding:24px;margin-bottom:12px;text-align:center;">
                      <div style="font-size:11px;color:#2563eb;font-weight:600;margin-bottom:8px;">
                        {card['strand'].upper()} &nbsp;·&nbsp; Card {idx+1} of {total}</div>
                      <div style="font-size:18px;font-weight:700;color:#1e3a8a;line-height:1.5;">
                        {card['q']}</div>
                    </div>""", unsafe_allow_html=True)
                if st.session_state.get("g6_fc_revealed"):
                    st.markdown(
                        f"""<div style="background:#f0fdf4;border:2px solid #22c55e;border-radius:14px;
                            padding:20px;white-space:pre-wrap;font-size:14px;color:#14532d;line-height:1.6;">
                          {card['a']}</div>""", unsafe_allow_html=True)
                    if st.button("🔒 Hide Answer", key="g6_fc_hide"):
                        st.session_state["g6_fc_revealed"] = False
                        st.rerun()
                else:
                    if st.button("👁️ Reveal Answer", key="g6_fc_reveal", type="primary"):
                        st.session_state["g6_fc_revealed"] = True
                        st.rerun()
                nav1, nav2, nav3 = st.columns([1, 2, 1])
                with nav1:
                    if st.button("← Prev", key="g6_fc_prev", disabled=(idx == 0)):
                        st.session_state["g6_fc_idx"] = idx - 1
                        st.session_state["g6_fc_revealed"] = False
                        st.rerun()
                with nav2:
                    st.markdown(f"<div style='text-align:center;color:#64748b;font-size:13px;padding-top:8px;'>"
                                f"{idx+1} / {total}</div>", unsafe_allow_html=True)
                with nav3:
                    if st.button("Next →", key="g6_fc_next", disabled=(idx >= total - 1)):
                        st.session_state["g6_fc_idx"] = idx + 1
                        st.session_state["g6_fc_revealed"] = False
                        st.rerun()
                strands = sorted(set(c["strand"] for c in cards))
                st.caption(f"Strands in this set: {' · '.join(strands)}")

            # ── Resources ─────────────────────────────────────────────────────
            with _sp_tabs[2]:
                st.markdown("##### 🌐 Curated STAAR Resources — Grade 6")
                grade_res = RESOURCES.get(6, {})
                for subject, categories in grade_res.items():
                    st.markdown(f"**{subject}**")
                    for cat_name, items in categories.items():
                        with st.expander(f"📂 {cat_name} ({len(items)})"):
                            for item in items:
                                free_badge = ('<span style="background:#dcfce7;color:#15803d;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;font-weight:600;">FREE</span>'
                                             if item["free"] else
                                             '<span style="background:#fee2e2;color:#b91c1c;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;">PAID</span>')
                                st.markdown(
                                    f"""<div style="padding:8px 0;border-bottom:1px solid #f1f5f9;">
                                      <a href="{item['url']}" target="_blank"
                                         style="font-weight:600;font-size:13px;color:#1d4ed8;">{item['name']}</a>
                                      &nbsp;{free_badge}
                                      <div style="font-size:12px;color:#64748b;margin-top:2px;">{item['note']}</div>
                                    </div>""", unsafe_allow_html=True)
                    st.markdown("---")

            # ── Mini Tests ────────────────────────────────────────────────────
            with _sp_tabs[3]:
                import random as _random
                import plotly.graph_objects as _go
                from services.staar_prep import (get_question_pool as _gqp,
                                                  log_staar_result, get_staar_results)

                g6_mt_keys = [k for k in MINI_TESTS if k.startswith("Grade 6")]

                # ── Strand selector + Refresh button side-by-side ─────────────
                hdr_c1, hdr_c2 = st.columns([4, 1])
                with hdr_c1:
                    mt_sel = st.selectbox("Choose a strand test", g6_mt_keys, key="g6_mt_sel",
                                          label_visibility="collapsed")
                with hdr_c2:
                    refresh_clicked = st.button("🔄 New Questions", key="g6_mt_newshuffle",
                                                use_container_width=True)

                pool     = _gqp(mt_sel)
                SAMPLE_N = min(20, len(pool))

                def _fresh_draw(key, p, n):
                    idxs = _random.sample(range(len(p)), n)
                    st.session_state[f"{key}_idxs"]     = idxs
                    st.session_state[f"{key}_answers"]  = [None] * n
                    st.session_state[f"{key}_submitted"] = False

                state_key = "g6_mt"
                if st.session_state.get(f"{state_key}_last_sel") != mt_sel:
                    _fresh_draw(state_key, pool, SAMPLE_N)
                    st.session_state[f"{state_key}_last_sel"] = mt_sel
                if refresh_clicked:
                    _fresh_draw(state_key, pool, SAMPLE_N)
                    st.rerun()

                # ── Performance graph ──────────────────────────────────────────
                try:
                    hist_df = get_staar_results(child="Son", strand=mt_sel)
                    if not hist_df.empty:
                        hist_df["date"] = pd.to_datetime(hist_df["date"], errors="coerce")
                        hist_df = hist_df.sort_values("date").tail(15)
                        hist_df["pct"] = pd.to_numeric(hist_df["pct"], errors="coerce").fillna(0)
                        bar_colors = ["#22c55e" if p >= 80 else "#f59e0b" if p >= 60 else "#ef4444"
                                      for p in hist_df["pct"]]
                        pfig = _go.Figure(_go.Bar(
                            x=hist_df["date"].dt.strftime("%b %d"),
                            y=hist_df["pct"],
                            marker_color=bar_colors,
                            text=[f"{p:.0f}%" for p in hist_df["pct"]],
                            textposition="outside",
                        ))
                        pfig.add_hline(y=80, line_dash="dot", line_color="#22c55e",
                                       annotation_text="80%", annotation_position="right")
                        pfig.update_layout(
                            height=160, margin=dict(l=0, r=40, t=28, b=0),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            yaxis=dict(range=[0, 110], showgrid=True, gridcolor="#e2e8f0",
                                       ticksuffix="%", tickfont=dict(size=10)),
                            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                            title=dict(text=f"Score History — {mt_sel.split('—')[-1].strip()}",
                                       font=dict(size=11, color="#64748b"), x=0),
                            showlegend=False,
                        )
                        st.plotly_chart(pfig, use_container_width=True,
                                        config={"displayModeBar": False})
                    else:
                        st.caption("📊 No score history yet — complete a test to see your progress here.")
                except Exception:
                    pass

                st.markdown(f"##### ✏️ Strand-Level Mini Tests — Grade 6 (STAAR-Style MCQ)")
                st.caption(f"{SAMPLE_N} questions drawn from a pool of {len(pool)} · "
                           f"click **🔄 New Questions** for a different set")

                q_idxs   = st.session_state.get(f"{state_key}_idxs", list(range(SAMPLE_N)))
                questions = [pool[i] for i in q_idxs]
                answers   = st.session_state.get(f"{state_key}_answers", [None] * SAMPLE_N)
                submitted = st.session_state.get(f"{state_key}_submitted", False)

                for i, qdata in enumerate(questions):
                    st.markdown(f"**Q{i+1}. {qdata['q']}**")
                    sel = st.radio(f"q6_{i}", qdata["opts"], index=None,
                                   key=f"g6_mt_{mt_sel}_{q_idxs[i]}_{i}",
                                   label_visibility="collapsed")
                    if sel is not None:
                        answers[i] = qdata["opts"].index(sel)
                    if submitted and answers[i] is not None:
                        correct = (answers[i] == qdata["ans"])
                        bg_c = "#dcfce7" if correct else "#fee2e2"
                        st.markdown(
                            f"""<div style="background:{bg_c};border-radius:8px;padding:8px 12px;
                                margin-bottom:4px;font-size:13px;">
                              {"✅ Correct!" if correct else f'❌ Incorrect. Correct answer: <em>{qdata["opts"][qdata["ans"]]}</em>'}
                              <br><span style="color:#475569;">{qdata['exp']}</span>
                            </div>""", unsafe_allow_html=True)
                    st.markdown("---")
                st.session_state[f"{state_key}_answers"] = answers

                n_answered = sum(1 for a in answers if a is not None)
                if not submitted:
                    st.progress(n_answered / SAMPLE_N,
                                text=f"{n_answered} / {SAMPLE_N} answered")
                    if st.button("Submit Answers", key="g6_mt_submit", type="primary",
                                 disabled=(n_answered < SAMPLE_N)):
                        st.session_state[f"{state_key}_submitted"] = True
                        st.rerun()
                else:
                    score = sum(1 for i, q in enumerate(questions)
                                if answers[i] is not None and answers[i] == q["ans"])
                    pct   = int(score / SAMPLE_N * 100)
                    bg_s  = "#dcfce7" if pct >= 80 else "#fef9c3" if pct >= 60 else "#fee2e2"
                    msg   = "Great job! 🎉" if pct >= 80 else "Keep practicing! 💪" if pct >= 60 else "Review this strand! 📖"
                    st.markdown(
                        f"""<div style="background:{bg_s};border-radius:12px;padding:16px;
                            text-align:center;font-size:16px;font-weight:700;">
                          Score: {score}/{SAMPLE_N} — {pct}% &nbsp; {msg}
                        </div>""", unsafe_allow_html=True)
                    # Save result to tracking sheet
                    try:
                        log_staar_result("Son", 6, mt_sel, score, SAMPLE_N)
                    except Exception:
                        pass
                    c_r1, c_r2 = st.columns(2)
                    with c_r1:
                        if st.button("🔁 Try Same Set Again", key="g6_mt_retry"):
                            st.session_state[f"{state_key}_answers"]  = [None] * SAMPLE_N
                            st.session_state[f"{state_key}_submitted"] = False
                            st.rerun()
                    with c_r2:
                        if st.button("🔄 New Questions", key="g6_mt_retry_new"):
                            _fresh_draw(state_key, pool, SAMPLE_N)
                            st.rerun()

                    # ── STAAR weakness tracker ─────────────────────────────────
                    st.markdown("---")
                    st.markdown("##### 📊 STAAR Strand Performance — This Session")
                    if "staar_strand_scores" not in st.session_state:
                        st.session_state["staar_strand_scores"] = {}
                    _ss = st.session_state["staar_strand_scores"]
                    _ss.setdefault(mt_sel, []).append(score / SAMPLE_N)

                    _strand_weak, _strand_ok = [], []
                    for strand, pcts in sorted(_ss.items()):
                        avg = sum(pcts) / len(pcts)
                        attempts = len(pcts)
                        bar_col = "#16a34a" if avg >= 0.75 else ("#d97706" if avg >= 0.50 else "#dc2626")
                        flag = " ⚠️" if avg < 0.60 else (" ✅" if avg >= 0.75 else "")
                        if avg < 0.60:
                            _strand_weak.append(strand)
                        st.markdown(
                            f'<div style="background:#f8fafc;border-left:3px solid {bar_col};'
                            f'border-radius:6px;padding:6px 12px;margin-bottom:4px;">'
                            f'<div style="display:flex;justify-content:space-between;">'
                            f'<span style="font-size:12px;font-weight:600;">{strand}{flag}</span>'
                            f'<span style="font-size:12px;color:{bar_col};font-weight:700;">{int(avg*100)}% ({attempts} try)</span>'
                            f'</div>'
                            f'<div style="background:#e2e8f0;border-radius:3px;height:5px;margin-top:4px;">'
                            f'<div style="background:{bar_col};width:{int(avg*100)}%;height:5px;border-radius:3px;"></div>'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )
                    if _strand_weak:
                        st.markdown(
                            f'<div style="background:#fff1f2;border:1px solid #fca5a5;border-radius:8px;padding:10px 14px;margin-top:8px;">'
                            f'<b style="color:#dc2626;">🎯 Focus on:</b> {", ".join(_strand_weak)}<br>'
                            f'<span style="font-size:12px;color:#374151;">Score below 60% — practice these strands more before test day.</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            # ── Official Tests ────────────────────────────────────────────────
            with _sp_tabs[4]:
                st.markdown("##### 📝 Official TEA Interactive Tests — Grade 6")
                st.info("Opens in a new tab · exact STAAR format · free · no login needed")
                for t in [
                    {"label": "Grade 6 Math — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-MA-2024-6&skipIntoTest=true&grade=6"},
                    {"label": "Grade 6 RLA — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-ELA-Reading_2024-6&skipIntoTest=true&grade=6"},
                ]:
                    st.markdown(
                        f"""<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;
                            padding:16px;margin-bottom:10px;">
                          <a href="{t['url']}" target="_blank"
                             style="font-size:15px;font-weight:700;color:#1d4ed8;">🔗 {t['label']}</a>
                        </div>""", unsafe_allow_html=True)
                st.markdown("**Released Tests & Keys (PDF)**")
                st.markdown(
                    "- [2023 Grade 6 Math Practice Test](https://tea.texas.gov/student-assessment/staar/"
                    "released-test-questions/2023-staar-redesign-6-math-practice-test.pdf)\n"
                    "- [TEA STAAR Released Questions Hub](https://tea.texas.gov/student-assessment/staar/"
                    "staar-released-test-questions) — all grades & years"
                )

        with sub3:
            st.markdown("#### 🔢 Math Rocks — Competitions, Resources & Practice")
            from services.math_rocks import (
                COMPETITIONS, RESOURCES, QUESTIONS, CATEGORY_META, sample_questions
            )

            mr1, mr2, mr3, mr4 = st.tabs([
                "🏆 Competitions", "📚 Resources", "🧮 Practice Tests", "📊 My Progress"
            ])

            # ── Competitions ──────────────────────────────────────────────────
            with mr1:
                st.markdown("##### 🏆 Math Competitions — McKinney TX 75070 + National")

                _TRAVEL_LABEL = {
                    "local":    ("📍 Within 50 mi",   "#eff6ff","#2563eb"),
                    "online":   ("💻 Online",          "#f0fdf4","#059669"),
                    "state":    ("🤠 Texas",           "#fffbeb","#d97706"),
                    "national": ("✈️ National Travel", "#fff1f2","#dc2626"),
                }
                _THEME_ALL = sorted({th for c in COMPETITIONS for th in c["themes"]})

                cf1, cf2 = st.columns([2,2])
                with cf1:
                    travel_f = st.multiselect("Travel", list(_TRAVEL_LABEL.keys()),
                        default=list(_TRAVEL_LABEL.keys()), key="comp_travel",
                        format_func=lambda k: _TRAVEL_LABEL[k][0])
                with cf2:
                    theme_f  = st.multiselect("Theme", _THEME_ALL,
                        default=_THEME_ALL, key="comp_theme")

                filtered_comps = [
                    c for c in COMPETITIONS
                    if c["travel"] in travel_f and any(t in theme_f for t in c["themes"])
                ]
                st.caption(f"{len(filtered_comps)} competition(s) shown")

                for c in filtered_comps:
                    tl, tbg, tcol = _TRAVEL_LABEL[c["travel"]]
                    badge = f'<span style="font-size:10px;background:{tbg};color:{tcol};border-radius:4px;padding:2px 7px;font-weight:600;">{tl}</span>'
                    best  = f' <span style="font-size:10px;background:#fef9c3;color:#92400e;border-radius:4px;padding:2px 7px;font-weight:600;">{c["badge"]}</span>' if c.get("badge") else ""
                    themes_html = " ".join(
                        f'<span style="font-size:10px;background:#f1f5f9;color:#475569;border-radius:4px;padding:1px 6px;">{t}</span>'
                        for t in c["themes"]
                    )
                    with st.expander(f'{c["name"]} — {c["org"]}'):
                        st.markdown(badge + best + " " + themes_html, unsafe_allow_html=True)
                        cols = st.columns(3)
                        cols[0].markdown(f"**Level**\n\n{c['level']}")
                        cols[1].markdown(f"**Grades**\n\n{c['grades']}")
                        cols[2].markdown(f"**When**\n\n{c['when']}")
                        cols2 = st.columns(2)
                        cols2[0].markdown(f"**Format**\n\n{c['format_detail']}")
                        cols2[1].markdown(f"**Cost**\n\n{c['cost']}")
                        st.markdown(f"📝 {c['notes']}")
                        st.markdown(f"🔗 [Official Website]({c['website']})")

            # ── Resources ──────────────────────────────────────────────────────
            with mr2:
                st.markdown("##### 📚 Resources by Theme & Level")
                _THEMES_RES = sorted({r["theme"] for r in RESOURCES})
                rf1, rf2 = st.columns(2)
                with rf1:
                    rtheme = st.multiselect("Theme", _THEMES_RES, default=_THEMES_RES, key="res_theme")
                with rf2:
                    rlevel = st.multiselect("Level", ["Beginner","Intermediate","Advanced"],
                        default=["Beginner","Intermediate","Advanced"], key="res_level")

                _SRC_COL = {
                    "AoPS":        ("#eff6ff","#2563eb","📘"),
                    "AoPS Wiki":   ("#eff6ff","#2563eb","📘"),
                    "MATHCOUNTS":  ("#fdf4ff","#7c3aed","🏆"),
                    "UIL Texas":   ("#f0fdf4","#059669","🤠"),
                    "Khan Academy":("#fff1f2","#dc2626","🎓"),
                    "YouTube":     ("#fff1f2","#dc2626","▶"),
                    "Brilliant":   ("#fffbeb","#d97706","💡"),
                    "IXL":         ("#fdf4ff","#7c3aed","✏️"),
                    "CK-12":       ("#f0fdf4","#059669","📗"),
                }
                for theme in _THEMES_RES:
                    if theme not in rtheme:
                        continue
                    theme_res = [r for r in RESOURCES if r["theme"] == theme and r["level"].split("–")[0] in " ".join(rlevel)]
                    if not theme_res:
                        continue
                    st.markdown(f"**{theme}**")
                    for r in theme_res:
                        sbg, scol, sico = _SRC_COL.get(r["source"], ("#f1f5f9","#475569","🔗"))
                        st.markdown(
                            f'<div style="background:{sbg};border-left:3px solid {scol};'
                            f'border-radius:6px;padding:8px 12px;margin-bottom:5px;">'
                            f'<a href="{r["url"]}" target="_blank" style="font-size:13px;font-weight:600;color:{scol};text-decoration:none;">'
                            f'{sico} {r["title"]}</a>'
                            f'<span style="font-size:10px;background:white;color:#475569;border-radius:4px;'
                            f'padding:1px 6px;margin-left:8px;">{r["source"]}</span>'
                            f'<span style="font-size:10px;color:#64748b;margin-left:6px;">{r["level"]}</span>'
                            f'<div style="font-size:11.5px;color:#374151;margin-top:3px;">{r["desc"]}</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown("")

            # ── Practice Tests ────────────────────────────────────────────────
            with mr3:
                st.markdown("##### 🧮 Practice Tests — 20 Questions per Category")
                # Init session state
                if "mr_scores" not in st.session_state:
                    st.session_state["mr_scores"] = {k: [] for k in CATEGORY_META}
                if "mr_active" not in st.session_state:
                    st.session_state["mr_active"] = {}
                if "mr_submitted" not in st.session_state:
                    st.session_state["mr_submitted"] = {}

                cat_tabs = st.tabs([CATEGORY_META[k]["label"] for k in CATEGORY_META])

                for tab_idx, (cat, meta) in enumerate(CATEGORY_META.items()):
                    with cat_tabs[tab_idx]:
                        active_key  = f"mr_qs_{cat}"
                        submit_key  = f"mr_done_{cat}"
                        answers_key = f"mr_ans_{cat}"

                        # Load or refresh questions
                        if active_key not in st.session_state:
                            st.session_state[active_key]  = sample_questions(cat, 20)
                            st.session_state[submit_key]  = False
                            st.session_state[answers_key] = {}

                        qs_with_idx = st.session_state[active_key]
                        submitted   = st.session_state[submit_key]

                        # Header row
                        h1, h2 = st.columns([4,1])
                        with h1:
                            st.markdown(f'<span style="font-size:12px;color:{meta["color"]};">{meta["desc"]}</span>', unsafe_allow_html=True)
                        with h2:
                            if st.button("🔀 New Questions", key=f"mr_refresh_{cat}"):
                                st.session_state[active_key]  = sample_questions(cat, 20)
                                st.session_state[submit_key]  = False
                                st.session_state[answers_key] = {}
                                st.rerun()

                        # Render questions
                        with st.form(f"mr_form_{cat}"):
                            ans_map = {}
                            for q_num, (orig_i, q) in enumerate(qs_with_idx):
                                diff_color = {"easy":"#16a34a","medium":"#d97706","hard":"#dc2626"}.get(q.get("diff","medium"),"#64748b")
                                diff_badge = f'<span style="font-size:10px;color:{diff_color};background:#f1f5f9;border-radius:3px;padding:1px 5px;">{q.get("diff","").upper()}</span>'
                                st.markdown(
                                    f'<div style="font-size:13px;font-weight:600;margin-bottom:2px;">'
                                    f'Q{q_num+1}. {q["q"]} {diff_badge}</div>',
                                    unsafe_allow_html=True,
                                )
                                sel = st.radio(
                                    f"q_{cat}_{q_num}",
                                    q["opts"],
                                    index=None,
                                    key=f"mr_radio_{cat}_{orig_i}",
                                    label_visibility="collapsed",
                                    horizontal=True,
                                )
                                ans_map[q_num] = (orig_i, q, sel)

                                if submitted:
                                    correct = sel == q["opts"][q["ans"]]
                                    bg_c    = "#dcfce7" if correct else "#fee2e2"
                                    icon_c  = "✅" if correct else "❌"
                                    exp_txt    = q.get("exp","")
                                    result_txt = "Correct!" if correct else ("Answer: " + q["opts"][q["ans"]])
                                    exp_part   = ("  —  " + exp_txt) if exp_txt else ""
                                    st.markdown(
                                        f'<div style="background:{bg_c};border-radius:6px;padding:6px 10px;font-size:12px;margin-bottom:8px;">'
                                        f'{icon_c} {result_txt}{exp_part}</div>',
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

                            if not submitted:
                                if st.form_submit_button("✅ Submit Answers", type="primary", use_container_width=True):
                                    st.session_state[answers_key] = ans_map
                                    st.session_state[submit_key]  = True
                                    # Score it
                                    n_correct = sum(
                                        1 for _, (oi, q, sel) in ans_map.items()
                                        if sel is not None and sel == q["opts"][q["ans"]]
                                    )
                                    n_answered = sum(1 for _, (oi, q, sel) in ans_map.items() if sel is not None)
                                    st.session_state["mr_scores"][cat].append((n_correct, n_answered))
                                    st.rerun()

                        if submitted:
                            n_correct = sum(
                                1 for _, (oi, q, sel) in st.session_state[answers_key].items()
                                if sel is not None and sel == q["opts"][q["ans"]]
                            )
                            n_total = len(qs_with_idx)
                            pct = int(n_correct / n_total * 100)
                            bar_col = "#16a34a" if pct >= 75 else ("#d97706" if pct >= 50 else "#dc2626")
                            st.markdown(
                                f'<div style="background:{meta["bg"]};border:1px solid {meta["color"]};'
                                f'border-radius:10px;padding:14px;text-align:center;margin:10px 0;">'
                                f'<div style="font-size:22px;font-weight:800;color:{bar_col};">{pct}%</div>'
                                f'<div style="font-size:13px;color:#374151;">{n_correct} / {n_total} correct</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            if st.button("🔀 Try New Questions", key=f"mr_next_{cat}"):
                                st.session_state[active_key]  = sample_questions(cat, 20)
                                st.session_state[submit_key]  = False
                                st.session_state[answers_key] = {}
                                st.rerun()

            # ── My Progress ───────────────────────────────────────────────────
            with mr4:
                st.markdown("##### 📊 My Progress — Session Summary")
                scores = st.session_state.get("mr_scores", {k: [] for k in CATEGORY_META})
                any_data = any(len(v) > 0 for v in scores.values())

                if not any_data:
                    st.info("Complete at least one practice test to see your progress here.")
                else:
                    st.markdown("**Performance by Category** (this session)")
                    weak = []
                    for cat, meta in CATEGORY_META.items():
                        cat_scores = scores.get(cat, [])
                        if not cat_scores:
                            continue
                        totals = [(c, a) for c, a in cat_scores if a > 0]
                        if not totals:
                            continue
                        avg_pct = int(sum(c/a for c,a in totals) / len(totals) * 100)
                        attempts = len(totals)
                        bar_col  = "#16a34a" if avg_pct >= 75 else ("#d97706" if avg_pct >= 50 else "#dc2626")
                        flag     = " ⚠️ Needs Focus" if avg_pct < 60 else (" ✅ Strong" if avg_pct >= 75 else "")
                        if avg_pct < 60:
                            weak.append(meta["label"])
                        bar_w = avg_pct
                        st.markdown(
                            f'<div style="background:{meta["bg"]};border:1px solid {meta["color"]};'
                            f'border-radius:8px;padding:10px 14px;margin-bottom:6px;">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<span style="font-weight:600;font-size:13px;">{meta["label"]}</span>'
                            f'<span style="font-size:13px;font-weight:700;color:{bar_col};">{avg_pct}%{flag}</span>'
                            f'</div>'
                            f'<div style="background:#e2e8f0;border-radius:4px;height:6px;margin-top:6px;">'
                            f'<div style="background:{bar_col};width:{bar_w}%;height:6px;border-radius:4px;"></div>'
                            f'</div>'
                            f'<div style="font-size:11px;color:#64748b;margin-top:3px;">{attempts} attempt(s)</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    if weak:
                        st.markdown("")
                        st.markdown(
                            f'<div style="background:#fff1f2;border:1px solid #fca5a5;border-radius:10px;padding:12px 16px;">'
                            f'<div style="font-weight:700;color:#dc2626;font-size:13px;">🎯 Focus Areas</div>'
                            f'<div style="font-size:12px;color:#374151;margin-top:4px;">'
                            f'Your scores below 60% in: <b>{", ".join(weak)}</b>.<br>'
                            f'Practice those categories 3× before moving to others. '
                            f'Use the Resources tab to find targeted study material.</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.success("Great job! All categories above 60%. Keep pushing for 75%+!")

                    if st.button("🔄 Reset Session Scores", key="mr_reset"):
                        st.session_state["mr_scores"] = {k: [] for k in CATEGORY_META}
                        st.rerun()

        with sub4:
            st.markdown("#### 🌟 Planning Ahead from Grade 6")
            st.markdown("""
<div style="background:#f0fdf4;border-radius:12px;padding:20px;border:1px solid #bbf7d0;">

**Key actions to take in Grade 6:**

| Action | Why | Timeline |
|--------|-----|----------|
| 📐 Pre-Algebra mastery | Qualifies for Algebra-1 in Grade 7 | By end of Grade 6 |
| 📊 Start PSAT awareness | National Merit Scholarship path | Grade 8-10 |
| 🏆 Join UIL competitions | Math, Number Sense, Science | Grade 6+ |
| 🌍 Explore AP prerequisites | Build foundation early | Grade 6-8 |
| 🤝 Community service | Ivy League considers this | Start now |
| 🎖️ Toastmasters Youth Club | Public speaking, competitions | Grade 6+ |

</div>
""", unsafe_allow_html=True)

        with sub5:
            st.markdown("#### 🏆 Competition Prep — Grade 6")
            from services.comp_prep import render_comp_prep as _rcp
            _rcp("grade_6")

    # ── Grade 7 ───────────────────────────────────────────────────────────────
    with g7:
        st.markdown("### 📗 Grade 7 — Planning Ahead")
        st.markdown('<div class="grade-badge">Upcoming · Grade 7</div>', unsafe_allow_html=True)
        g7a, g7b, g7c, g7d = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🌟 High School Prep", "🏆 Comp Prep"])

        with g7a:
            coming_soon("Grade 7 — Syllabus & monthly plan (mirrors Grade 6 structure)")
        with g7b:
            st.markdown("#### 🎯 STAAR Exam Preparation — Grade 7")
            from services.staar_prep import RESOURCES as _STAAR_RES, FLASHCARDS as _STAAR_FC
            _g7_tabs = st.tabs(["🃏 Flashcards", "🌐 Resources", "📝 Official Tests"])

            with _g7_tabs[0]:
                st.markdown("##### 🃏 Grade 7 Math Flashcards")
                g7_cards = _STAAR_FC.get("Grade 7 Math", [])
                g7_total = len(g7_cards)
                if st.session_state.get("g7_fc_idx") is None:
                    st.session_state["g7_fc_idx"] = 0
                if st.session_state.get("g7_fc_revealed") is None:
                    st.session_state["g7_fc_revealed"] = False
                g7_idx  = st.session_state.get("g7_fc_idx", 0)
                g7_card = g7_cards[g7_idx]
                st.markdown(
                    f"""<div style="background:#f0fdf4;border:2px solid #22c55e;border-radius:14px;
                        padding:24px;margin-bottom:12px;text-align:center;">
                      <div style="font-size:11px;color:#15803d;font-weight:600;margin-bottom:8px;">
                        {g7_card['strand'].upper()} &nbsp;·&nbsp; Card {g7_idx+1} of {g7_total}</div>
                      <div style="font-size:18px;font-weight:700;color:#14532d;line-height:1.5;">
                        {g7_card['q']}</div>
                    </div>""", unsafe_allow_html=True)
                if st.session_state.get("g7_fc_revealed"):
                    st.markdown(
                        f"""<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:14px;
                            padding:20px;white-space:pre-wrap;font-size:14px;color:#1e3a8a;line-height:1.6;">
                          {g7_card['a']}</div>""", unsafe_allow_html=True)
                    if st.button("🔒 Hide", key="g7_fc_hide"):
                        st.session_state["g7_fc_revealed"] = False
                        st.rerun()
                else:
                    if st.button("👁️ Reveal Answer", key="g7_fc_reveal", type="primary"):
                        st.session_state["g7_fc_revealed"] = True
                        st.rerun()
                n1, n2, n3 = st.columns([1, 2, 1])
                with n1:
                    if st.button("← Prev", key="g7_fc_prev", disabled=(g7_idx == 0)):
                        st.session_state["g7_fc_idx"] = g7_idx - 1
                        st.session_state["g7_fc_revealed"] = False
                        st.rerun()
                with n2:
                    st.markdown(f"<div style='text-align:center;color:#64748b;font-size:13px;"
                                f"padding-top:8px;'>{g7_idx+1} / {g7_total}</div>", unsafe_allow_html=True)
                with n3:
                    if st.button("Next →", key="g7_fc_next", disabled=(g7_idx >= g7_total - 1)):
                        st.session_state["g7_fc_idx"] = g7_idx + 1
                        st.session_state["g7_fc_revealed"] = False
                        st.rerun()

            with _g7_tabs[1]:
                st.markdown("##### 🌐 Curated STAAR Resources — Grade 7")
                g7_res = _STAAR_RES.get(7, {})
                for subj, cats in g7_res.items():
                    st.markdown(f"**{subj}**")
                    for cat_name, items in cats.items():
                        with st.expander(f"📂 {cat_name} ({len(items)})"):
                            for item in items:
                                free_badge = ('<span style="background:#dcfce7;color:#15803d;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;font-weight:600;">FREE</span>'
                                             if item["free"] else
                                             '<span style="background:#fee2e2;color:#b91c1c;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;">PAID</span>')
                                st.markdown(
                                    f"""<div style="padding:8px 0;border-bottom:1px solid #f1f5f9;">
                                      <a href="{item['url']}" target="_blank"
                                         style="font-weight:600;font-size:13px;color:#1d4ed8;">{item['name']}</a>
                                      &nbsp;{free_badge}
                                      <div style="font-size:12px;color:#64748b;margin-top:2px;">{item['note']}</div>
                                    </div>""", unsafe_allow_html=True)
                    st.markdown("---")

            with _g7_tabs[2]:
                st.markdown("##### 📝 Official TEA Interactive Tests — Grade 7")
                st.info("Opens in a new tab · exact STAAR format · free · no login needed")
                for t in [
                    {"label": "Grade 7 Math — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-MA-2024-7&skipIntoTest=true&grade=7"},
                    {"label": "Grade 7 RLA — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-ELA-Reading_2024-7&skipIntoTest=true&grade=7"},
                ]:
                    st.markdown(
                        f"""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
                            padding:16px;margin-bottom:10px;">
                          <a href="{t['url']}" target="_blank"
                             style="font-size:15px;font-weight:700;color:#15803d;">🔗 {t['label']}</a>
                        </div>""", unsafe_allow_html=True)
                st.markdown(
                    "- [TEA STAAR Released Questions Hub](https://tea.texas.gov/student-assessment/staar/"
                    "staar-released-test-questions) — all grades & years"
                )
        with g7c:
            st.markdown("#### 🎓 High School Preparation from Grade 7")
            st.markdown("""
<div style="background:#eff6ff;border-radius:12px;padding:20px;border:1px solid #bfdbfe;">

**Focus areas for Grade 7:**

| Focus | Details |
|-------|---------|
| 🧮 Algebra 1 | Qualify and excel — foundation for HS math track |
| 🔬 Science Olympiad | Start participating in competitions |
| 💻 Coding / Robotics | FIRST Lego League, robotics clubs |
| 📖 Advanced Reading | AP Language prep starts here |
| 🏅 Honors classes | Position for AP courses in HS |
| 🤝 Volunteering | 20+ hours/year minimum for IV League |

</div>
""", unsafe_allow_html=True)

        with g7d:
            st.markdown("#### 🏆 Competition Prep — Grade 7")
            from services.comp_prep import render_comp_prep as _rcp7
            _rcp7("grade_7")

    # ── Grade 8 ───────────────────────────────────────────────────────────────
    with g8:
        st.markdown("### 📙 Grade 8 — High School Bound")
        st.markdown('<div class="grade-badge">Future · Grade 8</div>', unsafe_allow_html=True)
        g8a, g8b, g8c, g8d = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🚀 HS & Beyond", "🏆 Comp Prep"])

        with g8a:
            coming_soon("Grade 8 — Syllabus & monthly plan")
        with g8b:
            st.markdown("#### 🎯 STAAR Exam Preparation — Grade 8")
            from services.staar_prep import RESOURCES as _STAAR_RES8, FLASHCARDS as _STAAR_FC8
            _g8_tabs = st.tabs(["🃏 Flashcards", "🌐 Resources", "📝 Official Tests"])

            with _g8_tabs[0]:
                st.markdown("##### 🃏 Grade 8 Math Flashcards")
                g8_cards = _STAAR_FC8.get("Grade 8 Math", [])
                g8_total = len(g8_cards)
                if st.session_state.get("g8_fc_idx") is None:
                    st.session_state["g8_fc_idx"] = 0
                if st.session_state.get("g8_fc_revealed") is None:
                    st.session_state["g8_fc_revealed"] = False
                g8_idx  = st.session_state.get("g8_fc_idx", 0)
                g8_card = g8_cards[g8_idx]
                st.markdown(
                    f"""<div style="background:#fef3c7;border:2px solid #f59e0b;border-radius:14px;
                        padding:24px;margin-bottom:12px;text-align:center;">
                      <div style="font-size:11px;color:#b45309;font-weight:600;margin-bottom:8px;">
                        {g8_card['strand'].upper()} &nbsp;·&nbsp; Card {g8_idx+1} of {g8_total}</div>
                      <div style="font-size:18px;font-weight:700;color:#78350f;line-height:1.5;">
                        {g8_card['q']}</div>
                    </div>""", unsafe_allow_html=True)
                if st.session_state.get("g8_fc_revealed"):
                    st.markdown(
                        f"""<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:14px;
                            padding:20px;white-space:pre-wrap;font-size:14px;color:#1e3a8a;line-height:1.6;">
                          {g8_card['a']}</div>""", unsafe_allow_html=True)
                    if st.button("🔒 Hide", key="g8_fc_hide"):
                        st.session_state["g8_fc_revealed"] = False
                        st.rerun()
                else:
                    if st.button("👁️ Reveal Answer", key="g8_fc_reveal", type="primary"):
                        st.session_state["g8_fc_revealed"] = True
                        st.rerun()
                n1, n2, n3 = st.columns([1, 2, 1])
                with n1:
                    if st.button("← Prev", key="g8_fc_prev", disabled=(g8_idx == 0)):
                        st.session_state["g8_fc_idx"] = g8_idx - 1
                        st.session_state["g8_fc_revealed"] = False
                        st.rerun()
                with n2:
                    st.markdown(f"<div style='text-align:center;color:#64748b;font-size:13px;"
                                f"padding-top:8px;'>{g8_idx+1} / {g8_total}</div>", unsafe_allow_html=True)
                with n3:
                    if st.button("Next →", key="g8_fc_next", disabled=(g8_idx >= g8_total - 1)):
                        st.session_state["g8_fc_idx"] = g8_idx + 1
                        st.session_state["g8_fc_revealed"] = False
                        st.rerun()

            with _g8_tabs[1]:
                st.markdown("##### 🌐 Curated STAAR Resources — Grade 8")
                g8_res = _STAAR_RES8.get(8, {})
                for subj, cats in g8_res.items():
                    st.markdown(f"**{subj}**")
                    for cat_name, items in cats.items():
                        with st.expander(f"📂 {cat_name} ({len(items)})"):
                            for item in items:
                                free_badge = ('<span style="background:#dcfce7;color:#15803d;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;font-weight:600;">FREE</span>'
                                             if item["free"] else
                                             '<span style="background:#fee2e2;color:#b91c1c;border-radius:8px;'
                                             'padding:1px 7px;font-size:11px;">PAID</span>')
                                st.markdown(
                                    f"""<div style="padding:8px 0;border-bottom:1px solid #f1f5f9;">
                                      <a href="{item['url']}" target="_blank"
                                         style="font-weight:600;font-size:13px;color:#1d4ed8;">{item['name']}</a>
                                      &nbsp;{free_badge}
                                      <div style="font-size:12px;color:#64748b;margin-top:2px;">{item['note']}</div>
                                    </div>""", unsafe_allow_html=True)
                    st.markdown("---")

            with _g8_tabs[2]:
                st.markdown("##### 📝 Official TEA Interactive Tests — Grade 8")
                st.info("Opens in a new tab · exact STAAR format · free · no login needed")
                for t in [
                    {"label": "Grade 8 Math — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-MA-2024-8&skipIntoTest=true&grade=8"},
                    {"label": "Grade 8 RLA — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-ELA-Reading_2024-8&skipIntoTest=true&grade=8"},
                    {"label": "Grade 8 Science — Interactive Practice Test (TEA)",
                     "url": "https://txpt.cambiumtds.com/student/?testId=TXPT-GEN-PRAC-UD-SC-2024-8&skipIntoTest=true&grade=8"},
                ]:
                    st.markdown(
                        f"""<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:12px;
                            padding:16px;margin-bottom:10px;">
                          <a href="{t['url']}" target="_blank"
                             style="font-size:15px;font-weight:700;color:#b45309;">🔗 {t['label']}</a>
                        </div>""", unsafe_allow_html=True)
                st.markdown(
                    "- [2023 Grade 8 Math Practice Test PDF](https://tea.texas.gov/student-assessment/staar/"
                    "released-test-questions/2023-staar-redesign-8-math-practice-test.pdf)\n"
                    "- [2023 Grade 8 Science Practice Test PDF](https://tea.texas.gov/student-assessment/staar/"
                    "released-test-questions/2023-staar-redesign-8-science-practice-test.pdf)\n"
                    "- [TEA STAAR Released Questions Hub](https://tea.texas.gov/student-assessment/staar/"
                    "staar-released-test-questions)"
                )
        with g8c:
            st.markdown("#### 🚀 Clear Path to High School & Beyond")
            st.markdown("""
<div style="background:#fef3c7;border-radius:12px;padding:20px;border:1px solid #fde68a;">

**Grade 8 checklist for HS readiness:**

| Milestone | Details |
|-----------|---------|
| 📐 Geometry | Complete in Grade 8 for HS Algebra 2 start |
| 🧪 Pre-AP Science | Physics or Chemistry foundations |
| 💪 AP Human Geography | Many schools offer this in Grade 8 |
| 🎤 Leadership roles | Student council, club leadership |
| 🌐 Foreign language | 2+ years by HS entry is ideal |
| 📝 PSAT 8/9 | Take it — establishes baseline |
| 🏆 Certifications | Coding, language certs add weight |

</div>
""", unsafe_allow_html=True)

        with g8d:
            st.markdown("#### 🏆 Competition Prep — Grade 8")
            from services.comp_prep import render_comp_prep as _rcp8
            _rcp8("grade_8")

    # ── Tamil School ──────────────────────────────────────────────────────────
    with tamil_tab:
        st.markdown("### 🕉️ Plano Tamil School — Nilai 6")

        # ── School info bar ───────────────────────────────────────────────────
        st.markdown("""
<div style="background:#fdf4e7;border:1px solid #f59e0b;border-radius:12px;padding:16px 20px;margin-bottom:16px;display:flex;gap:32px;flex-wrap:wrap;">
  <div><span style="font-size:12px;color:#92400e;font-weight:600;">📍 LOCATION</span><br>
    <span style="font-size:13px;">Genstar Montessori<br>10205 Custer Rd, Plano TX 75025</span></div>
  <div><span style="font-size:12px;color:#92400e;font-weight:600;">📅 SCHEDULE</span><br>
    <span style="font-size:13px;">Sundays · 2 hours/class<br>August – May</span></div>
  <div><span style="font-size:12px;color:#92400e;font-weight:600;">🎓 LEVEL</span><br>
    <span style="font-size:13px;">Nilai 6 · Age 11+<br>Year 2026-2027</span></div>
  <div><span style="font-size:12px;color:#92400e;font-weight:600;">📧 CONTACT</span><br>
    <span style="font-size:13px;">sasthatamilfoundation@gmail.com</span></div>
  <div><span style="font-size:12px;color:#92400e;font-weight:600;">🌐 WEBSITE</span><br>
    <a href="https://stfnonprofit.org/Plano-Tamil-School/" target="_blank" style="font-size:13px;">stfnonprofit.org</a></div>
</div>""", unsafe_allow_html=True)

        ts1, ts2, ts3, ts4, ts5 = st.tabs(["📚 Nilai 6 Curriculum", "📅 Calendar", "🏆 Competitions", "🔔 Reminders", "📋 Resources"])

        # ── Nilai 6 Curriculum ────────────────────────────────────────────────
        with ts1:
            st.markdown("#### 📚 Nilai 6 Curriculum — What to Learn This Year")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:12px;">
<div style="font-weight:700;color:#0f172a;margin-bottom:8px;">✍️ Writing</div>
<ul style="margin:0;padding-left:18px;font-size:13px;color:#374151;">
<li>Syntax — letter writing</li>
<li>Short essays</li>
<li>Story composition</li>
<li>Compound words</li>
</ul>
</div>

<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:12px;">
<div style="font-weight:700;color:#0f172a;margin-bottom:8px;">🗣️ Oral Skills</div>
<ul style="margin:0;padding-left:18px;font-size:13px;color:#374151;">
<li>8 lessons / stories</li>
<li>4 songs</li>
<li>6 pieces — Sangam literature & poetry</li>
<li>10 Thirukkural verses</li>
<li>100 vocabulary words</li>
</ul>
</div>""", unsafe_allow_html=True)

            with c2:
                st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:12px;">
<div style="font-weight:700;color:#0f172a;margin-bottom:8px;">📖 Grammar Topics</div>
<ul style="margin:0;padding-left:18px;font-size:13px;color:#374151;">
<li>வினைமுற்று — Finite Verb</li>
<li>பெயரெச்சம் — Adjective Participle</li>
<li>Adjectives & Adverbs (review)</li>
<li>Declension (review)</li>
<li>Continuous tenses (review)</li>
</ul>
</div>

<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-bottom:12px;">
<div style="font-weight:700;color:#0f172a;margin-bottom:8px;">📗 Reading & Speaking</div>
<ul style="margin:0;padding-left:18px;font-size:13px;color:#374151;">
<li>Daily 10+ min reading from class library</li>
<li>Logged reading minutes</li>
<li>2 reading tests per year (graded)</li>
<li>Public speaking — every 6 weeks</li>
<li>One-on-one teacher review before presentations</li>
</ul>
</div>""", unsafe_allow_html=True)

            st.markdown("""
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:14px 18px;margin-top:4px;">
<b>📋 Unit Structure:</b> The year is divided into <b>6 units</b>.
Each unit ends with a student presentation in week 6.
Total: ~6 presentations per school year.
</div>""", unsafe_allow_html=True)

        # ── Calendar ──────────────────────────────────────────────────────────
        with ts2:
            st.markdown("#### 📅 Tamil School Calendar 2026-2027")

            # Full calendar from PDF: Final PTS 2026-2027 calendar.pdf
            _PTS_CALENDAR = [
                # (date_str, unit, class_num, event_type, details)
                # event_type: "class","holiday","special","ptc"
                ("2026-08-09", "Unit 1", "1st Class",  "class",   "First day of school"),
                ("2026-08-16", "Unit 1", "2nd Class",  "class",   ""),
                ("2026-08-23", "Unit 1", "3rd Class",  "class",   ""),
                ("2026-08-30", "Unit 1", "4th Class",  "class",   ""),
                ("2026-09-05", "",       "",            "special", "STF 16th Annual Fundraiser"),
                ("2026-09-06", "",       "",            "holiday", "Labor Day — No Class"),
                ("2026-09-13", "Unit 1", "5th Class",  "class",   "Unit Test 1"),
                ("2026-09-20", "Unit 1", "6th Class",  "class",   "6th Week Presentation & Parent-Teacher Conference"),
                ("2026-09-27", "Unit 2", "1st Class",  "class",   ""),
                ("2026-10-04", "Unit 2", "2nd Class",  "class",   ""),
                ("2026-10-11", "Unit 2", "3rd Class",  "class",   ""),
                ("2026-10-18", "Unit 2", "4th Class",  "class",   ""),
                ("2026-10-25", "Unit 2", "5th Class",  "class",   "Unit Test 2"),
                ("2026-11-01", "Unit 2", "6th Class",  "class",   "6th Week Presentation & Parent-Teacher Conference"),
                ("2026-11-08", "",       "",            "holiday", "Deepavali — No Class"),
                ("2026-11-15", "Unit 3", "1st Class",  "class",   ""),
                ("2026-11-22", "",       "",            "holiday", "Thanksgiving — No Class"),
                ("2026-11-29", "Unit 3", "2nd Class",  "class",   ""),
                ("2026-12-06", "Unit 3", "3rd Class",  "class",   ""),
                ("2026-12-13", "Unit 3", "4th Class",  "class",   ""),
                ("2026-12-20", "Unit 3", "5th & 6th Class", "class", "Unit Test 3 & 6th Week Presentation (combined — Thanksgiving removed 6th class)"),
                ("2026-12-27", "",       "",            "holiday", "Winter Break — No Class"),
                ("2027-01-03", "",       "",            "holiday", "Winter Break — No Class"),
                ("2027-01-07", "",       "",            "ptc",     "Parent-Teacher Conference (online via GMeet) @7PM"),
                ("2027-01-10", "Unit 4", "1st Class",  "class",   ""),
                ("2027-01-17", "",       "",            "holiday", "Thamizhar Thirunal — No Class"),
                ("2027-01-24", "Unit 4", "2nd Class",  "class",   ""),
                ("2027-01-30", "",       "",            "special", "STF 20th Year Thirukkural Competition"),
                ("2027-01-31", "Unit 4", "3rd Class",  "class",   ""),
                ("2027-02-07", "Unit 4", "4th Class",  "class",   ""),
                ("2027-02-14", "Unit 4", "5th Class",  "class",   "Unit Test 4"),
                ("2027-02-21", "Unit 4", "6th Class",  "class",   "6th Week Presentation & Parent-Teacher Conference"),
                ("2027-02-28", "Unit 5", "1st Class",  "class",   "Drama Practice"),
                ("2027-03-07", "Unit 5", "2nd Class",  "class",   "Drama Practice"),
                ("2027-03-14", "",       "",            "holiday", "Spring Break — No Class"),
                ("2027-03-21", "Unit 5", "3rd Class",  "class",   "Drama Practice"),
                ("2027-03-28", "Unit 5", "4th Class",  "class",   "Drama Practice"),
                ("2027-04-04", "Unit 5", "5th Class",  "class",   "Drama Practice"),
                ("2027-04-11", "Unit 5", "6th Class",  "class",   "Annual Day"),
                ("2027-04-18", "Unit 6", "1st Class",  "class",   "Final Test"),
                ("2027-04-25", "Unit 6", "2nd Class",  "class",   "Report Cards & Certificates"),
            ]

            _TYPE_STYLE_TS = {
                "class":   ("#f0fdf4", "#16a34a", "📗"),
                "holiday": ("#fef9c3", "#92400e", "🚫"),
                "special": ("#eff6ff", "#1d4ed8", "🌟"),
                "ptc":     ("#fdf4ff", "#7c3aed", "👩‍🏫"),
            }

            today_d = date.today()

            # ── Upcoming (next 3) ─────────────────────────────────────────────
            upcoming = [
                r for r in _PTS_CALENDAR
                if date.fromisoformat(r[0]) >= today_d
            ][:3]

            if upcoming:
                st.markdown("##### 🔔 Coming Up")
                up_cols = st.columns(len(upcoming))
                for ci, (ds, unit, cls, etype, detail) in enumerate(upcoming):
                    bg, col_c, ico = _TYPE_STYLE_TS[etype]
                    d = date.fromisoformat(ds)
                    days_away = (d - today_d).days
                    tag = "Today!" if days_away == 0 else (f"In {days_away}d" if days_away <= 7 else d.strftime("%b %d"))
                    title = detail if detail else (f"{unit} · {cls}" if cls else unit)
                    up_cols[ci].markdown(
                        f'<div style="background:{bg};border:1px solid {col_c};border-radius:10px;padding:12px;text-align:center;">'
                        f'<div style="font-size:18px">{ico}</div>'
                        f'<div style="font-size:11px;color:{col_c};font-weight:700;">{tag}</div>'
                        f'<div style="font-size:12px;font-weight:600;margin-top:2px;">{d.strftime("%a, %b %d")}</div>'
                        f'<div style="font-size:11px;color:#64748b;margin-top:2px;">{title}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")

            # ── Full calendar by unit ─────────────────────────────────────────
            cal_view, holiday_view = st.tabs(["📋 Full Schedule", "🚫 Holidays & Special"])

            with cal_view:
                current_unit = None
                for ds, unit, cls, etype, detail in _PTS_CALENDAR:
                    if unit and unit != current_unit:
                        current_unit = unit
                        st.markdown(f"**── {unit} ──**")
                    d        = date.fromisoformat(ds)
                    bg, col_c, ico = _TYPE_STYLE_TS[etype]
                    is_past  = d < today_d
                    row_bg   = "#f8fafc" if is_past else bg
                    opacity  = "0.55" if is_past else "1"
                    if etype in ("class", "ptc"):
                        label    = cls if cls else "Conference"
                        detail_s = f" — {detail}" if detail else ""
                    else:
                        label    = detail
                        detail_s = ""
                    st.markdown(
                        f'<div style="background:{row_bg};border-left:3px solid {col_c};'
                        f'border-radius:6px;padding:6px 12px;margin-bottom:4px;opacity:{opacity};">'
                        f'<span style="font-size:12px;font-weight:600;color:{col_c};">{ico} {d.strftime("%a, %b %d, %Y")}</span>'
                        f'<span style="font-size:12px;color:#374151;"> · {label}{detail_s}</span>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

            with holiday_view:
                for ds, unit, cls, etype, detail in _PTS_CALENDAR:
                    if etype not in ("holiday", "special"):
                        continue
                    d        = date.fromisoformat(ds)
                    bg, col_c, ico = _TYPE_STYLE_TS[etype]
                    is_past  = d < today_d
                    opacity  = "0.55" if is_past else "1"
                    st.markdown(
                        f'<div style="background:{bg};border-left:3px solid {col_c};'
                        f'border-radius:6px;padding:6px 12px;margin-bottom:4px;opacity:{opacity};">'
                        f'<span style="font-size:12px;font-weight:600;color:{col_c};">{ico} {d.strftime("%a, %b %d, %Y")}</span>'
                        f'<span style="font-size:12px;color:#374151;"> · {detail}</span>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            st.markdown("##### 📌 Known Key Dates (2025-2026 reference)")
            st.markdown("""
| Date | Event |
|------|-------|
| August | 🏫 School year begins |
| Every Sunday | 📚 Regular class (2 hrs) — Genstar Montessori |
| Every 6th week | 🎤 Student presentation day |
| February 7, 2026 | 🏆 19th Thirukkural Competition |
| April | 📝 Registration opens for next year |
| May | 🎓 School year ends / Annual Day |

*Upload the 2026-2027 PDF above to get exact dates for this year.*
""")

        # ── Competitions ──────────────────────────────────────────────────────
        with ts3:
            st.markdown("#### 🏆 Competitions & Events")
            st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:12px;">
<div style="font-size:16px;font-weight:700;margin-bottom:8px;">🏆 Thirukkural Competition</div>
<div style="font-size:13px;color:#374151;">
<b>What:</b> Recite Thirukkural verses — cash prizes awarded<br>
<b>Goal:</b> Improve literary and prose skills through community involvement<br>
<b>Next:</b> February 7, 2026 (19th Annual)<br>
<b>Prep:</b> 10 Thirukkural verses required in Nilai 6 curriculum
</div>
</div>

<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:12px;">
<div style="font-size:16px;font-weight:700;margin-bottom:8px;">📜 Avvai Amudham Competition</div>
<div style="font-size:13px;color:#374151;">
<b>What:</b> Essay and speech competition<br>
<b>Goal:</b> Develop Tamil literary skills<br>
<b>Prep:</b> Practice essay writing and story composition from curriculum
</div>
</div>

<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;margin-bottom:12px;">
<div style="font-size:16px;font-weight:700;margin-bottom:8px;">🎭 Annual Day Performance</div>
<div style="font-size:13px;color:#374151;">
<b>What:</b> Cultural performances — Iyal (literature), Isai (music), Nadagam (drama)<br>
<b>Goal:</b> Showcase Tamil arts and culture<br>
<b>When:</b> Typically May (end of school year)
</div>
</div>

<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;">
<div style="font-size:16px;font-weight:700;margin-bottom:8px;">🎤 Public Speaking (Every 6 Weeks)</div>
<div style="font-size:13px;color:#374151;">
<b>What:</b> Student presentations to class — speeches or performances<br>
<b>Prep:</b> One-on-one teacher review before each presentation<br>
<b>Frequency:</b> ~6 times per school year
</div>
</div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("##### 🎯 Competition Prep Tracker")
            comp_items = [
                ("Thirukkural verses memorized", "10 required", "🏆"),
                ("Sangam literature pieces", "6 required", "📜"),
                ("Songs learned", "4 required", "🎵"),
                ("Vocabulary words", "100 required", "📝"),
                ("Stories / lessons", "8 required", "📖"),
            ]
            for item, target, icon in comp_items:
                c1, c2, c3 = st.columns([3,1,1])
                with c1: st.markdown(f"{icon} {item}")
                with c2: st.caption(target)
                with c3: st.progress(0.0)

        # ── Reminders ─────────────────────────────────────────────────────────
        with ts4:
            st.markdown("#### 🔔 Tamil School Reminders")
            try:
                rem_df_ts = read_sheet("reminders")
                if not rem_df_ts.empty:
                    ts_rems = rem_df_ts[rem_df_ts["section"].str.lower() == "tamil"]
                    if ts_rems.empty:
                        st.info("No Tamil school reminders yet.")
                    else:
                        from components.reminder_banner import render_reminder_banner
                        render_reminder_banner(ts_rems, max_show=10)
                else:
                    st.info("No reminders yet.")
            except Exception:
                st.info("Connect Google Sheets to see reminders.")

            st.markdown("---")
            st.markdown("##### ➕ Add Tamil School Reminder")
            with st.form("tamil_rem_form"):
                r1, r2 = st.columns(2)
                with r1:
                    rt = st.text_input("Reminder Title (e.g. Thirukkural practice)")
                    rm = st.text_area("Details", height=60)
                with r2:
                    rd      = st.date_input("Due Date", value=date.today())
                    rday    = st.selectbox("Remind me (days before)", [0,1,3,7], index=1)
                    rch     = st.selectbox("Notify via", ["push","email","push,email"])
                    all_day = st.checkbox("All Day", value=True, key="tamil_rem_allday")
                if not all_day:
                    tc1, tc2, tc3 = st.columns([2, 2, 1])
                    with tc1: t_hr  = st.slider("Hour", 1, 12, 9, key="tamil_rem_hr")
                    with tc2: t_min = st.selectbox("Minute", ["00","15","30","45"], key="tamil_rem_min")
                    with tc3: t_ap  = st.radio("", ["AM","PM"], key="tamil_rem_ampm", horizontal=False)
                    time_str = f"{t_hr}:{t_min} {t_ap}"
                else:
                    time_str = ""
                if st.form_submit_button("Add Reminder", type="primary"):
                    if rt:
                        from services.reminders import add as add_rem
                        add_rem("tamil", rt, rm, rd, rday, "once", rch, time_str)
                        st.success(f"✅ Added: {rt}" + (f" @ {time_str}" if time_str else " (All Day)"))
                        st.rerun()

        # ── Resources ─────────────────────────────────────────────────────────
        with ts5:
            st.markdown("#### 📋 Resources & Links")
            st.markdown("""
| Resource | Link |
|----------|------|
| 🌐 School Website | [stfnonprofit.org](https://stfnonprofit.org/Plano-Tamil-School/) |
| 👨‍🎓 Student Portal | [Students page](https://stfnonprofit.org/students/) |
| 📚 Grade Levels | [Grade descriptions](https://stfnonprofit.org/students/grade-levels/) |
| 📅 Calendar 2024-25 | [Download PDF](https://stfnonprofit.org/wp-content/uploads/2024/04/Calendar-2024-2025.pdf) |
| 📧 Contact | sasthatamilfoundation@gmail.com |

**Weekly newsletter:** Vaaram Oru Thuli (subscribe via school website)

**Tamil Library:** ~2,000 books available at school — borrow for daily 10-min reading practice
""")
            st.markdown("---")
            st.markdown("##### 📖 Daily Reading Log")
            st.info("Log 10+ minutes of Tamil reading daily — required for Nilai 6 reading grade.")
            with st.form("reading_log"):
                rl1, rl2, rl3 = st.columns(3)
                with rl1: rl_date = st.date_input("Date", value=date.today())
                with rl2: rl_mins = st.number_input("Minutes read", min_value=1, max_value=120, value=10)
                with rl3: rl_book = st.text_input("Book / material")
                if st.form_submit_button("Log Reading", type="primary"):
                    from backend.gsheet import append_row
                    append_row("tamil_reading_log", [rl_date.isoformat(), "Son", rl_mins, rl_book])
                    st.success(f"✅ Logged {rl_mins} minutes")

    # ── Classes & Fees ────────────────────────────────────────────────────────
    with classes_tab:
        st.markdown("### 📋 Classes & Fees Tracker — Son")

        cls_df = list_classes(child="Son")
        monthly = monthly_cost("Son")

        m1, m2, m3 = st.columns(3)
        m1.metric("Active Classes", len(cls_df) if not cls_df.empty else 0)
        m2.metric("Est. Monthly Cost", f"${monthly:,.0f}")
        m3.metric("Est. Annual Cost", f"${monthly*12:,.0f}")

        cl1, cl2, cl3 = st.tabs(["📋 Classes List", "📅 Upcoming Schedule", "➕ Add Class"])

        with cl1:
            def _parse_time(s):
                for fmt in ("%I:%M %p", "%H:%M"):
                    try:
                        return _dt.strptime(str(s).strip(), fmt).time()
                    except (ValueError, TypeError):
                        pass
                return None

            if not cls_df.empty:
                # Header row
                hc = st.columns([2.2, 1.8, 1.6, 1.4, 1.2, 0.75, 0.75, 0.75])
                for col, lbl in zip(hc, ["Class / Provider", "Days", "Time", "Fee", "Meets", "", "", ""]):
                    col.markdown(f"<span style='font-size:11px;font-weight:600;color:#64748b;'>{lbl}</span>",
                                 unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

                for _, cls in cls_df.iterrows():
                    is_paused  = str(cls.get("paused", "FALSE")).upper() == "TRUE"
                    row_op     = "0.55" if is_paused else "1"
                    is_editing = st.session_state.get("son_edit_id") == cls["id"]
                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2.2, 1.8, 1.6, 1.4, 1.2, 0.75, 0.75, 0.75])
                    with c1:
                        badge = ('<span style="background:#fef9c3;color:#854d0e;font-size:10px;'
                                 'border-radius:6px;padding:1px 6px;margin-left:4px;">⏸ paused</span>'
                                 if is_paused else "")
                        st.markdown(
                            f'<div style="opacity:{row_op}">'
                            f'<span style="font-weight:600;font-size:13px;">{cls["name"]}</span>{badge}<br>'
                            f'<span style="font-size:11px;color:#64748b;">{cls.get("provider","")}</span>'
                            f'</div>', unsafe_allow_html=True)
                    with c2:
                        days_disp = str(cls.get("days", "") or "—")
                        loc_disp  = str(cls.get("location", "") or "")
                        st.markdown(
                            f'<div style="font-size:12px;opacity:{row_op}">{days_disp}'
                            + (f'<br><span style="font-size:11px;color:#64748b;">📍 {loc_disp}</span>' if loc_disp else "")
                            + "</div>", unsafe_allow_html=True)
                    with c3:
                        ts = str(cls.get("time_start", "") or "")
                        te = str(cls.get("time_end", "") or "")
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'{"–".join(filter(None,[ts,te])) or "—"}</div>',
                                    unsafe_allow_html=True)
                    with c4:
                        cost = cls.get("cost", 0) or 0
                        ff   = str(cls.get("fee_frequency", "") or "")
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'${float(cost):,.0f}<br>'
                                    f'<span style="font-size:11px;color:#64748b;">{ff}</span></div>',
                                    unsafe_allow_html=True)
                    with c5:
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'{cls.get("frequency","")}</div>', unsafe_allow_html=True)
                    with c6:
                        plbl = "▶" if is_paused else "⏸"
                        if st.button(plbl, key=f"pause_son_{cls['id']}",
                                     help="Resume" if is_paused else "Pause",
                                     use_container_width=True):
                            toggle_pause(cls["id"])
                            st.rerun()
                    with c7:
                        elbl = "✕" if is_editing else "✏️"
                        if st.button(elbl, key=f"edit_son_{cls['id']}",
                                     help="Cancel edit" if is_editing else "Modify",
                                     use_container_width=True):
                            st.session_state["son_edit_id"] = None if is_editing else cls["id"]
                            st.rerun()
                    with c8:
                        if st.button("🗑️", key=f"del_son_{cls['id']}",
                                     help="Delete", use_container_width=True):
                            delete_class(cls["id"])
                            st.session_state.pop("son_edit_id", None)
                            st.rerun()
                    st.markdown("<hr style='margin:2px 0;border-color:#f1f5f9'>",
                                unsafe_allow_html=True)

                    # ── Inline edit form ──────────────────────────────────────
                    if is_editing:
                        st.markdown(
                            f'<div style="background:#eff6ff;border:1px solid #93c5fd;'
                            f'border-radius:10px;padding:14px 18px;margin-bottom:10px;">'
                            f'<b style="font-size:13px;">✏️ Editing: {cls["name"]}</b></div>',
                            unsafe_allow_html=True)
                        with st.form(f"edit_son_{cls['id']}_form"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                e_name  = st.text_input("Class Name", value=str(cls.get("name","")))
                                e_prov  = st.text_input("Provider", value=str(cls.get("provider","")))
                                e_loc   = st.text_input("Location", value=str(cls.get("location","")))
                                try:
                                    e_start_val = date.fromisoformat(str(cls.get("start_date", date.today())))
                                except (ValueError, TypeError):
                                    e_start_val = date.today()
                                e_start = st.date_input("Start Date", value=e_start_val, key=f"son_esd_{cls['id']}")
                            with ec2:
                                e_cost  = st.number_input("Fee Amount ($)",
                                                          value=float(cls.get("cost",0) or 0),
                                                          min_value=0.0, step=5.0)
                                cur_ff  = str(cls.get("fee_frequency",""))
                                e_feef  = st.selectbox("Fee Frequency", FEE_FREQUENCIES,
                                                       index=best_match_index(cur_ff, FEE_FREQUENCIES))
                                cur_fr  = str(cls.get("frequency",""))
                                e_freq  = st.selectbox("Class Meets", FREQUENCIES,
                                                       index=best_match_index(cur_fr, FREQUENCIES))
                            cur_days   = [d.strip() for d in str(cls.get("days","")).split(",") if d.strip() in DAYS_OF_WEEK]
                            e_days     = st.multiselect("Class Days", DAYS_OF_WEEK, default=cur_days,
                                                        key=f"son_edays_{cls['id']}")
                            et1, et2   = st.columns(2)
                            with et1:
                                e_ts = st.time_input("Start Time", value=_parse_time(cls.get("time_start")),
                                                     key=f"son_ets_{cls['id']}")
                            with et2:
                                e_te = st.time_input("End Time", value=_parse_time(cls.get("time_end")),
                                                     key=f"son_ete_{cls['id']}")
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                do_save   = st.form_submit_button("💾 Save Changes", type="primary",
                                                                  use_container_width=True)
                            with sc2:
                                do_cancel = st.form_submit_button("✕ Cancel", use_container_width=True)
                            if do_save:
                                update_class(cls["id"],
                                             name=e_name, provider=e_prov, location=e_loc,
                                             cost=e_cost, fee_frequency=e_feef,
                                             days=",".join(e_days), frequency=e_freq,
                                             start_date=e_start.isoformat(),
                                             time_start=e_ts.strftime("%I:%M %p") if e_ts else "",
                                             time_end=e_te.strftime("%I:%M %p") if e_te else "")
                                st.session_state["son_edit_id"] = None
                                st.rerun()
                            if do_cancel:
                                st.session_state["son_edit_id"] = None
                                st.rerun()

                paused_count = sum(
                    1 for _, r in cls_df.iterrows()
                    if str(r.get("paused","")).upper() == "TRUE"
                )
                if paused_count:
                    st.caption(f"⏸ {paused_count} class(es) paused — excluded from cost & schedule")
            else:
                st.info("No classes yet. Use the ➕ Add Class tab to get started.")

        with cl2:
            sessions = upcoming_sessions(child="Son", days_ahead=21)
            if not sessions:
                if cls_df.empty:
                    st.info("No classes added yet.")
                else:
                    st.info("No classes have day/time set. Add schedule details when creating a class.")
            else:
                st.markdown("##### 📅 Next 21 Days — Son's Classes")
                today_d = date.today()
                cur_date = None
                for s in sessions:
                    if s["date"] != cur_date:
                        cur_date = s["date"]
                        delta = (cur_date - today_d).days
                        dlabel = "Today" if delta == 0 else ("Tomorrow" if delta == 1 else
                                 cur_date.strftime("%A, %b %d"))
                        st.markdown(f"**{dlabel}**")
                    time_str = f"{s['time_start']}–{s['time_end']}" if s['time_start'] else ""
                    loc_str  = f" · 📍 {s['location']}" if s['location'] else ""
                    st.markdown(
                        f"""<div style="margin-left:16px;padding:9px 14px;background:#eff6ff;
                            border-left:3px solid #2563eb;border-radius:8px;margin-bottom:5px;
                            display:flex;gap:14px;align-items:center;flex-wrap:wrap;">
                          <span style="font-size:13px;font-weight:600;color:#1e40af;">{s['class']}</span>
                          <span style="font-size:12px;color:#3b82f6;">{s['provider']}</span>
                          {'<span style="font-size:12px;color:#1d4ed8;">🕐 ' + time_str + '</span>' if time_str else ''}
                          <span style="font-size:12px;color:#64748b;margin-left:auto;">{loc_str}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        with cl3:
            with st.form("add_class_son"):
                st.markdown("##### Class Details")
                c1, c2 = st.columns(2)
                with c1:
                    cname  = st.text_input("Class Name *", placeholder="e.g. Chess, Swim, iTalk")
                    cprov  = st.text_input("Provider / Instructor")
                    cloc   = st.text_input("Location", placeholder="e.g. Rec Center, Online")
                    cstart = st.date_input("Start Date", value=date.today())
                with c2:
                    ccost  = st.number_input("Fee Amount ($)", min_value=0.0, step=5.0,
                                             help="Amount per billing period")
                    cfeef  = st.selectbox("Fee Frequency", FEE_FREQUENCIES,
                                          help="How often this fee is charged")
                    cfreq  = st.selectbox("Class Meets", FREQUENCIES,
                                          help="How often the class actually meets")

                st.markdown("##### Class Days & Time")
                cdays = st.multiselect("Class Days *", DAYS_OF_WEEK,
                                       help="Select all days this class meets each week")
                t1, t2 = st.columns(2)
                with t1:
                    ct_start = st.time_input("Start Time", value=None, key="son_tstart")
                with t2:
                    ct_end   = st.time_input("End Time", value=None, key="son_tend")

                st.markdown("##### Reminders")
                auto_remind = st.checkbox("Auto-add weekly reminder for each class day",
                                          value=True, key="son_autoremind")

                if st.form_submit_button("➕ Add Class", type="primary"):
                    if not cname:
                        st.error("Class name is required.")
                    elif not cdays:
                        st.error("Select at least one class day.")
                    else:
                        days_str = ",".join(cdays)
                        ts_str   = ct_start.strftime("%I:%M %p") if ct_start else ""
                        te_str   = ct_end.strftime("%I:%M %p") if ct_end else ""
                        add_class("Son", cname, cprov, ccost, cfeef, days_str, cfreq, cstart,
                                  time_start=ts_str, time_end=te_str, location=cloc)
                        if auto_remind:
                            from services.reminders import add as add_rem
                            for d in cdays:
                                today_d    = date.today()
                                d_num      = DAYS_OF_WEEK.index(d)
                                days_until = (d_num - today_d.weekday()) % 7
                                next_d     = today_d + timedelta(days=days_until if days_until else 7)
                                detail     = (f"{cprov}" + (f" · {ts_str}–{te_str}" if ts_str else "")
                                              + (f" · {cloc}" if cloc else ""))
                                add_rem("kids", f"📚 {cname} — {d}", detail, next_d,
                                        remind_days=0, frequency="weekly", channels="push")
                        st.success(f"✅ Added: {cname}" + (" · reminders created" if auto_remind else ""))
                        st.rerun()

    # ── Competitions ──────────────────────────────────────────────────────────
    with comp_tab:
        st.markdown("### 🏆 Academic Competitions — Grade 6 through 8")
        st.caption("Competitions spanning Math, Science, Speech & Debate, Writing and more · FISD / Texas focus")

        cm_road, cm_math, cm_sci, cm_speech, cm_write, cm_log = st.tabs([
            "📊 Roadmap", "🔢 Math", "🔬 Science", "🎤 Speech & Debate", "✍️ Writing & Others", "📝 My Results",
        ])

        # ── helper: competition card ──────────────────────────────────────────
        def _comp_card(name, org, grades, when, levels, impact, stars, desc, tip=""):
            star_html  = "⭐" * stars + "☆" * (3 - stars)
            tip_html   = f'<div style="font-size:11px;color:#0369a1;margin-top:6px">💡 {tip}</div>' if tip else ""
            st.markdown(f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;
     padding:14px 16px;margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px">
    <span style="font-size:15px;font-weight:700;color:#1e293b">{name}</span>
    <span style="font-size:12px;font-weight:600;color:#7c3aed;background:#ede9fe;
          border-radius:20px;padding:2px 10px">{star_html} {impact}</span>
  </div>
  <div style="font-size:11px;color:#64748b;margin:4px 0 6px 0">{org} · Grades {grades} · {when}</div>
  <div style="font-size:12px;color:#334155;margin-bottom:5px">{desc}</div>
  <div style="font-size:11px;color:#059669;font-weight:600">📍 Levels: {levels}</div>
  {tip_html}
</div>""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # ROADMAP
        # ════════════════════════════════════════════════════════════════════
        with cm_road:
            st.markdown("#### 🗺️ Grade-by-Grade Competition Roadmap")

            for grade_label, grade_color, grade_bg, items in [
                ("Grade 6  ·  2026-2027", "#1d4ed8", "#eff6ff", [
                    ("🔢 Math",        "MOEMS",                "School",                   "Nov–Apr",  "Build problem-solving habit"),
                    ("🔢 Math",        "AMC 8",                "National",                 "November", "First attempt — learn the format"),
                    ("🔢 Math",        "UIL Number Sense",     "School → District",        "Spring",   "Fast mental math — good warm-up"),
                    ("🔬 Science",     "Science Olympiad",     "Invitational (trial)",     "Feb–Mar",  "Join school team, try invitational"),
                    ("🎤 Speech",      "Gavel Club Contests",  "Club → Area",              "Year-round","Table Topics + Prepared Speech"),
                    ("🎤 Speech",      "UIL Prose/Poetry",     "School → District",        "Spring",   "Strong fit with Gavel Club skills"),
                    ("✍️ Writing",     "Scholastic Art & Writing", "Regional → National",  "Sep–Dec",  "Personal essays / short stories"),
                    ("✍️ Writing",     "UIL Ready Writing",    "School → District",        "Spring",   "Timed editorial — pair with ELA"),
                ]),
                ("Grade 7  ·  2027-2028", "#059669", "#f0fdf4", [
                    ("🔢 Math",        "MATHCOUNTS",           "School → Chapter → State", "Nov–May",  "Start serious training — Art of Problem Solving"),
                    ("🔢 Math",        "AMC 8",                "National",                 "November", "Target: top 25% (Honor Roll)"),
                    ("🔢 Math",        "Purple Comet Math Meet","Online Team",             "April",    "Team competition — low stakes, great practice"),
                    ("🔢 Math",        "UIL Calculator",       "School → District",        "Spring",   "Pair with Number Sense"),
                    ("🔬 Science",     "Science Olympiad",     "School → Invitational → Regional","Feb–May","Pick 2-3 events; build depth"),
                    ("🎤 Speech",      "Gavel Club Contests",  "Club → Area → Division",   "Year-round","Target Area-level title"),
                    ("🎤 Speech",      "NSDA Middle School",   "School → Regional",        "Year-round","Lincoln-Douglas or Original Oratory"),
                    ("🎤 Speech",      "UIL Oral Reading",     "School → District",        "Spring",   "Complements Gavel skills"),
                    ("✍️ Writing",     "Scholastic Art & Writing","Regional → National",   "Sep–Dec",  "Repeat — build a portfolio"),
                    ("📚 Social St.",  "National History Day", "School → District → State","Oct–Mar",  "Any format: paper / exhibit / documentary"),
                ]),
                ("Grade 8  ·  2028-2029", "#d97706", "#fffbeb", [
                    ("🔢 Math",        "MATHCOUNTS",           "Chapter → State → National","Nov–May", "Goal: State qualifier · National is elite"),
                    ("🔢 Math",        "AMC 8",                "National",                 "November", "Target: MATHCOUNTS National Honor Roll"),
                    ("🔢 Math",        "AMC 10 (prep)",        "National",                 "November", "Start practicing AMC 10 problems"),
                    ("🔢 Math",        "UIL Math",             "School → District → State","Spring",   "Strong college-app signal if State-level"),
                    ("🔬 Science",     "Science Olympiad",     "School → Regional → State","Feb–May",  "Target State · pick 3-4 strong events"),
                    ("🎤 Speech",      "Gavel Club Contests",  "Club → Area → Division → District","Year-round","Target District-level — big résumé item"),
                    ("🎤 Speech",      "NSDA Middle School",   "School → Regional → National","Year-round","National qualifier = strong HS app signal"),
                    ("🎤 Speech",      "UIL Prose Interpretation","School → State",        "Spring",   "Performance speech — Gavel experience helps"),
                    ("✍️ Writing",     "Scholastic Art & Writing","Gold Key target",       "Sep–Dec",  "Gold Key = national recognition"),
                    ("✍️ Writing",     "UIL Ready Writing",    "School → State",           "Spring",   "State qualifier looks strong on HS apps"),
                    ("📚 Social St.",  "National History Day", "District → State → National","Oct–Mar","National = extremely impressive"),
                    ("🔡 Spelling",    "Scripps Spelling Bee", "School → Regional → National","Jan–May","If strong speller — national TV exposure"),
                ]),
            ]:
                st.markdown(
                    f'<div style="background:{grade_bg};border-left:4px solid {grade_color};'
                    f'border-radius:0 10px 10px 0;padding:10px 16px;margin:16px 0 8px 0;">'
                    f'<span style="font-size:14px;font-weight:700;color:{grade_color}">{grade_label}</span></div>',
                    unsafe_allow_html=True,
                )
                rows = [{"Subject": s, "Competition": c, "Levels": lv, "When": w, "Focus / Tip": t}
                        for s, c, lv, w, t in items]
                st.dataframe(
                    rows, use_container_width=True, hide_index=True,
                    column_config={
                        "Subject":      st.column_config.TextColumn(width="small"),
                        "Competition":  st.column_config.TextColumn(width="medium"),
                        "Levels":       st.column_config.TextColumn(width="medium"),
                        "When":         st.column_config.TextColumn(width="small"),
                        "Focus / Tip":  st.column_config.TextColumn(width="large"),
                    },
                )

            st.divider()
            st.markdown("##### 🎓 College Admissions Impact Summary")
            st.markdown("""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px">
  <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:12px">
    <div style="font-weight:700;color:#dc2626;margin-bottom:6px">⭐⭐⭐ High Impact</div>
    <div style="font-size:12px;color:#334155;line-height:1.6">
      MATHCOUNTS State/National<br>AMC 8 Honor Roll · AMC 10 AIME<br>
      Science Olympiad State/National<br>NSDA National qualifier<br>
      Scholastic Gold Key<br>National History Day National
    </div>
  </div>
  <div style="background:#fefce8;border:1px solid #fde047;border-radius:10px;padding:12px">
    <div style="font-weight:700;color:#ca8a04;margin-bottom:6px">⭐⭐ Solid Signal</div>
    <div style="font-size:12px;color:#334155;line-height:1.6">
      MATHCOUNTS Chapter qualifier<br>UIL District/Regional placements<br>
      Gavel Club Area/Division title<br>Purple Comet strong score<br>
      Scripps Regional qualifier
    </div>
  </div>
  <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px">
    <div style="font-weight:700;color:#059669;margin-bottom:6px">⭐ Foundation</div>
    <div style="font-size:12px;color:#334155;line-height:1.6">
      MOEMS participation<br>AMC 8 first attempts<br>
      UIL School-level events<br>Gavel Club contests<br>
      Scholastic participation
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # MATH
        # ════════════════════════════════════════════════════════════════════
        with cm_math:
            st.markdown("#### 🔢 Math Competitions")
            st.caption("Pipeline: MOEMS / AMC 8 → MATHCOUNTS → AMC 10 → AIME → USAJMO")

            _comp_card(
                "MATHCOUNTS", "MATHCOUNTS Foundation", "6–8", "Nov–May",
                "School → Chapter → State → National",
                "Very High", 3,
                "The premier middle-school math competition in the US. "
                "School team (4 members) + individual. Chapter and State rounds are qualifying. "
                "National competition is elite — top ~200 students nationwide.",
                "Register through school. Train with Art of Problem Solving (AoPS) MATHCOUNTS prep books. "
                "Start in Grade 6 to build up to a strong Grade 8 run.",
            )
            _comp_card(
                "AMC 8", "MAA (Math Association of America)", "6–8", "November",
                "National (no qualifying rounds)",
                "High", 3,
                "25 multiple-choice questions in 40 min. Top scorers earn Honor Roll and Distinguished Honor Roll. "
                "Feeds into the AMC 10/12 → AIME → USAJMO pipeline that colleges notice.",
                "Free to take at school. Great benchmark. Aim for 18+ in Grade 6, 20+ in Grade 7, 22+ in Grade 8.",
            )
            _comp_card(
                "AMC 10 (Preparation)", "MAA", "9–10 (prep in Grade 8)", "November",
                "National → AIME qualifier",
                "Very High", 3,
                "Start solving AMC 10 practice problems in Grade 8. "
                "Qualifying for AIME (score ≥ 107) is a significant high-school resume item. "
                "Making USAJMO is Ivy-level differentiation.",
                "Use AoPS AMC 10 prep. Solve 2016–2024 past papers by Grade 8.",
            )
            _comp_card(
                "MOEMS (Math Olympiad for Elementary & Middle Schools)", "MOEMS", "4–8", "Nov–Apr",
                "School (5 monthly contests)",
                "Good", 1,
                "5 monthly contests (Nov–Mar), each with 5 open-ended problems. "
                "Score earns Gold/Silver/Bronze patches. "
                "Excellent entry-level competition to build problem-solving habits.",
                "School registers as a team. Very low pressure — good for Grade 6 warm-up.",
            )
            _comp_card(
                "Purple Comet Math Meet", "Purdue University", "5–12", "April",
                "Online Team (school or open)",
                "Solid", 2,
                "30-problem team competition (30 min). Free online. "
                "Good for building team problem-solving and benchmarking against other schools.",
                "Form a team of up to 6. Register at purplecomet.org.",
            )
            st.markdown("---")
            st.markdown("##### 📐 UIL Math Events (Texas)")
            st.caption("UIL competitions run school → district → regional → state each spring.")
            for ev, desc in [
                ("Number Sense", "80 questions in 10 min — pure mental math speed. Great for Grades 6–8."),
                ("Calculator Applications", "Computation + applications using a calculator. Grade 7 onwards."),
                ("Mathematics", "Concepts + problem-solving, 30 questions/40 min. Strong alignment with school curriculum."),
            ]:
                st.markdown(
                    f'<div style="background:#f0f9ff;border-left:3px solid #0ea5e9;border-radius:0 8px 8px 0;'
                    f'padding:8px 12px;margin-bottom:6px;font-size:13px">'
                    f'<b>{ev}</b> — <span style="color:#334155">{desc}</span></div>',
                    unsafe_allow_html=True,
                )

        # ════════════════════════════════════════════════════════════════════
        # SCIENCE
        # ════════════════════════════════════════════════════════════════════
        with cm_sci:
            st.markdown("#### 🔬 Science Competitions")

            _comp_card(
                "Science Olympiad", "Science Olympiad Inc.", "6–12", "Nov–May",
                "School Invitational → Regional → State → National",
                "Very High", 3,
                "Team of 15 competes across 23 events spanning biology, chemistry, physics, earth science, "
                "engineering and technology. Each student specializes in 5–7 events. "
                "One of the most recognized STEM competitions in the US — colleges love it.",
                "Join school team in Grade 6 as an Invitational trial. "
                "Build depth in 2–3 events per year. Target State in Grade 8.",
            )
            _comp_card(
                "UIL Science", "UIL Texas", "6–8", "Spring",
                "School → District → Regional → State",
                "Solid", 2,
                "Biology, Chemistry, Physics and General Science events. "
                "Multiple-choice format. Strong alignment with TEKS curriculum.",
                "Pair with school science class. District placement = solid middle-school résumé item.",
            )
            _comp_card(
                "FIRST LEGO League (FLL)", "FIRST", "4–8", "Sep–Dec",
                "School/Club → Regional → State → World",
                "Solid", 2,
                "Team builds and programs a LEGO robot to complete missions, plus researches a real-world "
                "STEM problem and presents solutions. Encourages creativity and collaboration.",
                "Great for Grades 6–7. Check FISD robotics clubs. "
                "Strong college signal if team reaches World Championship.",
            )
            _comp_card(
                "Texas Science & Engineering Fair (TXSEF)", "Texas Academy of Science", "6–12", "Feb–Mar",
                "School → Regional → State → Regeneron ISEF",
                "High", 3,
                "Individual research project in any STEM field. "
                "State winner advances to Regeneron ISEF — the world's largest pre-college science fair. "
                "Winning at any level is impressive for selective high schools and colleges.",
                "Start small in Grade 6 with a focused question. Build on it each year. "
                "Pick a topic you're genuinely curious about.",
            )

        # ════════════════════════════════════════════════════════════════════
        # SPEECH & DEBATE
        # ════════════════════════════════════════════════════════════════════
        with cm_speech:
            st.markdown("#### 🎤 Speech & Debate Competitions")
            st.info(
                "**Gavel Club member** — Toastmasters' youth program. "
                "Club contest experience directly feeds into UIL and NSDA speech events. "
                "Gavel Club skills (prepared speech, table topics, evaluations) are transferable to every competition below.",
                icon="🗣️",
            )

            _comp_card(
                "Gavel Club Speech Contests", "Toastmasters International (Youth)", "6–12", "Year-round",
                "Club → Area → Division → District",
                "Solid", 2,
                "Toastmasters runs formal speech contests at each level. "
                "Events include: Prepared Speech (5–7 min), Table Topics (impromptu 1–2 min), "
                "Humorous Speech, Evaluation Contest, and International Speech Contest. "
                "District-level winner is a strong recognition for a middle-schooler.",
                "Table Topics and Prepared Speech contests run multiple times per year. "
                "Focus on Area title in Grade 7 and Division/District in Grade 8.",
            )
            _comp_card(
                "NSDA Middle School Speech & Debate", "National Speech & Debate Association", "6–8", "Year-round",
                "School → Tournament → Regional → National",
                "Very High", 3,
                "NSDA offers middle school events: Original Oratory, Expository Speaking, "
                "Storytelling, Debate (Public Forum, Lincoln-Douglas intro). "
                "Earning NSDA points and qualifying for National Tournament is a standout achievement.",
                "Register through school coach or independently at speechanddebate.org. "
                "Original Oratory pairs perfectly with Gavel Club prepared speech experience.",
            )

            st.markdown("---")
            st.markdown("##### 📋 UIL Speech Events (Texas — Spring Season)")
            st.caption("All UIL speech events follow the School → District → Regional → State ladder.")
            for ev, grades, desc in [
                ("Prose Interpretation", "6–8",
                 "Read aloud a published prose passage (5 min max). Judged on delivery, expression, and interpretation. "
                 "Gavel Club vocal variety and body language skills apply directly."),
                ("Poetry Interpretation", "6–8",
                 "Perform a published poem with voice and gesture. Similar to Prose but with poetic rhythm."),
                ("Oral Reading", "6–8",
                 "Sight-read an unfamiliar passage aloud with expression. Tests spontaneous delivery."),
                ("Informative Speaking", "6–8",
                 "Original 4–6 min speech with at least one visual aid. "
                 "Strong overlap with Gavel Club Prepared Speech pathway."),
                ("Persuasive Speaking", "6–8",
                 "Original persuasive speech, 4–6 min. "
                 "Same format as NSDA Original Oratory — can prepare one speech for both."),
            ]:
                st.markdown(
                    f'<div style="background:#fdf4ff;border-left:3px solid #a21caf;border-radius:0 8px 8px 0;'
                    f'padding:9px 13px;margin-bottom:7px;font-size:13px">'
                    f'<b>{ev}</b> <span style="font-size:11px;color:#94a3b8">· Grades {grades}</span><br>'
                    f'<span style="color:#334155">{desc}</span></div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            _comp_card(
                "Texas Forensic Association (TFA)", "TFA", "6–12", "Sep–May",
                "Tournament circuit → State",
                "High", 3,
                "Texas's largest competitive speech and debate circuit. "
                "Events: Lincoln-Douglas Debate, Public Forum Debate, Policy Debate, "
                "Congress, Original Oratory, Extemp Speaking. "
                "TFA State is one of the most competitive high-school speech tournaments in the country. "
                "Starting the circuit in Grade 8 gives a head-start entering high school.",
                "Check if Wortham/Lebanon Trail HS has a TFA team that accepts middle schoolers for practice.",
            )

        # ════════════════════════════════════════════════════════════════════
        # WRITING & OTHERS
        # ════════════════════════════════════════════════════════════════════
        with cm_write:
            st.markdown("#### ✍️ Writing, Social Studies & Other Competitions")

            _comp_card(
                "Scholastic Art & Writing Awards", "Scholastic", "6–12", "Sep–Dec submission",
                "Regional → National (Gold Key / Silver Key / Honorable Mention)",
                "Very High", 3,
                "Nation's longest-running recognition program for creative teens. "
                "Categories: Short Story, Personal Essay, Flash Fiction, Poetry, Journalism, Humor, Science Fiction. "
                "Gold Key at regional level = automatic National consideration. "
                "Past winners include Sylvia Plath, Truman Capote, Stephen King.",
                "Submit one strong piece per category. Personal Essay and Short Story are most accessible. "
                "Build a piece from school assignments over the summer.",
            )
            _comp_card(
                "UIL Ready Writing", "UIL Texas", "6–8", "Spring",
                "School → District → Regional → State",
                "Solid", 2,
                "Timed editorial essay (1 hr) on a provided topic. "
                "Tests argument structure, evidence, grammar and style. "
                "Strong alignment with ELA curriculum.",
                "Practice timed writing (60 min) every 2 weeks. Read strong editorials (NYT, WSJ) for models.",
            )
            _comp_card(
                "National History Day (NHD)", "National History Day", "6–12", "Oct–Mar",
                "School → District → State → National",
                "Very High", 3,
                "Annual theme-based research competition. Students submit in one of five formats: "
                "Paper, Exhibit, Documentary, Performance, or Website. "
                "Judged on historical argument, research quality, and presentation. "
                "National finalist = major college application standout.",
                "Pick a topic early (Sep). Documentary or Website format works well for tech-comfortable students. "
                "Texas NHD website: nhd.org/texas",
            )

            st.markdown("---")
            st.markdown("##### 📋 More UIL Academic Events")
            st.caption("UIL has the widest range of middle-school academic competitions in Texas.")
            for ev, grades, desc in [
                ("Social Studies", "6–8",
                 "50-question test on world history, geography, civics and economics. Spring season."),
                ("Spelling & Vocabulary", "6–8",
                 "Written spelling test (25 words) + oral bee format. Feeds into Scripps Bee prep."),
                ("Maps, Graphs & Charts", "6–8",
                 "Interpretation of maps, charts and data — strong overlap with Math and Science skills."),
                ("Dictionary Skills", "6–8",
                 "Speed and accuracy using a dictionary. Tests research and reference skills."),
                ("Science (UIL)", "6–8",
                 "Biology, Chemistry, Physical Science questions from TEKS. Spring season."),
            ]:
                st.markdown(
                    f'<div style="background:#f0fdf4;border-left:3px solid #22c55e;border-radius:0 8px 8px 0;'
                    f'padding:9px 13px;margin-bottom:7px;font-size:13px">'
                    f'<b>{ev}</b> <span style="font-size:11px;color:#94a3b8">· Grades {grades}</span><br>'
                    f'<span style="color:#334155">{desc}</span></div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            _comp_card(
                "Scripps National Spelling Bee", "Scripps / E.W. Scripps", "6–8", "Jan–May",
                "School → Regional (Bee) → National",
                "High", 3,
                "The most recognized spelling competition in the US — national finals air on ESPN. "
                "School-level bee → wins to regional → national in Washington DC. "
                "Strong vocabulary and memory skills; pairs well with UIL Spelling prep.",
                "School coordinator registers. Merriam-Webster online practice list available free at spellingbee.com.",
            )

        # ════════════════════════════════════════════════════════════════════
        # MY RESULTS LOG
        # ════════════════════════════════════════════════════════════════════
        with cm_log:
            st.markdown("#### 📝 Competition Results Log")
            st.caption("Track participation, levels reached, and scores year by year.")

            # Session-state log for this session (no GSheets persistence yet — placeholder)
            if "comp_log" not in st.session_state:
                st.session_state["comp_log"] = []

            with st.expander("➕ Add Result", expanded=True):
                with st.form("comp_log_form"):
                    cl1, cl2, cl3 = st.columns(3)
                    with cl1:
                        cl_year  = st.selectbox("School Year", ["2026-2027","2027-2028","2028-2029"])
                        cl_grade = st.selectbox("Grade", ["6","7","8"])
                    with cl2:
                        cl_subj  = st.selectbox("Subject", ["Math","Science","Speech & Debate","Writing","Social Studies","Other"])
                        cl_comp  = st.text_input("Competition Name", placeholder="e.g. MATHCOUNTS Chapter")
                    with cl3:
                        cl_level = st.selectbox("Highest Level", ["School","Chapter / District","Regional","State","National"])
                        cl_place = st.text_input("Placement / Score", placeholder="e.g. 3rd place · 24/25")
                    cl_notes = st.text_input("Notes", placeholder="Optional details")
                    if st.form_submit_button("Add Entry", type="primary"):
                        if cl_comp:
                            st.session_state["comp_log"].append({
                                "Year": cl_year, "Grade": cl_grade, "Subject": cl_subj,
                                "Competition": cl_comp, "Level": cl_level,
                                "Placement / Score": cl_place, "Notes": cl_notes,
                            })
                            st.success(f"✅ Logged: {cl_comp}")
                            st.rerun()
                        else:
                            st.warning("Enter a competition name.")

            if st.session_state["comp_log"]:
                import pandas as _pd
                log_df = _pd.DataFrame(st.session_state["comp_log"])
                st.dataframe(log_df, use_container_width=True, hide_index=True)
            else:
                st.info("No results logged yet. Add your first competition result above.")

            st.caption("💡 Results are session-only for now — GSheets persistence can be added later.")

    with uil_tab:
        from services.uil_materials import render_uil_center
        render_uil_center()

    with tests_tab:
        from services.practice_tests import render_practice_tests
        render_practice_tests()

    # ── ♟️ Chess ──────────────────────────────────────────────────────────────
    with chess_tab:
        st.markdown("### ♟️ Chess — Premier Chess Academy (PCA)")

        # ── Info cards ────────────────────────────────────────────────────────
        ci1, ci2, ci3 = st.columns(3)
        ci1.markdown(
            '<div style="background:#eff6ff;border:1.5px solid #bfdbfe;border-radius:10px;padding:12px 16px">'
            '<div style="font-size:13px;color:#64748b;font-weight:600">SCHEDULE</div>'
            '<div style="font-size:18px;font-weight:700;color:#1e40af">Tue & Thu</div>'
            '<div style="font-size:14px;color:#374151">5:30 PM CST</div>'
            '</div>', unsafe_allow_html=True
        )
        ci2.markdown(
            '<div style="background:#f0fdf4;border:1.5px solid #bbf7d0;border-radius:10px;padding:12px 16px">'
            '<div style="font-size:13px;color:#64748b;font-weight:600">ACADEMY</div>'
            '<div style="font-size:18px;font-weight:700;color:#15803d">PCA</div>'
            '<div style="font-size:14px;color:#374151">USCF Affiliated</div>'
            '</div>', unsafe_allow_html=True
        )
        ci3.markdown(
            '<div style="background:#fdf4ff;border:1.5px solid #e9d5ff;border-radius:10px;padding:12px 16px">'
            '<div style="font-size:13px;color:#64748b;font-weight:600">PLATFORM</div>'
            '<div style="font-size:18px;font-weight:700;color:#7e22ce">Chess.com</div>'
            '<div style="font-size:14px;color:#374151">Club + Tournaments</div>'
            '</div>', unsafe_allow_html=True
        )

        st.markdown("")
        lnk1, lnk2 = st.columns(2)
        with lnk1:
            st.link_button("♟️ PCA Club on Chess.com", "https://www.chess.com/club/premier-chess-academy-usa", use_container_width=True)
        with lnk2:
            st.link_button("🌐 PCA Website", "https://premierchessacademy.com/", use_container_width=True)

        st.divider()

        # ── Sub-tabs ──────────────────────────────────────────────────────────
        ch_prog, ch_rate, ch_upcoming, ch_log, ch_res = st.tabs(
            ["📈 Progress & Goals", "🏅 Ratings", "📅 Upcoming Events", "🏆 My Tournament Log", "📚 Resources"]
        )

        with ch_prog:
            st.markdown("#### 📈 Progress & Goals")
            pg1, pg2 = st.columns(2)
            with pg1:
                with st.container(border=True):
                    st.markdown("**Current Level**")
                    level = st.selectbox("Chess level", ["Beginner", "Intermediate", "Advanced", "Tournament Player"], index=1, key="chess_level")
                    focus = st.text_input("Current focus area (e.g. Openings, Endgames)", key="chess_focus", placeholder="e.g. Sicilian Defense, Rook Endgames")
                    st.caption("These are session-only — GSheets persistence can be added later.")
            with pg2:
                with st.container(border=True):
                    st.markdown("**Short-Term Goals**")
                    st.markdown(
                        "- 🎯 Achieve USCF rating ≥ 1000\n"
                        "- 🎯 Win at least one tournament section\n"
                        "- 🎯 Master 3 solid openings as White and Black\n"
                        "- 🎯 Complete tactics training — 15 min/day"
                    )
                    st.caption("Edit goals directly in the app code → Kids.py chess section.")

            st.markdown("#### 🗓️ Weekly Practice Plan")
            with st.container(border=True):
                plan_cols = st.columns(4)
                plan_cols[0].markdown("**📖 Openings** (15 min)\nReview opening repertoire on Chess.com lessons")
                plan_cols[1].markdown("**🧩 Tactics** (15 min)\nDaily puzzles on Chess.com or Chesstempo")
                plan_cols[2].markdown("**♟️ PCA Class** (Tue/Thu)\n5:30 PM — attend and take notes")
                plan_cols[3].markdown("**🔍 Game Review** (10 min)\nAnalyze 1 game/week with engine after class")

        with ch_rate:
            st.markdown("#### 🏅 Rating Tracker")
            st.caption("Log ratings manually after each rated event. USCF ratings are official; Chess.com is rapid/blitz online.")
            import pandas as _pd2
            if "chess_ratings" not in st.session_state:
                st.session_state["chess_ratings"] = []

            with st.expander("➕ Log a Rating Update", expanded=False):
                rc1, rc2, rc3, rc4 = st.columns(4)
                with rc1:
                    r_date = st.date_input("Date", key="chess_r_date")
                with rc2:
                    r_type = st.selectbox("Type", ["USCF", "Chess.com Rapid", "Chess.com Blitz"], key="chess_r_type")
                with rc3:
                    r_val = st.number_input("Rating", min_value=100, max_value=3000, value=800, step=10, key="chess_r_val")
                with rc4:
                    r_note = st.text_input("Note (optional)", key="chess_r_note", placeholder="e.g. After PCA Feb tournament")
                if st.button("Add Rating Entry", key="chess_r_add"):
                    st.session_state["chess_ratings"].append({
                        "Date": str(r_date), "Type": r_type, "Rating": r_val, "Note": r_note
                    })
                    st.success("Rating logged!")
                    st.rerun()

            if st.session_state["chess_ratings"]:
                df_rates = _pd2.DataFrame(st.session_state["chess_ratings"])
                st.dataframe(df_rates, use_container_width=True, hide_index=True)
            else:
                st.info("No ratings logged yet — add your first entry above.")

        with ch_upcoming:
            st.markdown("#### 📅 Upcoming PCA Events")
            st.caption(
                "Chess.com club events require a logged-in member session — live sync isn't possible here. "
                "Open the link below while logged into Chess.com to see the full schedule, then copy upcoming events below."
            )
            st.link_button(
                "🔗 View PCA Upcoming Events on Chess.com →",
                "https://www.chess.com/clubs/upcomingevents/premier-chess-academy-usa",
                use_container_width=True,
            )
            st.divider()

            # ── Manual upcoming events tracker ────────────────────────────────
            st.markdown("**Add Upcoming Events** *(copy from Chess.com)*")
            if "chess_upcoming" not in st.session_state:
                st.session_state["chess_upcoming"] = []

            with st.expander("➕ Add an Upcoming Event", expanded=True):
                ue1, ue2, ue3 = st.columns(3)
                with ue1:
                    ue_date = st.date_input("Event Date", key="chess_ue_date")
                    ue_name = st.text_input("Event Name", key="chess_ue_name",
                                            placeholder="e.g. PCA Weekly Rapid #42")
                with ue2:
                    ue_type = st.selectbox("Type", ["Club Match", "Tournament", "Weekly Rapid",
                                                     "Ladder", "Other"], key="chess_ue_type")
                    ue_tc   = st.text_input("Time Control", key="chess_ue_tc",
                                            placeholder="e.g. 15+10, 5+3")
                with ue3:
                    ue_rounds = st.text_input("Rounds / Format", key="chess_ue_rounds",
                                              placeholder="e.g. 5 rounds Swiss")
                    ue_note   = st.text_input("Notes", key="chess_ue_note",
                                              placeholder="Optional")
                if st.button("Add Event", key="chess_ue_add", type="primary"):
                    st.session_state["chess_upcoming"].append({
                        "Date": str(ue_date), "Event": ue_name, "Type": ue_type,
                        "Time Control": ue_tc, "Format": ue_rounds, "Notes": ue_note,
                    })
                    st.success("Event added!")
                    st.rerun()

            if st.session_state["chess_upcoming"]:
                import pandas as _pd_ue
                df_ue = _pd_ue.DataFrame(st.session_state["chess_upcoming"])
                df_ue = df_ue.sort_values("Date").reset_index(drop=True)
                st.dataframe(df_ue, use_container_width=True, hide_index=True)
                if st.button("🗑️ Clear All Upcoming Events", key="chess_ue_clear"):
                    st.session_state["chess_upcoming"] = []
                    st.rerun()
            else:
                st.info("No upcoming events added yet — copy them from the Chess.com link above.")

        with ch_log:
            st.markdown("#### 🏆 My Tournament Log")
            st.caption("Log completed PCA and open tournaments. USCF results also appear at uschess.org after rated events.")
            if "chess_tournaments" not in st.session_state:
                st.session_state["chess_tournaments"] = []

            with st.expander("➕ Log a Completed Tournament", expanded=False):
                tc1, tc2, tc3 = st.columns(3)
                with tc1:
                    t_date  = st.date_input("Date", key="chess_t_date")
                    t_name  = st.text_input("Tournament Name", key="chess_t_name",
                                            placeholder="e.g. PCA Spring Open 2026")
                with tc2:
                    t_org   = st.text_input("Organizer", key="chess_t_org", value="PCA",
                                            placeholder="PCA / USCF Open / etc.")
                    t_sect  = st.text_input("Section (e.g. K-8 U800)", key="chess_t_sect")
                with tc3:
                    t_score = st.text_input("Score (e.g. 3.5/5)", key="chess_t_score")
                    t_place = st.text_input("Place / Award", key="chess_t_place",
                                            placeholder="e.g. 2nd in section")
                t_note = st.text_input("Notes", key="chess_t_note",
                                       placeholder="Optional — highlight games, takeaways")
                if st.button("Add to Log", key="chess_t_add", type="primary"):
                    st.session_state["chess_tournaments"].append({
                        "Date": str(t_date), "Tournament": t_name, "Organizer": t_org,
                        "Section": t_sect, "Score": t_score, "Place": t_place, "Notes": t_note,
                    })
                    st.success("Tournament logged!")
                    st.rerun()

            if st.session_state["chess_tournaments"]:
                df_tourn = _pd2.DataFrame(st.session_state["chess_tournaments"])
                df_tourn = df_tourn.sort_values("Date", ascending=False).reset_index(drop=True)
                st.dataframe(df_tourn, use_container_width=True, hide_index=True)
            else:
                st.info("No tournaments logged yet — add your first result above.")

        with ch_res:
            st.markdown("#### 📚 Chess Learning Resources")
            res_cols = st.columns(2)
            with res_cols[0]:
                with st.container(border=True):
                    st.markdown("**🌐 Online Practice**")
                    st.markdown(
                        "- [Chess.com](https://www.chess.com) — Daily puzzles, lessons, live games\n"
                        "- [Lichess.org](https://lichess.org) — Free tactics trainer, analysis board\n"
                        "- [ChessTempo](https://chesstempo.com) — Endgame & tactics drills\n"
                        "- [Chess Kid](https://www.chesskid.com) — Kid-safe chess platform by Chess.com"
                    )
                with st.container(border=True):
                    st.markdown("**📖 Opening Repertoire Tips**")
                    st.markdown(
                        "**As White:** 1.e4 → Italian Game or London System\n\n"
                        "**As Black vs 1.e4:** Sicilian Defense or e5\n\n"
                        "**As Black vs 1.d4:** King's Indian or Nimzo-Indian\n\n"
                        "*Focus on 2–3 solid openings. Depth beats breadth at this level.*"
                    )
            with res_cols[1]:
                with st.container(border=True):
                    st.markdown("**🏆 Tournaments & Ratings**")
                    st.markdown(
                        "- [US Chess Federation](https://www.uschess.org) — Official USCF ratings & tournament results\n"
                        "- [PCA Club on Chess.com](https://www.chess.com/club/premier-chess-academy-usa) — Club events & standings\n"
                        "- [PCA Website](https://premierchessacademy.com/) — Academy info & schedule\n"
                        "- [Texas Chess Association](https://txchess.org) — TX scholastic tournaments"
                    )
                with st.container(border=True):
                    st.markdown("**🧩 Daily Habit (15 min)**")
                    st.markdown(
                        "| Day | Activity |\n"
                        "|-----|----------|\n"
                        "| Mon | 10 tactics puzzles (Chess.com) |\n"
                        "| Tue | PCA class 5:30 PM |\n"
                        "| Wed | Review 1 opening line |\n"
                        "| Thu | PCA class 5:30 PM |\n"
                        "| Fri | Play 1 slow game online |\n"
                        "| Sat | Analyze the week's games |\n"
                        "| Sun | Rest or light puzzles |"
                    )


# ═══════════════════════════════════════════════════════════════════════════════
# DAUGHTER
# ═══════════════════════════════════════════════════════════════════════════════
with child_tab2:
    d1, d2, d3 = st.tabs(["🏥 PA School", "🌟 Planning Ahead", "📋 Classes & Fees"])

    with d1:
        st.markdown("### 🏥 PA School — Physician Assistant Path")
        pa1, pa2, pa3 = st.tabs(["📚 Reference Pages", "📋 Application Tracker", "🗓️ Timeline"])
        with pa1:
            st.info("Upload PA school HTML reference files to display here.")
            uploaded = st.file_uploader("Upload PA school HTML page", type=["html","htm"], key="pa_upload")
            if uploaded:
                html_content = uploaded.read().decode("utf-8", errors="ignore")
                st.components.v1.html(html_content, height=600, scrolling=True)
        with pa2:
            coming_soon("PA school application tracker — schools, deadlines, status")
        with pa3:
            coming_soon("PA school timeline — prerequisites, CASPA, interviews")

    with d2:
        coming_soon("Daughter — planning ahead tracker")

    with d3:
        st.markdown("### 📋 Classes & Fees Tracker — Daughter")
        cls_df_d = list_classes(child="Daughter")
        monthly_d = monthly_cost("Daughter")

        m1, m2, m3 = st.columns(3)
        m1.metric("Active Classes", len(cls_df_d) if not cls_df_d.empty else 0)
        m2.metric("Est. Monthly Cost", f"${monthly_d:,.0f}")
        m3.metric("Est. Annual Cost", f"${monthly_d*12:,.0f}")

        dl1, dl2, dl3 = st.tabs(["📋 Classes List", "📅 Upcoming Schedule", "➕ Add Class"])

        with dl1:
            if not cls_df_d.empty:
                hc = st.columns([2.2, 1.8, 1.6, 1.4, 1.2, 0.75, 0.75, 0.75])
                for col, lbl in zip(hc, ["Class / Provider", "Days", "Time", "Fee", "Meets", "", "", ""]):
                    col.markdown(f"<span style='font-size:11px;font-weight:600;color:#64748b;'>{lbl}</span>",
                                 unsafe_allow_html=True)
                st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

                for _, cls in cls_df_d.iterrows():
                    is_paused  = str(cls.get("paused", "FALSE")).upper() == "TRUE"
                    row_op     = "0.55" if is_paused else "1"
                    is_editing = st.session_state.get("dau_edit_id") == cls["id"]
                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2.2, 1.8, 1.6, 1.4, 1.2, 0.75, 0.75, 0.75])
                    with c1:
                        badge = ('<span style="background:#fef9c3;color:#854d0e;font-size:10px;'
                                 'border-radius:6px;padding:1px 6px;margin-left:4px;">⏸ paused</span>'
                                 if is_paused else "")
                        st.markdown(
                            f'<div style="opacity:{row_op}">'
                            f'<span style="font-weight:600;font-size:13px;">{cls["name"]}</span>{badge}<br>'
                            f'<span style="font-size:11px;color:#64748b;">{cls.get("provider","")}</span>'
                            f'</div>', unsafe_allow_html=True)
                    with c2:
                        days_disp = str(cls.get("days", "") or "—")
                        loc_disp  = str(cls.get("location", "") or "")
                        st.markdown(
                            f'<div style="font-size:12px;opacity:{row_op}">{days_disp}'
                            + (f'<br><span style="font-size:11px;color:#64748b;">📍 {loc_disp}</span>' if loc_disp else "")
                            + "</div>", unsafe_allow_html=True)
                    with c3:
                        ts = str(cls.get("time_start", "") or "")
                        te = str(cls.get("time_end", "") or "")
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'{"–".join(filter(None,[ts,te])) or "—"}</div>',
                                    unsafe_allow_html=True)
                    with c4:
                        cost = cls.get("cost", 0) or 0
                        ff   = str(cls.get("fee_frequency", "") or "")
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'${float(cost):,.0f}<br>'
                                    f'<span style="font-size:11px;color:#64748b;">{ff}</span></div>',
                                    unsafe_allow_html=True)
                    with c5:
                        st.markdown(f'<div style="font-size:12px;opacity:{row_op}">'
                                    f'{cls.get("frequency","")}</div>', unsafe_allow_html=True)
                    with c6:
                        plbl = "▶" if is_paused else "⏸"
                        if st.button(plbl, key=f"pause_dau_{cls['id']}",
                                     help="Resume" if is_paused else "Pause",
                                     use_container_width=True):
                            toggle_pause(cls["id"])
                            st.rerun()
                    with c7:
                        elbl = "✕" if is_editing else "✏️"
                        if st.button(elbl, key=f"edit_dau_{cls['id']}",
                                     help="Cancel edit" if is_editing else "Modify",
                                     use_container_width=True):
                            st.session_state["dau_edit_id"] = None if is_editing else cls["id"]
                            st.rerun()
                    with c8:
                        if st.button("🗑️", key=f"del_dau_{cls['id']}",
                                     help="Delete", use_container_width=True):
                            delete_class(cls["id"])
                            st.session_state.pop("dau_edit_id", None)
                            st.rerun()
                    st.markdown("<hr style='margin:2px 0;border-color:#f1f5f9'>",
                                unsafe_allow_html=True)

                    # ── Inline edit form ──────────────────────────────────────
                    if is_editing:
                        st.markdown(
                            f'<div style="background:#fdf4ff;border:1px solid #d8b4fe;'
                            f'border-radius:10px;padding:14px 18px;margin-bottom:10px;">'
                            f'<b style="font-size:13px;">✏️ Editing: {cls["name"]}</b></div>',
                            unsafe_allow_html=True)
                        with st.form(f"edit_dau_{cls['id']}_form"):
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                e_name  = st.text_input("Class Name", value=str(cls.get("name","")))
                                e_prov  = st.text_input("Provider", value=str(cls.get("provider","")))
                                e_loc   = st.text_input("Location", value=str(cls.get("location","")))
                                try:
                                    e_start_val = date.fromisoformat(str(cls.get("start_date", date.today())))
                                except (ValueError, TypeError):
                                    e_start_val = date.today()
                                e_start = st.date_input("Start Date", value=e_start_val, key=f"dau_esd_{cls['id']}")
                            with ec2:
                                e_cost  = st.number_input("Fee Amount ($)",
                                                          value=float(cls.get("cost",0) or 0),
                                                          min_value=0.0, step=5.0)
                                cur_ff  = str(cls.get("fee_frequency",""))
                                e_feef  = st.selectbox("Fee Frequency", FEE_FREQUENCIES,
                                                       index=best_match_index(cur_ff, FEE_FREQUENCIES))
                                cur_fr  = str(cls.get("frequency",""))
                                e_freq  = st.selectbox("Class Meets", FREQUENCIES,
                                                       index=best_match_index(cur_fr, FREQUENCIES))
                            cur_days   = [d.strip() for d in str(cls.get("days","")).split(",") if d.strip() in DAYS_OF_WEEK]
                            e_days     = st.multiselect("Class Days", DAYS_OF_WEEK, default=cur_days,
                                                        key=f"dau_edays_{cls['id']}")
                            et1, et2   = st.columns(2)
                            with et1:
                                e_ts = st.time_input("Start Time", value=_parse_time(cls.get("time_start")),
                                                     key=f"dau_ets_{cls['id']}")
                            with et2:
                                e_te = st.time_input("End Time", value=_parse_time(cls.get("time_end")),
                                                     key=f"dau_ete_{cls['id']}")
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                do_save   = st.form_submit_button("💾 Save Changes", type="primary",
                                                                  use_container_width=True)
                            with sc2:
                                do_cancel = st.form_submit_button("✕ Cancel", use_container_width=True)
                            if do_save:
                                update_class(cls["id"],
                                             name=e_name, provider=e_prov, location=e_loc,
                                             cost=e_cost, fee_frequency=e_feef,
                                             days=",".join(e_days), frequency=e_freq,
                                             start_date=e_start.isoformat(),
                                             time_start=e_ts.strftime("%I:%M %p") if e_ts else "",
                                             time_end=e_te.strftime("%I:%M %p") if e_te else "")
                                st.session_state["dau_edit_id"] = None
                                st.rerun()
                            if do_cancel:
                                st.session_state["dau_edit_id"] = None
                                st.rerun()

                paused_count_d = sum(
                    1 for _, r in cls_df_d.iterrows()
                    if str(r.get("paused","")).upper() == "TRUE"
                )
                if paused_count_d:
                    st.caption(f"⏸ {paused_count_d} class(es) paused — excluded from cost & schedule")
            else:
                st.info("No classes yet. Use the ➕ Add Class tab to get started.")

        with dl2:
            sessions_d = upcoming_sessions(child="Daughter", days_ahead=21)
            if not sessions_d:
                if cls_df_d.empty:
                    st.info("No classes added yet.")
                else:
                    st.info("No classes have day/time set. Add schedule details when creating a class.")
            else:
                st.markdown("##### 📅 Next 21 Days — Daughter's Classes")
                today_d2 = date.today()
                cur_date2 = None
                for s in sessions_d:
                    if s["date"] != cur_date2:
                        cur_date2 = s["date"]
                        delta = (cur_date2 - today_d2).days
                        dlabel = "Today" if delta == 0 else ("Tomorrow" if delta == 1 else
                                 cur_date2.strftime("%A, %b %d"))
                        st.markdown(f"**{dlabel}**")
                    time_str = f"{s['time_start']}–{s['time_end']}" if s['time_start'] else ""
                    loc_str  = f" · 📍 {s['location']}" if s['location'] else ""
                    st.markdown(
                        f"""<div style="margin-left:16px;padding:9px 14px;background:#fdf4ff;
                            border-left:3px solid #9333ea;border-radius:8px;margin-bottom:5px;
                            display:flex;gap:14px;align-items:center;flex-wrap:wrap;">
                          <span style="font-size:13px;font-weight:600;color:#6b21a8;">{s['class']}</span>
                          <span style="font-size:12px;color:#9333ea;">{s['provider']}</span>
                          {'<span style="font-size:12px;color:#7c3aed;">🕐 ' + time_str + '</span>' if time_str else ''}
                          <span style="font-size:12px;color:#64748b;margin-left:auto;">{loc_str}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        with dl3:
            with st.form("add_class_daughter"):
                st.markdown("##### Class Details")
                c1, c2 = st.columns(2)
                with c1:
                    cname  = st.text_input("Class Name *")
                    cprov  = st.text_input("Provider / Instructor")
                    cloc   = st.text_input("Location", placeholder="e.g. Online, Studio")
                    cstart = st.date_input("Start Date", value=date.today())
                with c2:
                    ccost  = st.number_input("Fee Amount ($)", min_value=0.0, step=5.0,
                                             help="Amount per billing period")
                    cfeef  = st.selectbox("Fee Frequency", FEE_FREQUENCIES,
                                          help="How often this fee is charged",
                                          key="d_feef")
                    cfreq  = st.selectbox("Class Meets", FREQUENCIES,
                                          help="How often the class actually meets",
                                          key="d_cfreq")

                st.markdown("##### Class Days & Time")
                cdays = st.multiselect("Class Days *", DAYS_OF_WEEK, key="daughter_days")
                t1, t2 = st.columns(2)
                with t1:
                    ct_start = st.time_input("Start Time", value=None, key="daughter_tstart")
                with t2:
                    ct_end   = st.time_input("End Time", value=None, key="daughter_tend")

                st.markdown("##### Reminders")
                auto_remind_d = st.checkbox("Auto-add weekly reminder for each class day",
                                            value=True, key="daughter_autoremind")

                if st.form_submit_button("➕ Add Class", type="primary"):
                    if not cname:
                        st.error("Class name is required.")
                    elif not cdays:
                        st.error("Select at least one class day.")
                    else:
                        days_str  = ",".join(cdays)
                        ts_str    = ct_start.strftime("%I:%M %p") if ct_start else ""
                        te_str    = ct_end.strftime("%I:%M %p") if ct_end else ""
                        add_class("Daughter", cname, cprov, ccost, cfeef, days_str, cfreq, cstart,
                                  time_start=ts_str, time_end=te_str, location=cloc)
                        if auto_remind_d:
                            from services.reminders import add as add_rem
                            for d in cdays:
                                today_d2   = date.today()
                                d_num      = DAYS_OF_WEEK.index(d)
                                days_until = (d_num - today_d2.weekday()) % 7
                                next_d     = today_d2 + timedelta(days=days_until if days_until else 7)
                                detail     = (f"{cprov}" + (f" · {ts_str}–{te_str}" if ts_str else "")
                                              + (f" · {cloc}" if cloc else ""))
                                add_rem("kids", f"📚 {cname} — {d}", detail, next_d,
                                        remind_days=0, frequency="weekly", channels="push")
                        st.success(f"✅ Added: {cname}" + (" · reminders created" if auto_remind_d else ""))
                        st.rerun()

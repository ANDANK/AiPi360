"""Kids section — Son (Grade 6/7/8) and Daughter."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="AiPi360 · Kids", page_icon="🧒", layout="wide")

from backend.auth import require_auth, sign_out
require_auth()

from components.metric_card import section_header, coming_soon
from components.reminder_banner import render_section_reminders
from services.kids import list_classes, add_class, delete_class, monthly_cost, FREQUENCIES
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

    g6, g7, g8, tamil_tab, classes_tab = st.tabs(["📘 Grade 6", "📗 Grade 7", "📙 Grade 8", "🕉️ Tamil School", "📋 Classes & Fees"])

    # ── Grade 6 ───────────────────────────────────────────────────────────────
    with g6:
        st.markdown("### 📘 Grade 6 — FISD")
        sub1, sub2, sub3, sub4 = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🔢 Math Rocks", "🌟 Planning Ahead"])

        with sub1:
            st.markdown("#### 📅 FISD School Calendar — Wortham Intermediate")

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

            # ── Calendar display ──────────────────────────────────────────────
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
                        # Auto-seed baseline on first visit
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
                        st.caption(f"*(Est.) = estimated from standard FISD pattern — verify at friscoisd.org*")
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
                    r_title = st.text_input("Event / Reminder")
                    r_date  = st.date_input("Reminder Date", value=date.today())
                    r_msg   = st.text_area("Details", height=60)
                    if st.form_submit_button("➕ Add Reminder", type="primary"):
                        from services.reminders import add as add_rem
                        add_rem("fisd", r_title, r_msg, r_date)
                        st.success("Reminder added!")
                        st.rerun()

        with sub2:
            st.markdown("#### 🎯 STAAR Exam Preparation")
            staar1, staar2, staar3, staar4 = st.tabs(["📋 Prep Plan", "🌐 Sites & Papers", "✏️ Section Tests", "📝 Full Mock Test"])
            with staar1:
                coming_soon("STAAR Preparation Plan — track progress by subject")
            with staar2:
                coming_soon("Curated STAAR practice sites & model papers")
            with staar3:
                coming_soon("Section-level practice tests with scoring")
            with staar4:
                coming_soon("Full-length mock STAAR tests")

        with sub3:
            st.markdown("#### 🔢 Math Rocks & Number Sense")
            st.info("💡 Specialized module for Number Sense competition preparation.")
            ns1, ns2 = st.tabs(["📖 Tips & Tricks", "🧪 Practice Tests"])
            with ns1:
                coming_soon("Number sense tricks — one topic card per trick with examples")
            with ns2:
                coming_soon("Timed practice tests in competition format")

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

    # ── Grade 7 ───────────────────────────────────────────────────────────────
    with g7:
        st.markdown("### 📗 Grade 7 — Planning Ahead")
        st.markdown('<div class="grade-badge">Upcoming · Grade 7</div>', unsafe_allow_html=True)
        g7a, g7b, g7c = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🌟 High School Prep"])

        with g7a:
            coming_soon("Grade 7 — Syllabus & monthly plan (mirrors Grade 6 structure)")
        with g7b:
            coming_soon("Grade 7 STAAR preparation")
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

    # ── Grade 8 ───────────────────────────────────────────────────────────────
    with g8:
        st.markdown("### 📙 Grade 8 — High School Bound")
        st.markdown('<div class="grade-badge">Future · Grade 8</div>', unsafe_allow_html=True)
        g8a, g8b, g8c = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🚀 HS & Beyond"])

        with g8a:
            coming_soon("Grade 8 — Syllabus & monthly plan")
        with g8b:
            coming_soon("Grade 8 STAAR preparation + high school readiness")
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

            col_ref, col_add = st.columns([3, 2])

            with col_ref:
                st.info("📎 Upload your 2026-2027 calendar PDF to populate dates automatically.")
                uploaded_cal = st.file_uploader("Upload Tamil School Calendar PDF", type=["pdf"], key="tamil_cal_upload")
                if uploaded_cal:
                    st.success("Calendar uploaded. Claude will extract dates — feature coming soon.")

            with col_add:
                st.markdown("##### ➕ Add Calendar Event")
                with st.form("tamil_cal_form"):
                    ev_title = st.text_input("Event")
                    ev_date  = st.date_input("Date", value=date.today())
                    ev_type  = st.selectbox("Type", ["Class Day","Holiday","No Class","Presentation","Competition","Other"])
                    if st.form_submit_button("Add", type="primary"):
                        from services.reminders import add as add_rem
                        add_rem("tamil", ev_title, ev_type, ev_date, remind_days=1, frequency="once", channels="push")
                        st.success(f"✅ Added: {ev_title}")
                        st.rerun()

            st.markdown("---")
            st.markdown("##### 📆 Saved Tamil School Events")
            try:
                rem_df_t = read_sheet("reminders")
                if not rem_df_t.empty:
                    tamil_evs = rem_df_t[rem_df_t["section"].str.lower() == "tamil"].copy()
                    if tamil_evs.empty:
                        st.info("No events added yet. Use the form above or upload the calendar PDF.")
                    else:
                        tamil_evs["due_date"] = pd.to_datetime(tamil_evs["due_date"], errors="coerce").dt.date
                        tamil_evs = tamil_evs.sort_values("due_date")
                        st.dataframe(
                            tamil_evs[["title","message","due_date","status"]].rename(
                                columns={"title":"Event","message":"Type","due_date":"Date","status":"Status"}
                            ),
                            use_container_width=True, hide_index=True,
                        )
                else:
                    st.info("No events yet.")
            except Exception:
                st.info("Connect Google Sheets to see events.")

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
                    rd   = st.date_input("Due Date", value=date.today())
                    rday = st.selectbox("Remind me (days before)", [0,1,3,7], index=1)
                    rch  = st.selectbox("Notify via", ["push","email","push,email"])
                if st.form_submit_button("Add Reminder", type="primary"):
                    if rt:
                        from services.reminders import add as add_rem
                        add_rem("tamil", rt, rm, rd, rday, "once", rch)
                        st.success(f"✅ Added: {rt}")
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

        m1, m2 = st.columns(2)
        m1.metric("Active Classes", len(cls_df) if not cls_df.empty else 0)
        m2.metric("Est. Monthly Cost", f"${monthly:,.0f}")

        if not cls_df.empty:
            st.dataframe(
                cls_df[["name","provider","cost","frequency","start_date"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No classes yet. Add one below.")

        with st.expander("➕ Add a Class / Activity"):
            with st.form("add_class_son"):
                c1, c2 = st.columns(2)
                with c1:
                    cname = st.text_input("Class Name (e.g. Chess, Swim, iTalk)")
                    cprov = st.text_input("Provider / Instructor")
                with c2:
                    ccost = st.number_input("Cost ($)", min_value=0.0, step=5.0)
                    cfreq = st.selectbox("Frequency", FREQUENCIES)
                cstart = st.date_input("Start Date", value=date.today())
                if st.form_submit_button("Add Class", type="primary"):
                    if cname:
                        add_class("Son", cname, cprov, ccost, cfreq, cstart)
                        st.success(f"✅ Added: {cname}")
                        st.rerun()

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

        m1, m2 = st.columns(2)
        m1.metric("Active Classes", len(cls_df_d) if not cls_df_d.empty else 0)
        m2.metric("Est. Monthly Cost", f"${monthly_d:,.0f}")

        if not cls_df_d.empty:
            st.dataframe(
                cls_df_d[["name","provider","cost","frequency","start_date"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No classes yet.")

        with st.expander("➕ Add a Class / Activity"):
            with st.form("add_class_daughter"):
                c1, c2 = st.columns(2)
                with c1:
                    cname = st.text_input("Class Name")
                    cprov = st.text_input("Provider")
                with c2:
                    ccost = st.number_input("Cost ($)", min_value=0.0, step=5.0)
                    cfreq = st.selectbox("Frequency", FREQUENCIES)
                cstart = st.date_input("Start Date", value=date.today())
                if st.form_submit_button("Add Class", type="primary"):
                    if cname:
                        add_class("Daughter", cname, cprov, ccost, cfreq, cstart)
                        st.success(f"✅ Added: {cname}")
                        st.rerun()

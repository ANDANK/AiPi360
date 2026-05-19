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

    g6, g7, g8, classes_tab = st.tabs(["📘 Grade 6", "📗 Grade 7", "📙 Grade 8", "📋 Classes & Fees"])

    # ── Grade 6 ───────────────────────────────────────────────────────────────
    with g6:
        st.markdown("### 📘 Grade 6 — FISD")
        sub1, sub2, sub3, sub4 = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🔢 Math Rocks", "🌟 Planning Ahead"])

        with sub1:
            st.markdown("#### Monthly Syllabus & Plan")
            col1, col2 = st.columns([2,1])
            with col1:
                coming_soon("Syllabus & YouTube resources — connect your school calendar to populate this")
            with col2:
                st.markdown("##### 🗓️ Upcoming School Events")
                try:
                    rem_df = read_sheet("reminders")
                    school_rems = rem_df[rem_df["section"].str.lower().isin(["fisd","school","kids"])] if not rem_df.empty else pd.DataFrame()
                    if school_rems.empty:
                        st.info("No school reminders yet.")
                    else:
                        for _, r in school_rems.head(5).iterrows():
                            st.markdown(f"• **{r['title']}** — {r.get('due_date','')}")
                except Exception:
                    st.info("Add school reminders in the Calendar section.")

                st.markdown("##### 🔔 Add School Reminder")
                with st.form("school_rem_form"):
                    r_title = st.text_input("Event / Reminder")
                    r_date  = st.date_input("Date", value=date.today())
                    r_msg   = st.text_area("Details", height=60)
                    if st.form_submit_button("➕ Add", type="primary"):
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

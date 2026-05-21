"""UIL A+ Academic Study Materials — renderer for the UIL Study Center tab."""
import os
import base64
import streamlit as st

_SCHOOL = os.path.join(os.path.dirname(__file__), "..", "uploads", "school")
_UIL_PAGE = "https://www.uiltexas.org/aplus/page/2024-aplus-academics-study-materials"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _path(filename: str) -> str:
    return os.path.join(_SCHOOL, filename)


def _exists(filename: str) -> bool:
    return os.path.isfile(_path(filename))


def _dl_btn(filename: str, label: str, key: str) -> None:
    """Download button — silently skipped if file not present."""
    p = _path(filename)
    if os.path.isfile(p):
        with open(p, "rb") as f:
            data = f.read()
        st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime="application/pdf",
            key=key,
            use_container_width=True,
        )
    else:
        st.caption(f"⚠️ {filename} not found on disk")


def _pdf_preview(filename: str, height: int = 520) -> None:
    """Embed PDF inline via base64 iframe (works on Streamlit Cloud)."""
    p = _path(filename)
    if not os.path.isfile(p):
        st.info("PDF preview not available — use the download button above.")
        return
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" '
        f'width="100%" height="{height}px" style="border:1px solid #e2e8f0;border-radius:8px"></iframe>',
        unsafe_allow_html=True,
    )


def _format_card(questions: int, time_min: int, calc: bool, extra: str = "") -> None:
    calc_txt = "Calculator allowed" if calc else "No calculator"
    st.markdown(
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 14px 0">'
        f'<span style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;'
        f'padding:5px 14px;font-size:13px;font-weight:600;color:#1d4ed8">📝 {questions} Questions</span>'
        f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
        f'padding:5px 14px;font-size:13px;font-weight:600;color:#059669">⏱️ {time_min} Minutes</span>'
        f'<span style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;'
        f'padding:5px 14px;font-size:13px;font-weight:600;color:#b45309">'
        f'{"🔢" if calc else "🚫"} {calc_txt}</span>'
        + (f'<span style="background:#fdf4ff;border:1px solid #e9d5ff;border-radius:8px;'
           f'padding:5px 14px;font-size:13px;color:#7c3aed">{extra}</span>' if extra else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def _ext_link_card(label: str, desc: str, url: str) -> None:
    st.markdown(
        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;'
        f'padding:12px 16px;margin-bottom:8px">'
        f'<a href="{url}" target="_blank" style="font-weight:600;color:#2563eb;font-size:14px">'
        f'🔗 {label}</a>'
        f'<div style="font-size:12px;color:#64748b;margin-top:3px">{desc}</div></div>',
        unsafe_allow_html=True,
    )


def _section_header(title: str, color: str = "#1d4ed8") -> None:
    st.markdown(
        f'<div style="font-size:14px;font-weight:700;color:{color};'
        f'border-bottom:2px solid {color}33;padding-bottom:4px;margin:16px 0 10px 0">'
        f'{title}</div>',
        unsafe_allow_html=True,
    )


# ── Subject renderers ─────────────────────────────────────────────────────────

def _render_number_sense() -> None:
    st.markdown("#### 🔢 Number Sense")
    st.caption("80 mental-math problems · 10 minutes · no calculator — the ultimate speed-math event")
    _format_card(80, 10, False, "Individual · Grades 4–8")

    st.markdown("""
> **What it tests:** Pure mental arithmetic — fractions, decimals, percents, squares, cubes,
> prime factorization, divisibility, and dozens of learnable *shortcuts* (tricks).
> The top secret: **the tricks are learnable**. Most top scorers learn 40–60 specific patterns
> and apply them at speed. You don't need genius — you need practice and the right study materials.
""")

    c1, c2 = st.columns([1, 1])

    with c1:
        _section_header("📦 2024-25 Official Packet", "#059669")
        _dl_btn("Number_Sense_Packet_2425.pdf", "📥 Download 2024-25 Study Packet", "ns_2425")
        with st.expander("📄 Preview Study Packet", expanded=False):
            _pdf_preview("Number_Sense_Packet_2425.pdf", height=480)

        _section_header("📦 2023-24 Packet (extra practice)", "#059669")
        _dl_btn("Number_Sense_Packet_2324.pdf", "📥 Download 2023-24 Packet", "ns_2324")

        _section_header("📝 Sample Tests with Answer Keys")
        _dl_btn("A+_Number_Sense_Sample_Test_and_Key.pdf", "📥 Sample Test + Answer Key", "ns_sample")
        with st.expander("📄 Preview Sample Test", expanded=False):
            _pdf_preview("A+_Number_Sense_Sample_Test_and_Key.pdf", height=480)
        _dl_btn("MS_Q076.pdf", "📥 Middle School Practice Test (Q076)", "ns_ms_q076")
        _dl_btn("numbersense.pdf", "📥 Number Sense Practice Set", "ns_general")
        _dl_btn("2022_A+_Elementary_Number_Sense.pdf", "📥 2022 A+ Elementary Number Sense", "ns_2022_el")

        _section_header("📝 Numbered Practice Tests")
        for fname, label in [
            ("12200.pdf", "Practice Test 12200"),
            ("12210.pdf", "Practice Test 12210"),
            ("12220.pdf", "Practice Test 12220"),
            ("12320.pdf", "Practice Test 12320"),
        ]:
            _dl_btn(fname, f"📥 {label}", f"ns_{fname[:5]}")

    with c2:
        _section_header("💡 Tricks & Tips Guides", "#dc2626")
        _dl_btn("Number_Sense_Tips.pdf", "📥 Number Sense Tips Guide", "ns_tips1")
        with st.expander("📄 Preview Tips Guide", expanded=False):
            _pdf_preview("Number_Sense_Tips.pdf", height=480)
        _dl_btn("Number_Sense_Tips (1).pdf", "📥 Number Sense Tips (v2)", "ns_tips2")
        _dl_btn("Heath_NSTricks_revA.pdf", "📥 Heath Tricks Guide (revA)", "ns_heath")
        with st.expander("📄 Preview Heath Tricks", expanded=False):
            _pdf_preview("Heath_NSTricks_revA.pdf", height=480)
        _dl_btn("HS_Number_Sense_Tips_for_Coaches.pdf", "📥 Coach Tips (HS level)", "ns_coach")

        _section_header("📊 Sequence Charts & Problem Sets", "#7c3aed")
        _dl_btn("APlus_NumberSense_SequenceChart_rev1617.pdf",
                "📥 A+ Sequence Chart (2016-17)", "ns_seq")
        with st.expander("📄 Preview Sequence Chart", expanded=False):
            _pdf_preview("APlus_NumberSense_SequenceChart_rev1617.pdf", height=400)
        _dl_btn("number_dojo_el_prob_seq_1-20.pdf", "📥 Number Dojo Sequences 1-20", "ns_dojo")
        _dl_btn("uil_el_prob_seq_1-20.pdf", "📥 UIL Elementary Sequences 1-20", "ns_uil_el")

        _section_header("🌐 Official UIL Resources")
        _ext_link_card(
            "UIL Number Sense Official Page",
            "Official rules, additional past tests, and coach resources",
            "https://www.uiltexas.org/academics/math/number-sense",
        )
        _ext_link_card(
            "Developing MS Number Sense (11MB — UIL site)",
            "Comprehensive middle school guide — too large to embed, download from UIL",
            _UIL_PAGE,
        )
        _ext_link_card(
            "UIL A+ Full Study Materials Page",
            "All 2024-25 official study packets including full junior high bundle",
            _UIL_PAGE,
        )

    st.divider()
    with st.expander("🚀 Quick-Start Trick Sheet — Top 15 Number Sense Shortcuts", expanded=False):
        st.markdown("""
| # | Trick | Example | Shortcut |
|---|-------|---------|----------|
| 1 | Multiply by 11 | 47 × 11 | Split digits, add middle: 4(4+7)7 = 517 |
| 2 | Square numbers ending in 5 | 65² | Tens digit × (tens+1), append 25: 6×7=42 → **4225** |
| 3 | Fractions to decimals | 1/8 | Memorize: 1/8=.125, 1/6=.1667, 1/7≈.143 |
| 4 | Percent of a number | 35% of 80 | Flip: 80% of 35 = 28 (same answer, often easier) |
| 5 | Multiply two numbers near 100 | 97×98 | (100−3)(100−2) = 10000 − 500 + 6 = **9506** |
| 6 | Squares of consecutive integers | 13²=169, 14²=? | Add 13+14=27 to 169 → **196** |
| 7 | Divisibility by 7 | 161 ÷ 7? | Double last digit, subtract: 16−2=14 ✓ |
| 8 | LCM quick | LCM(8,12) | Larger × (smaller ÷ GCF): 12×(8÷4)=**24** |
| 9 | Mixed number × whole | 2⅓ × 9 | (2×9)+(⅓×9) = 18+3 = **21** |
| 10 | Powers of 2 | 2¹⁰ | Memorize: 2^10=1024, 2^11=2048, 2^12=4096 |
| 11 | Multiply by 25 | 36 × 25 | ÷4 then ×100: 36/4=9, 9×100=**900** |
| 12 | Multiply by 125 | 48 × 125 | ÷8 then ×1000: 48/8=6, 6×1000=**6000** |
| 13 | Sum 1 to n | Sum 1–100 | n(n+1)/2 = 100×101/2 = **5050** |
| 14 | Difference of squares | 52²−48² | (52+48)(52−48) = 100×4 = **400** |
| 15 | Remainder tricks | 347 mod 9 | Sum digits: 3+4+7=14 → 1+4=5 remainder **5** |

> 📚 Study the full trick sets in the **Heath Tricks Guide** and **Number Sense Tips** downloads above.
> Practice each trick 20 times until it's automatic before moving to the next.
""")


def _render_mathematics() -> None:
    st.markdown("#### ➕ Mathematics")
    st.caption("30 problems · 40 minutes · no calculator — conceptual math and problem solving")
    _format_card(30, 40, False, "Individual · Grades 6–8")

    st.markdown("""
> **What it tests:** Mathematical reasoning across algebra, geometry, number theory,
> statistics, and problem solving. Unlike Number Sense (pure speed), Mathematics rewards
> *careful reading and structured solutions*. Show-your-work discipline matters.
> Topics follow the TEKS curriculum but go significantly deeper.
""")

    c1, c2 = st.columns([1, 1])
    with c1:
        _section_header("📦 Official 2024-25 Study Packet", "#059669")
        _dl_btn("Mathematics_Packet_2425.pdf", "📥 Download 2024-25 Mathematics Packet", "math_2425")
        with st.expander("📄 Preview Mathematics Packet", expanded=False):
            _pdf_preview("Mathematics_Packet_2425.pdf", height=500)

        _section_header("📝 Strategy & Practice")
        _dl_btn("Math Ninja Bill.pdf", "📥 Math Ninja Bill — Strategy Guide", "math_ninja")
        with st.expander("📄 Preview Math Ninja Bill", expanded=False):
            _pdf_preview("Math Ninja Bill.pdf", height=480)
        _dl_btn("sample-book.pdf", "📥 Sample Problem Book", "math_sample")

    with c2:
        _section_header("📚 Topics Tested (Grade 6 focus)")
        for topic, detail in [
            ("Number Theory",    "Primes, GCF, LCM, divisibility rules, factoring"),
            ("Fractions/Ratios", "Complex fractions, ratios, proportions, unit rates"),
            ("Algebra",          "One/two-step equations, inequalities, patterns"),
            ("Geometry",         "Area, perimeter, volume, angle relationships"),
            ("Statistics",       "Mean, median, mode, range, basic probability"),
            ("Word Problems",    "Multi-step real-world problems — read carefully"),
        ]:
            st.markdown(
                f'<div style="background:#f8fafc;border-left:3px solid #3b82f6;'
                f'border-radius:0 6px 6px 0;padding:6px 10px;margin-bottom:5px;font-size:13px">'
                f'<b>{topic}:</b> <span style="color:#475569">{detail}</span></div>',
                unsafe_allow_html=True,
            )
        _section_header("🌐 Official UIL Resources")
        _ext_link_card(
            "UIL Mathematics Official Page",
            "Rules, past tests, and additional study guides",
            "https://www.uiltexas.org/academics/math/mathematics",
        )


def _render_science() -> None:
    st.markdown("#### 🔬 Science")
    st.caption("30 questions · 30 minutes · no calculator — life, earth, and physical science")
    _format_card(30, 30, False, "Individual · Grades 6–8")

    st.markdown("""
> **What it tests:** Questions draw from biology, chemistry, earth science, physics, and
> scientific reasoning. Grade 6 content covers TEKS but extends into Grade 7–8 topics.
> The 2024-25 study packet is the primary resource — read every page.
""")

    c1, c2 = st.columns([1, 1])
    with c1:
        _section_header("📦 Official 2024-25 Study Packet", "#059669")
        _dl_btn("Science_Packet_2425.pdf", "📥 Download 2024-25 Science Packet", "sci_2425")
        with st.expander("📄 Preview Science Packet", expanded=False):
            _pdf_preview("Science_Packet_2425.pdf", height=520)

    with c2:
        _section_header("📚 Topics by Domain")
        for domain, topics in [
            ("Life Science",     "Cell biology, genetics, ecosystems, classification, human body systems"),
            ("Earth Science",    "Rock cycle, plate tectonics, weather, space, natural resources"),
            ("Physical Science", "Matter, energy, forces, motion, electricity, waves, light"),
            ("Sci. Reasoning",   "Hypothesis, variables, data interpretation, lab safety"),
        ]:
            st.markdown(
                f'<div style="background:#ecfeff;border-left:3px solid #0891b2;'
                f'border-radius:0 6px 6px 0;padding:6px 10px;margin-bottom:5px;font-size:13px">'
                f'<b>{domain}:</b> <span style="color:#475569">{topics}</span></div>',
                unsafe_allow_html=True,
            )
        _section_header("🌐 Official UIL Resources")
        _ext_link_card(
            "UIL Science Official Page",
            "Official rules, past tests, and suggested reading",
            "https://www.uiltexas.org/academics/science",
        )


def _render_maps() -> None:
    st.markdown("#### 🗺️ Maps, Graphs & Charts")
    st.caption("45 questions · 30 minutes · skills-based data interpretation")
    _format_card(45, 30, False, "Individual · Grades 5–8")

    st.markdown("""
> **What it tests:** Reading and interpreting maps (scales, legends, coordinates, latitude/longitude),
> bar/line/pie charts, tables, diagrams, and data analysis.
> Strong overlap with Math skills — students who do well in Math tend to do well here.
> The 2024-25 packet (27MB) is too large to embed — download directly from UIL below.
""")

    c1, c2 = st.columns([1, 1])
    with c1:
        _section_header("📦 Official 2024-25 Packet (External)", "#b45309")
        _ext_link_card(
            "Maps, Graphs & Charts 2024-25 Packet (27MB PDF)",
            "Download directly from UIL A+ page — too large to serve in-app",
            _UIL_PAGE,
        )
        _ext_link_card(
            "UIL Maps/Graphs/Charts Official Page",
            "Rules, past tests, and supplemental resources",
            "https://www.uiltexas.org/academics/current-events/maps-graphs-charts",
        )
    with c2:
        _section_header("📚 Topics")
        for t in [
            "Map scales — compute real distances from map measurements",
            "Map legends — interpret symbols, colors, and patterns",
            "Latitude and longitude — locate points, compute distances",
            "Time zones — compute time differences across zones",
            "Bar/line/pie charts — read values, trends, and percentages",
            "Tables — find values, compute totals, compare data",
            "Diagrams — flowcharts, organizational charts, Venn diagrams",
        ]:
            st.markdown(f"- {t}")


def _render_impromptu() -> None:
    st.markdown("#### 🎤 Impromptu Speaking")
    st.caption("2 min prep · 4 min speech · on-the-spot speaking skills")
    _format_card(0, 4, False, "Individual · Grades 6–8 · Speech event")

    st.markdown("""
> **What it tests:** The ability to speak coherently and persuasively on an unknown topic
> with only 2 minutes of preparation. Judges score on: content & development, organization,
> delivery (eye contact, voice, gestures), and language (word choice, clarity).
> **Your Gavel Club experience is a major advantage here.**
> The Table Topics you practice weekly is almost identical to the UIL Impromptu format.
""")

    c1, c2 = st.columns([1, 1])
    with c1:
        _section_header("📦 Official 2024-25 Study Packet", "#059669")
        _dl_btn("Impromptu_Speaking_Packet_2425.pdf",
                "📥 Download 2024-25 Impromptu Speaking Packet", "imp_2425")
        with st.expander("📄 Preview Impromptu Speaking Packet", expanded=False):
            _pdf_preview("Impromptu_Speaking_Packet_2425.pdf", height=500)

    with c2:
        _section_header("🗣️ Gavel Club Connection")
        st.info(
            "**You're already training for this every week.** "
            "UIL Impromptu Speaking = UIL-official version of Gavel Club Table Topics. "
            "The same PREP framework applies:\n\n"
            "**P**oint → **R**eason → **E**xample → **P**oint (restate)\n\n"
            "Use your Gavel Club meeting time to practice 3–4 Impromptu topics each session.",
            icon="🎙️",
        )
        _section_header("📐 Scoring Breakdown")
        for criterion, pts, desc in [
            ("Content & Development",   "40 pts", "Clear position, well-developed ideas, logic"),
            ("Organization",            "30 pts", "Intro, 2-3 main points, strong close"),
            ("Delivery",                "20 pts", "Eye contact, voice, gestures, no filler words"),
            ("Language",                "10 pts", "Vocabulary, grammar, sentence variety"),
        ]:
            st.markdown(
                f'<div style="background:#fdf4ff;border-left:3px solid #a21caf;'
                f'border-radius:0 6px 6px 0;padding:6px 10px;margin-bottom:5px;font-size:13px">'
                f'<b>{criterion}</b> <span style="color:#7c3aed;font-weight:700">{pts}</span>'
                f'<br><span style="color:#475569;font-size:11px">{desc}</span></div>',
                unsafe_allow_html=True,
            )
        _ext_link_card(
            "UIL Impromptu Speaking Official Page",
            "Rules, past prompts, and judge guidelines",
            "https://www.uiltexas.org/academics/language/impromptu-speaking",
        )


def _render_chess() -> None:
    st.markdown("#### ♟️ Chess Puzzle")
    st.caption("Solve chess puzzles in a timed test format — pattern recognition over game play")
    _format_card(30, 30, False, "Individual · Grades 2–8")

    st.markdown("""
> **What it tests:** Chess puzzle recognition — checkmate-in-X, fork, pin, skewer, discovered attack.
> You do NOT need to be a strong tournament chess player. You need to recognize tactical patterns quickly.
> The 2024-25 packet (12MB) is too large to embed — download directly from UIL.
""")

    c1, c2 = st.columns([1, 1])
    with c1:
        _section_header("📦 Official 2024-25 Packet (External)", "#b45309")
        _ext_link_card(
            "Chess Puzzle 2024-25 Packet (12MB PDF)",
            "Download directly from UIL A+ page",
            _UIL_PAGE,
        )
        _ext_link_card("UIL Chess Puzzle Official Page", "Rules and past tests",
                       "https://www.uiltexas.org/academics/other-academics/chess-puzzle")
    with c2:
        _section_header("📚 Tactical Patterns to Learn")
        for p in ["Checkmate in 1 / 2 moves", "Fork — one piece attacks two",
                  "Pin — piece can't move without exposing king",
                  "Skewer — like a pin but attacks the more valuable piece first",
                  "Discovered Attack — moving one piece reveals attack by another",
                  "Back-rank mate — rook/queen delivers mate on opponent's back rank"]:
            st.markdown(f"- {p}")
        _ext_link_card("Chess.com Puzzles (free practice)", "Solve daily puzzles online",
                       "https://www.chess.com/puzzles")


def _render_full_packets() -> None:
    st.markdown("#### 📦 Full Study Bundles")
    st.caption("Complete packets covering all events — too large to embed, link to UIL directly")

    st.markdown("""
The UIL A+ full bundles contain **all events** in a single PDF.
These are the primary study resource for students preparing for multiple events.
Download them from the official UIL page below.
""")

    _ext_link_card(
        "Junior High Full Bundle 2024-25 (~20MB)",
        "All Grade 6-8 events: Number Sense, Math, Science, Maps/Charts, "
        "Impromptu Speaking, Chess, Social Studies, Dictionary Skills, Spelling, "
        "Music Memory, and more",
        _UIL_PAGE,
    )
    _ext_link_card(
        "Elementary Full Bundle 2024-25 (~27MB)",
        "All Grade 2-8 events — includes events not in Junior High bundle",
        _UIL_PAGE,
    )
    _ext_link_card(
        "UIL A+ Official Study Materials Page",
        "Source for all official 2024-25 packets + archive of 2018–2023 materials",
        _UIL_PAGE,
    )

    st.markdown("---")
    st.markdown("##### 📅 Competition Calendar (FISD typical schedule)")
    for lvl, when, detail in [
        ("School Meet",    "February",    "Internal competition — top scorers in each event advance"),
        ("District Meet",  "March",       "Competition against other FISD schools — top 3 advance"),
        ("Regional Meet",  "April",       "Competition across NE Texas region — top 3 advance to State"),
        ("State Meet",     "May (Austin)","University of Texas campus — most prestigious level for MS"),
    ]:
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:flex-start;'
            f'margin-bottom:8px;font-size:13px">'
            f'<span style="min-width:110px;font-weight:600;color:#1d4ed8">{lvl}</span>'
            f'<span style="min-width:80px;color:#059669;font-weight:500">{when}</span>'
            f'<span style="color:#334155">{detail}</span></div>',
            unsafe_allow_html=True,
        )


# ── Main renderer ─────────────────────────────────────────────────────────────

def render_uil_center() -> None:
    """Full UIL Study Center — call from the UIL tab in the Kids page."""

    # Header
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1d4ed8 0%,#0891b2 100%);'
        'border-radius:14px;padding:18px 22px;margin-bottom:16px;color:#fff">'
        '<div style="font-size:20px;font-weight:800;letter-spacing:-0.03em">'
        '🏅 UIL A+ Academic Competitions — Study Center</div>'
        '<div style="font-size:12px;opacity:0.85;margin-top:4px">'
        'FISD · Grade 6–8 · School → District → Regional → State</div></div>',
        unsafe_allow_html=True,
    )

    col_link, col_info = st.columns([2, 3])
    with col_link:
        st.link_button(
            "🌐 Official UIL A+ 2024-25 Study Materials Page",
            url=_UIL_PAGE,
            use_container_width=True,
        )
    with col_info:
        st.caption(
            "All packets below come from the official UIL A+ website. "
            "Small packets (< 2MB) are served from local files for fast access. "
            "Large packets link directly to UIL."
        )

    # Subject tabs
    t_ns, t_math, t_sci, t_maps, t_imp, t_chess, t_pkg = st.tabs([
        "🔢 Number Sense",
        "➕ Mathematics",
        "🔬 Science",
        "🗺️ Maps/Charts",
        "🎤 Impromptu",
        "♟️ Chess",
        "📦 Full Packets",
    ])

    with t_ns:    _render_number_sense()
    with t_math:  _render_mathematics()
    with t_sci:   _render_science()
    with t_maps:  _render_maps()
    with t_imp:   _render_impromptu()
    with t_chess: _render_chess()
    with t_pkg:   _render_full_packets()

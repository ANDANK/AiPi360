"""AMC practice test data and Streamlit renderer."""
import time as _time

import streamlit as st
import streamlit.components.v1 as _comp

# ── 2026 AMC 8 ────────────────────────────────────────────────────────────────

_AOPS_2026 = "https://artofproblemsolving.com/wiki/index.php/2026_AMC_8"

_P2026 = [
    dict(
        num=1, answer="A",
        choices=["18", "21", "24", "27", "30"],
        text="What is the value of the following expression?",
        latex=r"1 + 2 - 3 + 4 + 5 - 6 + 7 + 8 - 9 + 10 + 11 - 12",
    ),
    dict(
        num=2, answer="C",
        choices=["49", "51", "53", "55", "57"],
        text=(
            "In the array shown below, three 3s are surrounded by 2s, which are in turn "
            "surrounded by a border of 1s. What is the sum of the numbers in the array?"
        ),
        latex=r"\begin{array}{ccccccc}1&1&1&1&1&1&1\\1&2&2&2&2&2&1\\1&2&3&3&3&2&1\\1&2&2&2&2&2&1\\1&1&1&1&1&1&1\end{array}",
    ),
    dict(
        num=3, answer="D",
        choices=[
            "Triangle only",
            "Hexagon and square only",
            "Hexagon and triangle only",
            "Square and triangle only",
            "Hexagon, triangle, and square",
        ],
        text=(
            "Haruki has a piece of wire that is 24 centimeters long. "
            "He wants to bend it to form each of the following shapes, one at a time:\n\n"
            "1. A regular hexagon with side length 5 cm.\n"
            "2. A square of area 36 cm².\n"
            "3. A right triangle whose legs are 6 and 8 cm long.\n\n"
            "Which of the shapes can Haruki make?"
        ),
    ),
    dict(
        num=4, answer="E",
        choices=["80", "90", "100", "110", "120"],
        text=(
            "Brynn's savings decreased by 20% in July, then increased by 50% of the new "
            "amount in August. Brynn's savings are now what percent of the original amount?"
        ),
    ),
    dict(
        num=5, answer="B",
        choices=["15", "30", "40", "45", "60"],
        text=(
            "Casey went on a road trip that covered 100 miles, stopping only for a lunch "
            "break along the way. The trip took 3 hours in total and her average speed "
            "while driving was 40 miles per hour. In minutes, how long was the lunch break?"
        ),
    ),
    dict(
        num=6, answer="E",
        choices=["1/6", "1/4", "1/3", "3/8", "2/5"],
        figure=True,
        text=(
            "Peter lives near a rectangular field that is filled with blackberry bushes. "
            "The field is 10 meters long and 8 meters wide, and Peter can reach any "
            "blackberries that are within 1 meter of an edge of the field. "
            "The portion of the field he can reach is shaded in the figure. "
            "What fraction of the area of the field can Peter reach?"
        ),
    ),
    dict(
        num=7, answer="C",
        choices=["45", "48", "50", "52", "55"],
        text=(
            "Mika would like to estimate how far she can ride a new model of electric bike "
            "on a fully charged battery. She completed two trips totaling 40 miles. "
            "The first trip used 1/2 of the total battery power, while the second trip "
            "used 3/10 of the total battery power. How many miles can this electric bike "
            "go on a fully charged battery?"
        ),
    ),
    dict(
        num=8, answer="D",
        choices=["10", "20", "25", "50", "100"],
        text=(
            'A poll asked a number of people if they liked solving mathematics problems. '
            'Exactly 74% answered "yes." What is the fewest possible number of people '
            "who could have been asked the question?"
        ),
    ),
    dict(
        num=9, answer="B",
        choices=["4/9", "2/3", "1", "3/2", "9/4"],
        text="What is the value of this expression?",
        latex=r"\frac{\sqrt{16\sqrt{81}}}{\sqrt{81\sqrt{16}}}",
    ),
    dict(
        num=10, answer="A",
        choices=["Luke", "Melina", "Nico", "Olympia", "Pedro"],
        text=(
            "Five runners completed the grueling Xmarathon: Luke, Melina, Nico, Olympia, "
            "and Pedro.\n\n"
            "- Nico finished 11 minutes behind Pedro.\n"
            "- Olympia finished 2 minutes ahead of Melina, but 3 minutes behind Pedro.\n"
            "- Olympia finished 6 minutes ahead of Luke.\n\n"
            "Which runner finished fourth?"
        ),
    ),
    dict(
        num=11, answer="B",
        choices=["4π", "6π", "13π/2", "8π", "13π"],
        figure=True,
        text=(
            "Squares of side length 1, 1, 2, 3, and 5 are arranged to form a rectangle. "
            "A curve is drawn by inscribing a quarter circle in each square and joining "
            "the quarter circles in order, from shortest to longest. "
            "What is the length of the curve?"
        ),
    ),
    dict(
        num=12, answer="D",
        choices=["2", "3", "4", "5", "It is impossible to fill the circles"],
        figure=True,
        text=(
            "In the figure below, each circle will be filled with a digit from 1 to 6. "
            "Each digit must appear exactly once. The sum of the digits in neighboring "
            "circles is shown in the box between them. "
            "What digit must be placed in the top circle?"
        ),
    ),
    dict(
        num=13, answer="A",
        choices=["10", "21/2", "32/3", "11", "34/3"],
        figure=True,
        text=(
            "The figure below shows a tiling of 1×1 unit squares. Each row of unit "
            "squares is shifted horizontally by half a unit relative to the row above it. "
            "A shaded square is drawn on top of the tiling with each vertex at a vertex "
            "of a unit square. In square units, what is the area of the shaded square?"
        ),
    ),
    dict(
        num=14, answer="B",
        choices=["70", "75", "80", "85", "90"],
        text=(
            "Jami picked three equally spaced integer numbers on the number line. "
            "The sum of the first and the second numbers is 40, while the sum of the "
            "second and third numbers is 60. What is the sum of all three numbers?"
        ),
    ),
    dict(
        num=15, answer="A",
        choices=["4", "6", "8", "9", "27"],
        figure=True,
        text=(
            "Elijah has a large collection of identical wooden cubes which are white on "
            "4 faces and gray on 2 faces that share an edge. He glues some cubes together "
            "face-to-face. The figure shows 2 cubes glued together, leaving 3 gray faces "
            "visible. What is the fewest number of cubes he could glue together to ensure "
            "no gray faces are visible, no matter how he rotates the figure?"
        ),
    ),
    dict(
        num=16, answer="D",
        choices=["1/4", "2/5", "1/2", "3/5", "3/4"],
        text=(
            "Consider all positive four-digit integers consisting of only even digits. "
            "What fraction of these integers are divisible by 4?"
        ),
    ),
    dict(
        num=17, answer="A",
        choices=["2", "4", "9", "12", "24"],
        figure=True,
        text=(
            "Four students are seated in a row. They chat with the people sitting next "
            "to them, then rearrange themselves so that they are no longer seated next "
            "to any of the same people. How many rearrangements are possible?"
        ),
    ),
    dict(
        num=18, answer="B",
        choices=["1", "2", "3", "4", "5"],
        text=(
            "In how many ways can 60 be written as the sum of two or more consecutive "
            "odd positive integers that are arranged in increasing order?"
        ),
    ),
    dict(
        num=19, answer="D",
        choices=["1/6", "1/5", "1/4", "1/3", "2/5"],
        figure=True,
        text=(
            "Miguel is walking with his dog, Luna. When they reach the entrance to a "
            "park, Miguel throws a ball straight ahead and continues to walk at a steady "
            "pace. Luna sprints toward the ball, which stops by a tree. As soon as the "
            "dog reaches the ball, she brings it back to Miguel. Luna runs 5 times faster "
            "than Miguel walks. What fraction of the distance between the entrance and "
            "the tree does Miguel cover by the time Luna brings him the ball?"
        ),
    ),
    dict(
        num=20, answer="D",
        choices=["3", "7", "10", "13", "16"],
        text=(
            "The land of Catania uses gold coins and silver coins. Gold coins are 1 mm "
            "thick and silver coins are 3 mm thick. In how many ways can Taylor make a "
            "stack of coins that is 8 mm tall using any arrangement of gold and silver "
            "coins, assuming order matters?"
        ),
    ),
    dict(
        num=21, answer="B",
        choices=["1/5", "1/4", "2/5", "1/2", "3/5"],
        figure=True,
        text=(
            "Charlotte the spider is walking along a web shaped like a 5-pointed star "
            "with 5 outer points and 5 inner points. Each time Charlotte reaches a point, "
            "she randomly chooses a neighboring point and moves to that point. Charlotte "
            "starts at one of the outer points and makes 3 moves (re-visiting points is "
            "allowed). What is the probability she is now at one of the outer points?"
        ),
    ),
    dict(
        num=22, answer="A",
        choices=["9", "10", "12", "13", "14"],
        text=(
            "The integers from 1 to 25 are arbitrarily separated into five groups of "
            "5 numbers each. The median of each group is identified. Let M equal the "
            "median of the five medians. What is the least possible value of M?"
        ),
    ),
    dict(
        num=23, answer="C",
        choices=["2π + 20", "5π/2 + 20", "4π + 20", "9π/2 + 20", "5π + 20"],
        figure=True,
        text=(
            "Lakshmi has 5 round coins of diameter 4 centimeters. She arranges the coins "
            "in 2 rows on a table top and wraps an elastic band tightly around them. "
            "In centimeters, what will be the length of the band?"
        ),
    ),
    dict(
        num=24, answer="E",
        choices=["147", "150", "156", "168", "171"],
        text=(
            'The notation n! (read "n factorial") is the product of the first n positive '
            "integers (e.g., 3! = 6). Define the superfactorial of n, written SF(n), to "
            "be the product of the factorials of the first n integers "
            "(e.g., SF(3) = 1! · 2! · 3! = 12). "
            "How many factors of 7 appear in the prime factorization of SF(51), "
            "the superfactorial of 51?"
        ),
    ),
    dict(
        num=25, answer="E",
        choices=["4", "5", "6", "7", "8"],
        figure=True,
        text=(
            "In an equiangular hexagon, all interior angles measure 120°. "
            "Consider all equiangular hexagons with positive integer side lengths that "
            "can be inscribed in an equilateral triangle, with all six vertices on the "
            "sides of the triangle. What is the total number of such hexagons? "
            "Hexagons that differ only by a rotation or a reflection are considered the same."
        ),
    ),
]

AMC8_2026 = {
    "title": "2026 AMC 8",
    "year": 2026,
    "time_min": 40,
    "source": _AOPS_2026,
    "problems": _P2026,
}

TESTS = {"2026 AMC 8": AMC8_2026}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _timer_html(end_ts: float) -> str:
    ms = int(end_ts * 1000)
    return f"""
<div id="amct" style="font-size:18px;font-weight:700;font-family:monospace;
 padding:5px 16px;border-radius:8px;display:inline-block;
 background:#eff6ff;border:1.5px solid #bfdbfe;color:#1d4ed8;">⏱️ --:--</div>
<script>(function(){{
  const end={ms};
  function tick(){{
    const rem=Math.max(0,Math.floor((end-Date.now())/1000));
    const el=document.getElementById('amct');
    if(!el)return;
    if(rem===0){{el.innerHTML='⏱️ TIME\\'S UP!';el.style.color='#dc2626';el.style.background='#fef2f2';el.style.borderColor='#fca5a5';return;}}
    const m=Math.floor(rem/60),s=rem%60;
    el.innerHTML='⏱️ '+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
    if(rem<300){{el.style.color='#dc2626';el.style.background='#fef2f2';el.style.borderColor='#fca5a5';}}
    setTimeout(tick,1000);
  }}
  tick();
}})();</script>"""


def _score_banner(correct: int, total: int):
    pct = correct / total
    if pct >= 21 / 25:
        label, color, bg = "\U0001f3c6 Distinguished Honor Roll!", "#14532d", "#dcfce7"
    elif pct >= 15 / 25:
        label, color, bg = "\U0001f948 Honor Roll", "#1e3a8a", "#dbeafe"
    elif pct >= 10 / 25:
        label, color, bg = "\U0001f4c8 Good effort — keep going!", "#78350f", "#fef3c7"
    else:
        label, color, bg = "\U0001f4da Keep practicing — you'll get there!", "#7f1d1d", "#fee2e2"
    st.markdown(
        f'<div style="padding:14px 20px;border-radius:10px;background:{bg};margin:8px 0">'
        f'<span style="font-size:28px;font-weight:800;color:{color}">{correct}/{total}</span>'
        f'&nbsp;&nbsp;<span style="font-size:16px;font-weight:600;color:{color}">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.progress(pct)


def _reset(kp: str, t: dict):
    for k in ("started", "submitted", "start_ts", "saved"):
        st.session_state.pop(f"{kp}_{k}", None)
    for p in t["problems"]:
        st.session_state.pop(f"{kp}_q{p['num']}", None)
    st.rerun()


# ── Problem renderer ──────────────────────────────────────────────────────────

def _render_problem(p: dict, kp: str, submitted: bool):
    num         = p["num"]
    key         = f"{kp}_q{num}"
    saved       = st.session_state.get(f"{kp}_saved", {})
    sel         = saved.get(num) if submitted else st.session_state.get(key)
    correct_ans = p["answer"]
    is_right    = submitted and sel == correct_ans
    is_wrong    = submitted and bool(sel) and sel != correct_ans

    icon = (" ✅" if is_right else " ❌" if is_wrong else " ⬜") if submitted else ""
    fig  = f"  [\U0001f4d0 figure on AoPS]({_AOPS_2026})" if p.get("figure") else ""

    with st.container(border=True):
        st.markdown(f"**Problem {num}**{icon}{fig}", unsafe_allow_html=True)
        st.markdown(p["text"])
        if p.get("latex"):
            st.latex(p["latex"])

        cols = st.columns(5)
        for i, letter in enumerate("ABCDE"):
            choice = p["choices"][i]
            with cols[i]:
                if submitted:
                    if letter == correct_ans:
                        st.markdown(
                            f'<span style="color:#16a34a;font-weight:700">({letter}) {choice} ✓</span>',
                            unsafe_allow_html=True,
                        )
                    elif letter == sel:
                        st.markdown(
                            f'<span style="color:#dc2626">({letter}) {choice} ✗</span>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<span style="color:#94a3b8">({letter}) {choice}</span>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(f"({letter}) {choice}")

        if not submitted:
            st.radio(
                "", ["A", "B", "C", "D", "E"],
                key=key, horizontal=True, index=None,
                label_visibility="collapsed",
            )
        else:
            if is_right:
                st.success(f"Your answer: **{sel}** — Correct! ✅")
            elif is_wrong:
                st.error(f"Your answer: **{sel}** — Correct answer: **{correct_ans}**")
            else:
                st.warning(f"Not answered — Correct answer: **{correct_ans}**")


# ── Test renderer ─────────────────────────────────────────────────────────────

def _render_test(t: dict):
    kp = f"ptest_{t['year']}"
    st.session_state.setdefault(f"{kp}_started",   False)
    st.session_state.setdefault(f"{kp}_submitted",  False)
    st.session_state.setdefault(f"{kp}_start_ts",   0.0)
    st.session_state.setdefault(f"{kp}_saved",      {})

    started   = st.session_state[f"{kp}_started"]
    submitted = st.session_state[f"{kp}_submitted"]

    st.markdown(f"### {t['title']}")
    st.caption(
        f"25 questions · {t['time_min']} minutes · 1 pt each · "
        f"No penalty for wrong answers · "
        f"[Full test + figures on AoPS ↗]({t['source']})"
    )

    if not started:
        with st.container(border=True):
            st.markdown("**Instructions**")
            st.markdown(
                "- 25 multiple-choice questions (A–E).\n"
                "- Select one answer per problem. You may change answers before submitting.\n"
                "- No penalty for wrong answers — attempt every problem.\n"
                "- Problems marked \U0001f4d0 include a figure; tap the link to view it on AoPS.\n"
                "- Press **Start Test** when ready — the 40-minute countdown begins immediately."
            )
        if st.button("▶️  Start Test", type="primary"):
            st.session_state[f"{kp}_started"]  = True
            st.session_state[f"{kp}_start_ts"] = _time.time()
            st.rerun()
        return

    if not submitted:
        end_ts = st.session_state[f"{kp}_start_ts"] + t["time_min"] * 60
        _comp.html(_timer_html(end_ts), height=48)

    for p in t["problems"]:
        _render_problem(p, kp, submitted)

    st.divider()

    if not submitted:
        answered = sum(
            1 for p in t["problems"]
            if st.session_state.get(f"{kp}_q{p['num']}")
        )
        st.caption(f"{answered} / 25 answered")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("✅  Submit Test", type="primary"):
                saved = {
                    p["num"]: st.session_state.get(f"{kp}_q{p['num']}")
                    for p in t["problems"]
                }
                st.session_state[f"{kp}_saved"]     = saved
                st.session_state[f"{kp}_submitted"] = True
                st.rerun()
        with c2:
            if st.button("\U0001f504  Reset"):
                _reset(kp, t)
    else:
        saved   = st.session_state[f"{kp}_saved"]
        probs   = t["problems"]
        correct = sum(1 for p in probs if saved.get(p["num"]) == p["answer"])
        wrong   = sum(1 for p in probs if saved.get(p["num"]) and saved.get(p["num"]) != p["answer"])
        blank   = len(probs) - correct - wrong
        _score_banner(correct, len(probs))
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Correct",    correct)
        c2.metric("❌ Wrong",       wrong)
        c3.metric("⬜ Unanswered",  blank)
        if st.button("\U0001f504  Retake Test"):
            _reset(kp, t)


# ── Entry point ───────────────────────────────────────────────────────────────

def render_practice_tests():
    st.markdown("## \U0001f4dd AMC Practice Tests")
    sel = st.selectbox("Select test:", list(TESTS.keys()), label_visibility="collapsed")
    st.divider()
    _render_test(TESTS[sel])

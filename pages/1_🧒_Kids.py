"""Kids section — Son (Grade 6/7/8) and Daughter."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime as _dt

st.set_page_config(page_title="AiPi360 · Kids", page_icon="🧒", layout="wide")

from backend.auth import require_auth, sign_out
require_auth()

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

    g6, g7, g8, tamil_tab, classes_tab = st.tabs(["📘 Grade 6", "📗 Grade 7", "📙 Grade 8", "🕉️ Tamil School", "📋 Classes & Fees"])

    # ── Grade 6 ───────────────────────────────────────────────────────────────
    with g6:
        st.markdown("### 📘 Grade 6 — FISD")
        sub1, sub2, sub3, sub4 = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🔢 Math Rocks", "🌟 Planning Ahead"])

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

            # ── Two sections: Calendar + Curriculum ───────────────────────────
            cal_section, curr_section = st.tabs(["📅 School Calendar", "📚 TEKS Curriculum"])

            with curr_section:
                from services.g6_teks import (
                    MONTHLY_PACING, SUBJECT_STYLE, STAAR_INFO, TEA_CODES
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

                    # Show 4 subject cards side by side (2x2 grid)
                    st.markdown(f"##### {sel_month.replace(chr(10), ' — ')}")
                    col_a, col_b = st.columns(2)
                    for idx, subj in enumerate(subjects):
                        col = col_a if idx % 2 == 0 else col_b
                        style = SUBJECT_STYLE[subj]
                        # Find topics for this month
                        topics = next(
                            (t for m, t in MONTHLY_PACING[subj] if m == sel_month), []
                        )
                        topic_html = "".join(
                            f"""<div style="padding:4px 0;border-bottom:1px solid #f1f5f9;
                                font-size:12.5px;color:{'#b45309' if t.startswith(('★','⚠️')) else '#1e293b'};">
                              {'⚠️' if t.startswith('⚠️') else ('★' if t.startswith('★') else '•')}
                              {t.lstrip('⚠️★ ')}
                            </div>"""
                            for t in topics
                        )
                        col.markdown(
                            f"""<div style="background:{style['bg']};border:1px solid {style['border']};
                                border-radius:12px;padding:14px;margin-bottom:12px;">
                              <div style="font-size:13px;font-weight:700;color:{style['border']};
                                   margin-bottom:8px;">{style['icon']} {subj}</div>
                              <div style="font-size:10px;color:{style['tag_color']};
                                   background:{style['tag_bg']};border-radius:6px;
                                   padding:2px 8px;display:inline-block;margin-bottom:8px;">
                                {TEA_CODES[subj]}
                              </div>
                              {topic_html}
                            </div>""",
                            unsafe_allow_html=True,
                        )

                else:  # By Subject
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
                                with st.expander(hdr, expanded=False):
                                    for t in topics:
                                        if t.startswith("★"):
                                            st.markdown(
                                                f'<div style="background:#fef9c3;border-left:3px solid #ca8a04;'
                                                f'border-radius:6px;padding:6px 10px;margin:3px 0;'
                                                f'font-size:13px;font-weight:600;">⭐ {t.lstrip("★ ")}</div>',
                                                unsafe_allow_html=True,
                                            )
                                        elif t.startswith("⚠️"):
                                            st.markdown(
                                                f'<div style="background:#fff7ed;border-left:3px solid #ea580c;'
                                                f'border-radius:6px;padding:5px 10px;margin:3px 0;'
                                                f'font-size:12px;color:#9a3412;">{t}</div>',
                                                unsafe_allow_html=True,
                                            )
                                        else:
                                            st.markdown(f"• {t}")

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
                        r_title = st.text_input("Event / Reminder")
                        r_date  = st.date_input("Reminder Date", value=date.today())
                        r_msg   = st.text_area("Details", height=60)
                        if st.form_submit_button("➕ Add Reminder", type="primary"):
                            from services.reminders import add as add_rem
                            add_rem("fisd", r_title, r_msg, r_date)
                            st.success("Reminder added!")
                            st.rerun()

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

    # ── Grade 8 ───────────────────────────────────────────────────────────────
    with g8:
        st.markdown("### 📙 Grade 8 — High School Bound")
        st.markdown('<div class="grade-badge">Future · Grade 8</div>', unsafe_allow_html=True)
        g8a, g8b, g8c = st.tabs(["📅 Syllabus & Plan", "🎯 STAAR Prep", "🚀 HS & Beyond"])

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

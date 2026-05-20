"""Account Tracker — balances, analytics, projections & market alerts."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as _components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import base64, json, re

st.set_page_config(page_title="AiPi360 · Account Tracker", page_icon="📊", layout="wide")

from backend.auth import require_auth, sign_out
from backend.page_manager import check_maintenance, check_page_access
require_auth()
check_maintenance()
check_page_access("accounts")

from components.reminder_banner import render_section_reminders
from services.accounts import (
    list_accounts, add_account, deactivate_account,
    save_balances, load_balances, latest_balances,
    list_alerts, add_alert, delete_alert,
    list_brokers, add_broker, toggle_broker, seed_brokers,
    save_manual_entry, list_manual_entries, latest_manual_balances,
    icon as acc_icon, label as acc_label, is_retirement, auto_tax_status,
    ACCOUNT_TYPES, RETIREMENT_ACCOUNT_TYPES, IRS_LIMITS, TAX_STATUS_LABELS,
    DEFAULT_SELF_DOB, DEFAULT_SPOUSE_DOB, PROJECTION_END_YEAR,
    monthly_totals, yearend_totals, project_retirement,
)
from backend.gsheet import read_sheet, refresh_cache

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; font-size: 14px !important;
    border-radius: 10px 10px 0 0 !important;
    border: 1px solid #e2e8f0 !important; border-bottom: none !important;
    background: #f8fafc !important; padding: 10px 22px !important;
    margin-right: 4px !important; transition: all 0.15s ease !important;
}
button[data-baseweb="tab"]:hover { background: #f1f5f9 !important; }
button[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(16,185,129,0.10) !important;
    border-color: rgba(16,185,129,0.45) !important;
    color: #059669 !important; font-weight: 700 !important;
}
.section-ret {
    font-size: 13px; font-weight: 700; color: #059669;
    background: rgba(16,185,129,0.07); border-left: 3px solid #10b981;
    border-radius: 0 6px 6px 0; padding: 5px 14px; margin: 6px 0 10px 0;
}
.section-nonret {
    font-size: 13px; font-weight: 700; color: #2563eb;
    background: rgba(37,99,235,0.07); border-left: 3px solid #3b82f6;
    border-radius: 0 6px 6px 0; padding: 5px 14px; margin: 6px 0 10px 0;
}
.section-self   { font-size: 13px; font-weight: 600; color: #059669; border-bottom: 1px solid rgba(16,185,129,0.2); padding-bottom: 4px; margin: 8px 0 6px 0; }
.section-spouse { font-size: 13px; font-weight: 600; color: #d97706; border-bottom: 1px solid rgba(217,119,6,0.2);  padding-bottom: 4px; margin: 8px 0 6px 0; }
.section-joint  { font-size: 13px; font-weight: 600; color: #2563eb; border-bottom: 1px solid rgba(37,99,235,0.2);   padding-bottom: 4px; margin: 8px 0 6px 0; }
.acct-name { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 2px; }
.acct-type { font-size: 11px; font-weight: 400; color: #64748b; margin-left: 4px; }
.acct-last { font-size: 11px; color: #64748b; margin-top: 3px; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# JS: select-all on focus so typing replaces 0 instead of appending
_components.html("""
<script>
(function(){
  var doc=window.parent.document;
  function attach(){
    doc.querySelectorAll('input[type="number"]').forEach(function(el){
      if(!el._sol){el._sol=true;el.addEventListener('focus',function(){this.select();});}
    });
  }
  attach();
  new MutationObserver(attach).observe(doc.body,{childList:true,subtree:true});
})();
</script>""", height=0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _fc(v, d=0):
    """Format as currency string."""
    if v is None: return "—"
    return f"${abs(v):,.{d}f}"

_VIEW_KEY = "acct_tracker_view"
_VIEW_RET = "retirement"
_VIEW_NON = "non_retirement"
_VIEW_ALL = "all"

_ATYPE_COLOR = {
    "roth_ira":"#06b6d4","traditional_ira":"#8b5cf6","401k":"#3b82f6",
    "roth_401k":"#60a5fa","hsa":"#f97316","sep_ira":"#ec4899","solo_401k":"#a78bfa",
    "brokerage":"#10b981","crypto":"#f59e0b","savings":"#34d399",
    "checking":"#fbbf24","treasury":"#6ee7b7","cd":"#a3e635",
    "real_estate":"#fb923c","fsa":"#e879f9","auto":"#94a3b8","mortgage":"#f87171",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("**People**")
    self_name   = st.text_input("Person 1 (Self)",   value="Self")
    spouse_name = st.text_input("Person 2 (Spouse)", value="Spouse")
    self_dob    = st.date_input("Person 1 DOB",   value=DEFAULT_SELF_DOB,   min_value=date(1940,1,1))
    spouse_dob  = st.date_input("Person 2 DOB",   value=DEFAULT_SPOUSE_DOB, min_value=date(1940,1,1))
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_cache()
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True): sign_out()
    st.page_link("app.py", label="🏠 Home", use_container_width=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="font-size:26px;font-weight:800;color:#1e293b;letter-spacing:-0.03em;">'
    '📊 Account Tracker</div>'
    '<div style="font-size:12px;color:#64748b;margin-top:2px;">'
    'Track, compare and project all your accounts through 2040</div>',
    unsafe_allow_html=True,
)

try:
    rem_df = read_sheet("reminders")
    render_section_reminders(rem_df, "accounts")
except Exception:
    pass

# ── View toggle ───────────────────────────────────────────────────────────────
st.markdown("<div style='margin:10px 0 4px 0'></div>", unsafe_allow_html=True)
cur_view = st.session_state.get(_VIEW_KEY, _VIEW_RET)
tog_l, tog_m, tog_r, tog_gap = st.columns([1.5, 1.9, 1.6, 4])
with tog_l:
    if st.button("🎯 Retirement",
                 type="primary" if cur_view == _VIEW_RET else "secondary",
                 use_container_width=True):
        st.session_state[_VIEW_KEY] = _VIEW_RET; st.rerun()
with tog_m:
    if st.button("💼 Non-Retirement",
                 type="primary" if cur_view == _VIEW_NON else "secondary",
                 use_container_width=True):
        st.session_state[_VIEW_KEY] = _VIEW_NON; st.rerun()
with tog_r:
    if st.button("📊 All Accounts",
                 type="primary" if cur_view == _VIEW_ALL else "secondary",
                 use_container_width=True):
        st.session_state[_VIEW_KEY] = _VIEW_ALL; st.rerun()
st.divider()

# ── Load & filter accounts ────────────────────────────────────────────────────
current_year = datetime.now().year

@st.cache_data(ttl=300)
def _accounts():   return list_accounts()
@st.cache_data(ttl=300)
def _balances():   return load_balances()

try:
    accounts_df = _accounts()
except Exception as e:
    st.error(f"Could not load accounts: {e}"); st.stop()

all_accts = accounts_df.to_dict("records") if not accounts_df.empty else []

def _is_ret(a): return is_retirement(a.get("account_type",""))

ret_accts_all = [a for a in all_accts if _is_ret(a)]
nonret_accts  = [a for a in all_accts if not _is_ret(a)]

view = st.session_state.get(_VIEW_KEY, _VIEW_RET)
if view == _VIEW_RET:   display_accts = ret_accts_all
elif view == _VIEW_NON: display_accts = nonret_accts
else:                   display_accts = all_accts

_no_accts_msg = ""
if not display_accts:
    kind = "retirement" if view == _VIEW_RET else ("non-retirement" if view == _VIEW_NON else "")
    _no_accts_msg = f"No active {kind} accounts. Use the **⚙️ Setup** tab to add some."

def _split_by_owner(accts):
    s = sorted([a for a in accts if a.get("owner")=="self"],   key=lambda a: a.get("account_type",""))
    p = sorted([a for a in accts if a.get("owner")=="spouse"], key=lambda a: a.get("account_type",""))
    j =        [a for a in accts if a.get("owner")=="joint"]
    return s, p, j

# SECURE 2.0 warning (2026+)
if display_accts and view in (_VIEW_RET, _VIEW_ALL) and current_year >= 2026:
    s_ret, sp_ret, _ = _split_by_owner(ret_accts_all)
    missing = []
    if not any(a.get("account_type")=="roth_401k" for a in s_ret):
        missing.append(f"{self_name} Roth 401(k)")
    if not any(a.get("account_type")=="roth_401k" for a in sp_ret) and current_year >= 2029:
        missing.append(f"{spouse_name} Roth 401(k)")
    if missing:
        with st.expander("⚠️ SECURE 2.0: Add Roth 401(k) for catch-up tracking", expanded=False):
            st.warning("From 2026, 401(k) catch-up must go to a Roth 401(k). Add: " + ", ".join(missing))

# ── Shared data for Analytics + Projections ───────────────────────────────────
bal_history  = _balances()
latest       = latest_balances(bal_history)

disp_ids     = {a["account_id"] for a in display_accts}
ret_ids      = {a["account_id"] for a in ret_accts_all}
nonret_ids   = {a["account_id"] for a in nonret_accts}
_excluded    = st.session_state.get("ret_excluded", set())

hist_filt    = bal_history[bal_history["account_id"].isin(disp_ids)] if not bal_history.empty else bal_history

def _sum(ids): return sum(v for k,v in latest.items() if k in ids and k not in _excluded)
_total_now   = _sum(disp_ids) if display_accts else 0.0
_ret_now     = _sum(ret_ids)  if display_accts else 0.0
_nonret_now  = _sum(nonret_ids) if display_accts else 0.0
_self_now    = (sum(v for k,v in latest.items() if k not in _excluded and k in disp_ids
                   and any(a["account_id"]==k and a.get("owner")=="self" for a in display_accts))
                if display_accts else 0.0)
_spouse_now  = (sum(v for k,v in latest.items() if k not in _excluded and k in disp_ids
                   and any(a["account_id"]==k and a.get("owner")=="spouse" for a in display_accts))
                if display_accts else 0.0)

# ── Tabs ──────────────────────────────────────────────────────────────────────
if _no_accts_msg:
    st.warning(_no_accts_msg)

tab_bal, tab_analytics, tab_proj, tab_alerts, tab_mgmt = st.tabs([
    "📥 Balance Input", "📊 Analytics", "🔮 Projections", "🔔 Market Alerts", "⚙️ Setup"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Balance Input
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bal:
    d_col, upload_col = st.columns([2, 5])
    with d_col:
        snap_date = st.date_input("📅 Snapshot Date", value=date.today())
    with upload_col:
        uploaded = st.file_uploader(
            "📎 Upload statement / screenshot to auto-fill balances",
            type=["png","jpg","jpeg"], label_visibility="collapsed",
            help="Upload a PNG/JPG screenshot. Claude reads balances and pre-fills — verify before saving.",
        )
        if uploaded and display_accts:
            ext = uploaded.name.rsplit(".",1)[-1].lower()
            media_type = "image/jpeg" if ext in ("jpg","jpeg") else "image/png"
            with st.spinner("🔍 Reading balances with Claude AI…"):
                try:
                    import anthropic as _anth
                    api_key = st.secrets.get("ANTHROPIC_API_KEY","") or os.getenv("ANTHROPIC_API_KEY","")
                    if not api_key: raise RuntimeError("ANTHROPIC_API_KEY not set in secrets.")
                    client = _anth.Anthropic(api_key=api_key)
                    acct_list = "\n".join(
                        f'- id:"{a["account_id"]}"  name:"{a["account_name"]}"  type:"{acc_label(a.get("account_type",""))}"  owner:"{a.get("owner","")}"'
                        for a in display_accts
                    )
                    prompt = f"""Extract financial account balances from this statement/screenshot.

Known accounts:
{acct_list}

Return ONLY valid JSON: account_id → balance (plain number, no $ or commas).
Example: {{"abc123": 125000.50}}
Only include accounts where you can clearly identify a corresponding balance.
If nothing matches, return {{}}"""
                    resp = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=512,
                        messages=[{"role":"user","content":[
                            {"type":"image","source":{"type":"base64","media_type":media_type,
                             "data":base64.standard_b64encode(uploaded.read()).decode()}},
                            {"type":"text","text":prompt},
                        ]}],
                    )
                    raw = resp.content[0].text.strip()
                    m = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
                    if m:
                        extracted = {k: float(v) for k,v in json.loads(m.group()).items()}
                        for aid, amt in extracted.items():
                            st.session_state[f"bal_{aid}"] = float(amt)
                        st.session_state["_img_extracted"] = set(extracted.keys())
                        st.success(f"✅ Found {len(extracted)} balance(s) — verify below and save.")
                    else:
                        st.warning("Couldn't match balances — enter manually.")
                except Exception as exc:
                    st.error(f"Extraction failed: {exc}")

    skip_set     = set(st.session_state.get("ret_excluded", set()))
    _img_ids     = st.session_state.get("_img_extracted", set())
    bal_inputs: dict[str, float] = {}

    def _acct_card(acc, col_ctx):
        if acc is None:
            with col_ctx: st.markdown("<div style='height:130px'></div>", unsafe_allow_html=True)
            return
        aid      = acc["account_id"]
        atype    = acc.get("account_type","")
        last     = float(latest.get(aid, 0) or 0)
        from_img = aid in _img_ids
        with col_ctx:
            with st.container(border=True):
                badge = ' <span style="font-size:10px;color:#059669;font-weight:500">📷 from image</span>' if from_img else ""
                st.markdown(
                    f'<div class="acct-name">{acc_icon(atype)} {acc["account_name"]}'
                    f'<span class="acct-type">· {acc_label(atype)}</span>{badge}</div>',
                    unsafe_allow_html=True,
                )
                bal = st.number_input("Balance", min_value=0.0, value=0.0, step=500.0,
                                      format="%.2f", key=f"bal_{aid}", label_visibility="collapsed")
                st.markdown(
                    f'<div class="acct-last">Last: {_fc(last) if last else "—"}'
                    f' &nbsp;<code style="font-size:9px;color:#94a3b8">{aid}</code></div>',
                    unsafe_allow_html=True,
                )
                skipped = st.checkbox("Hide from forecast", key=f"skip_{aid}",
                                      value=aid in skip_set,
                                      help="Removes account from projections. History is NOT deleted.")
        bal_inputs[aid] = bal
        if skipped: skip_set.add(aid)
        else:       skip_set.discard(aid)

    def _padded(lst, n):
        r = len(lst) % n
        return lst + ([None] * ((n - r) % n))

    def _render_owner_grid(accts):
        s_list, p_list, j_list = _split_by_owner(accts)
        c_self, c_sep, c_spouse = st.columns([1, 0.03, 1], gap="small")
        with c_sep:
            st.markdown("""
            <div style="display:flex;justify-content:center;height:100%;padding-top:10px;">
              <div style="width:2px;min-height:300px;
                background:linear-gradient(to bottom,transparent 0%,rgba(16,185,129,.5) 18%,
                rgba(139,92,246,.65) 50%,rgba(245,158,11,.5) 82%,transparent 100%);
                border-radius:2px;"></div>
            </div>""", unsafe_allow_html=True)
        with c_self:
            st.markdown(f'<div class="section-self">👤 {self_name}</div>', unsafe_allow_html=True)
            if s_list:
                for i in range(0, len(_padded(s_list,2)), 2):
                    p = _padded(s_list,2); sl,sr = st.columns(2, gap="medium")
                    _acct_card(p[i], sl); _acct_card(p[i+1], sr)
            else:
                st.caption("No accounts.")
        with c_spouse:
            st.markdown(f'<div class="section-spouse">👥 {spouse_name}</div>', unsafe_allow_html=True)
            if p_list:
                for i in range(0, len(_padded(p_list,2)), 2):
                    p = _padded(p_list,2); sl,sr = st.columns(2, gap="medium")
                    _acct_card(p[i], sl); _acct_card(p[i+1], sr)
            else:
                st.caption("No accounts.")
        if j_list:
            st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-joint">🤝 Joint</div>', unsafe_allow_html=True)
            for i in range(0, len(_padded(j_list,3)), 3):
                p = _padded(j_list,3); jc1,jc2,jc3 = st.columns(3, gap="medium")
                _acct_card(p[i], jc1); _acct_card(p[i+1], jc2); _acct_card(p[i+2], jc3)

    if view == _VIEW_ALL:
        if ret_accts_all:
            st.markdown('<div class="section-ret">🎯 Retirement Accounts <span style="font-size:11px;color:#6ee7b7;font-weight:400">· Tax-advantaged</span></div>', unsafe_allow_html=True)
            _render_owner_grid(ret_accts_all)
        if nonret_accts:
            st.markdown("<hr style='margin:20px 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
            st.markdown('<div class="section-nonret">💼 Non-Retirement Accounts <span style="font-size:11px;color:#93c5fd;font-weight:400">· Taxable &amp; other</span></div>', unsafe_allow_html=True)
            _render_owner_grid(nonret_accts)
    elif view == _VIEW_NON:
        st.markdown('<div class="section-nonret">💼 Non-Retirement Accounts</div>', unsafe_allow_html=True)
        _render_owner_grid(display_accts)
    else:
        _render_owner_grid(display_accts)

    st.session_state["ret_excluded"] = skip_set

    st.markdown("---")
    sv_col, _ = st.columns([2, 5])
    with sv_col:
        if st.button("💾 Save All Balances", type="primary", use_container_width=True):
            name_map = {a["account_id"]: a["account_name"] for a in all_accts}
            entries  = [{"account_id": aid, "account_name": name_map.get(aid, aid), "balance": bal}
                        for aid, bal in bal_inputs.items() if bal > 0]
            if entries:
                try:
                    save_balances(entries, snap_date)
                    st.success(f"✅ Saved {len(entries)} balance(s) for {snap_date}.")
                    for aid in bal_inputs: st.session_state.pop(f"bal_{aid}", None)
                    st.session_state.pop("_img_extracted", None)
                    refresh_cache(); _accounts.clear(); _balances.clear(); st.rerun()
                except Exception as exc:
                    st.error(f"Save failed: {exc}")
            else:
                st.warning("Enter at least one balance > $0 before saving.")

    if view in (_VIEW_RET, _VIEW_ALL):
        with st.expander("📋 IRS Contribution Limits Reference (2024–2040)", expanded=False):
            rows = [{"Year": yr,
                     "401k Regular": lim["irs_401k"], "401k Catch-up (50+)": lim["irs_401k_cu"],
                     "IRA": lim["ira"], "IRA Catch-up (50+)": lim["ira_cu"],
                     "HSA (Self)": lim["hsa_self"], "HSA (Family)": lim["hsa_fam"],
                     "Status": "✅ Confirmed" if lim["confirmed"] else "📊 Estimated"}
                    for yr, lim in sorted(IRS_LIMITS.items())]
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                         column_config={k: st.column_config.NumberColumn(format="$%d")
                                        for k in ["401k Regular","401k Catch-up (50+)","IRA",
                                                  "IRA Catch-up (50+)","HSA (Self)","HSA (Family)"]})


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Analytics
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    if bal_history.empty or not display_accts:
        st.info("No balance data yet — use the **Balance Input** tab to record your first snapshot.")
    else:
        # KPIs
        k1, k2, k3 = st.columns(3)
        if view == _VIEW_ALL:
            k1.metric("💰 Total Balance",    _fc(_total_now))
            k2.metric("🎯 Retirement",       _fc(_ret_now))
            k3.metric("💼 Non-Retirement",   _fc(_nonret_now))
        else:
            k1.metric("Combined Balance",    _fc(_total_now))
            k2.metric(f"👤 {self_name}",     _fc(_self_now))
            k3.metric(f"👥 {spouse_name}",   _fc(_spouse_now))

        # Data diagnostics
        hist_ids      = set(bal_history["account_id"].astype(str).str.strip())
        unmatched_ids = hist_ids - disp_ids
        missing_ids   = disp_ids - hist_ids
        diag_label = (
            "🔍 Data Diagnostics"
            + (f" — ⚠️ {len(unmatched_ids)} unrecognised ID(s)" if unmatched_ids else "")
            + (f" — ⚠️ {len(missing_ids)} account(s) with no history" if missing_ids else "")
        )
        with st.expander(diag_label, expanded=False):
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.markdown("**Expected accounts (current view)**")
                for a in display_accts:
                    aid = a["account_id"]
                    bal = latest.get(aid)
                    if aid in hist_ids and bal:
                        tag = f"✅ {_fc(float(bal or 0))}"
                    elif aid in hist_ids:
                        tag = "⚠️ found but balance = $0"
                    else:
                        tag = "❌ no history — save a balance in Tab 1"
                    st.markdown(
                        f"<div style='font-size:12px;margin-bottom:4px'>"
                        f"<code style='font-size:11px'>{aid}</code><br>"
                        f"<span style='color:#64748b'>{a['account_name']}</span> · {tag}</div>",
                        unsafe_allow_html=True,
                    )
            with dcol2:
                if unmatched_ids:
                    st.markdown("**⚠️ Balance history found for unknown account IDs**")
                    st.caption(
                        "These account_ids exist in the balance sheet but don't match any account "
                        "in the **current view**. If it's a non-retirement account, switch to "
                        "**All Accounts** view to see it. If it was deleted, the history remains "
                        "but the account is no longer tracked."
                    )
                    for uid in sorted(unmatched_ids):
                        row = bal_history[bal_history["account_id"].astype(str).str.strip()==uid]
                        name = row["account_name"].iloc[0] if not row.empty else "?"
                        bal  = row["balance"].iloc[-1] if not row.empty else 0
                        st.markdown(
                            f"<div style='font-size:12px;margin-bottom:4px;color:#ef4444'>"
                            f"<code style='font-size:11px'>{uid}</code><br>"
                            f"<span style='color:#64748b'>{name} · {_fc(float(bal))}</span></div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("✅ All history records match accounts in the current view.")

        st.divider()

        # ── 1. Year-End Balances Pivot ────────────────────────────────────────
        st.subheader("🏦 Year-End Balances at Account Level")
        hf = hist_filt[hist_filt["balance"] > 0] if not hist_filt.empty else hist_filt
        if hf.empty:
            st.info("No non-zero balance data yet.")
        else:
            pv = hf.copy()
            pv["year"] = pv["date"].dt.year
            pv_last = pv.sort_values("date").groupby(["year","account_id"])["balance"].last().reset_index()
            name_map = {a["account_id"]: a["account_name"] for a in display_accts}
            pv_last["account_name"] = pv_last["account_id"].map(name_map).fillna(pv_last["account_id"])
            pivot = pv_last.pivot_table(index="account_name", columns="year", values="balance", aggfunc="last")
            years = sorted(pivot.columns, reverse=True)
            rows_pv = []
            for acct in pivot.index:
                row = {"Account": acct}
                for i, yr in enumerate(years):
                    bal  = pivot.loc[acct, yr] if not pd.isna(pivot.loc[acct, yr]) else None
                    row[f"{yr} Balance"] = bal
                    prev = years[i+1] if i+1 < len(years) else None
                    if prev is not None:
                        pb = pivot.loc[acct, prev] if not pd.isna(pivot.loc[acct, prev]) else None
                        if bal is not None and pb is not None and pb != 0:
                            row[f"{yr} YoY $"] = bal - pb
                            row[f"{yr} YoY %"] = (bal - pb) / pb * 100
                        else:
                            row[f"{yr} YoY $"] = row[f"{yr} YoY %"] = None
                    else:
                        row[f"{yr} YoY $"] = row[f"{yr} YoY %"] = None
                rows_pv.append(row)
            wide_df = pd.DataFrame(rows_pv)

            # Total row — two passes: sum balances first, then compute YoY from totals
            total_row: dict = {"Account": "📊 Total"}
            for yr in years:
                bal_col = f"{yr} Balance"
                total_row[bal_col] = wide_df[bal_col].sum(skipna=True) if bal_col in wide_df.columns else None
            for i, yr in enumerate(years):
                prev = years[i+1] if i+1 < len(years) else None
                if prev is not None:
                    tb = total_row.get(f"{yr} Balance")
                    pb = total_row.get(f"{prev} Balance")
                    if tb is not None and pb is not None and pb != 0:
                        total_row[f"{yr} YoY $"] = tb - pb
                        total_row[f"{yr} YoY %"] = (tb - pb) / pb * 100
                    else:
                        total_row[f"{yr} YoY $"] = total_row[f"{yr} YoY %"] = None
                else:
                    total_row[f"{yr} YoY $"] = total_row[f"{yr} YoY %"] = None
            wide_df = pd.concat([wide_df, pd.DataFrame([total_row])], ignore_index=True)

            col_cfg = {}
            for i, yr in enumerate(years):
                prev = years[i+1] if i+1 < len(years) else None
                vs_label = f" vs {prev}" if prev else ""
                col_cfg[f"{yr} Balance"] = st.column_config.NumberColumn(f"{yr} Balance",       format="$%,.0f",  width="medium")
                col_cfg[f"{yr} YoY $"]   = st.column_config.NumberColumn(f"{yr}{vs_label} ($)", format="$%+,.0f", width="medium")
                col_cfg[f"{yr} YoY %"]   = st.column_config.NumberColumn(f"{yr}{vs_label} (%)", format="%+.1f%%", width="small")
            st.caption("Most recent year first · Scroll right for older years · YoY vs prior year-end")
            st.dataframe(wide_df, use_container_width=True, hide_index=True,
                         height=min(500, 60+38*max(len(wide_df),1)), column_config=col_cfg)

        st.divider()

        # ── 2. Monthly Trend ──────────────────────────────────────────────────
        st.subheader("📅 Monthly Trend — Last 8 Months")
        df_mo = monthly_totals(hist_filt) if not hist_filt.empty else pd.DataFrame()
        if df_mo.empty:
            st.info("Not enough history for monthly trend yet.")
        else:
            mo_c, mo_t = st.columns([1.6, 1])
            with mo_c:
                fig_mo = go.Figure(go.Bar(
                    x=df_mo["month_str"], y=df_mo["total"], marker_color="#3b82f6",
                    text=df_mo["total"].apply(lambda v: f"${v/1e6:.2f}M" if v>=1e6 else f"${v:,.0f}"),
                    textposition="outside",
                    hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
                ))
                fig_mo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                                     height=260, margin=dict(l=0,r=0,t=10,b=0),
                                     xaxis=dict(showgrid=False),
                                     yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
                st.plotly_chart(fig_mo, use_container_width=True)
            with mo_t:
                df_mo_s = df_mo[["month_str","total","mom_change"]].copy().iloc[::-1].reset_index(drop=True)
                df_mo_s.columns = ["Month","Balance","MoM Change"]
                st.dataframe(df_mo_s, use_container_width=True, hide_index=True, height=260,
                             column_config={"Balance": st.column_config.NumberColumn(format="$%,.0f"),
                                            "MoM Change": st.column_config.NumberColumn(format="$%+,.0f")})

        st.divider()

        # ── 3. Year-End Historical ────────────────────────────────────────────
        st.subheader("📆 Year-End Balances (Historical)")
        df_ye = yearend_totals(hist_filt) if not hist_filt.empty else pd.DataFrame()
        if df_ye.empty:
            st.info("Not enough history for year-end summary yet.")
        else:
            ye_c, ye_t = st.columns([1.6, 1])
            with ye_c:
                bar_colors = ["#3b82f6" if i==0 or pd.isna(r["yoy_change"])
                               else ("#10b981" if r["yoy_change"]>=0 else "#ef4444")
                               for i,r in df_ye.iterrows()]
                fig_ye = go.Figure(go.Bar(
                    x=df_ye["year"].astype(str), y=df_ye["total"], marker_color=bar_colors,
                    text=df_ye["total"].apply(lambda v: f"${v/1e6:.2f}M" if v>=1e6 else f"${v:,.0f}"),
                    textposition="outside",
                    hovertemplate="Year %{x}<br>$%{y:,.0f}<extra></extra>",
                ))
                fig_ye.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                                     height=260, margin=dict(l=0,r=0,t=10,b=0),
                                     xaxis=dict(showgrid=False),
                                     yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
                st.plotly_chart(fig_ye, use_container_width=True)
            with ye_t:
                df_ye_s = df_ye[["year","total","yoy_change","yoy_pct"]].copy().iloc[::-1].reset_index(drop=True)
                df_ye_s.columns = ["Year","Balance","YoY $","YoY %"]
                st.dataframe(df_ye_s, use_container_width=True, hide_index=True, height=260,
                             column_config={"Balance": st.column_config.NumberColumn(format="$%,.0f"),
                                            "YoY $":   st.column_config.NumberColumn(format="$%+,.0f"),
                                            "YoY %":   st.column_config.NumberColumn(format="%+.1f%%")})

        st.divider()

        # ── 4. Self vs Spouse grouped bar ────────────────────────────────────
        st.subheader(f"👤 {self_name} vs 👥 {spouse_name}")
        cmp_rows = [
            {"Account": a["account_name"],
             "Person": self_name if a.get("owner")=="self" else (spouse_name if a.get("owner")=="spouse" else "Joint"),
             "Balance": latest.get(a["account_id"], 0)}
            for a in display_accts if a["account_id"] not in _excluded
        ]
        if cmp_rows:
            df_cmp = pd.DataFrame(cmp_rows)
            fig_cmp = px.bar(df_cmp, x="Account", y="Balance", color="Person", barmode="group",
                             color_discrete_map={self_name:"#10b981", spouse_name:"#f59e0b", "Joint":"#3b82f6"},
                             text="Balance")
            fig_cmp.update_traces(texttemplate="$%{text:,.0f}", textposition="outside",
                                  hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>")
            fig_cmp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                                  height=300, margin=dict(l=0,r=0,t=8,b=0),
                                  xaxis=dict(showgrid=False),
                                  yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
            st.plotly_chart(fig_cmp, use_container_width=True)

        st.divider()

        # ── 5. Balance Over Time ──────────────────────────────────────────────
        st.subheader("📈 Balance Over Time")
        if not bal_history.empty:
            df_h = bal_history[bal_history["account_id"].isin(disp_ids)].copy()
            fig_h = go.Figure()
            for acc in display_accts:
                aid  = acc["account_id"]
                df_a = df_h[df_h["account_id"]==aid].sort_values("date")
                if df_a.empty: continue
                fig_h.add_trace(go.Scatter(
                    x=df_a["date"], y=df_a["balance"], name=acc["account_name"],
                    mode="lines+markers", opacity=0.75,
                    line=dict(width=1.5, color=_ATYPE_COLOR.get(acc.get("account_type",""), "#94a3b8")),
                    hovertemplate=f"{acc['account_name']}<br>%{{x|%b %Y}}: $%{{y:,.0f}}<extra></extra>",
                ))
            df_comb = df_h.groupby("date")["balance"].sum().reset_index().sort_values("date")
            fig_h.add_trace(go.Scatter(
                x=df_comb["date"], y=df_comb["balance"], name="Combined",
                mode="lines+markers", line=dict(width=3, color="#3b82f6"),
                hovertemplate="Combined %{x|%b %Y}: $%{y:,.0f}<extra></extra>",
            ))
            fig_h.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                height=340, margin=dict(l=0,r=0,t=8,b=0),
                legend=dict(orientation="h", y=-0.25, font_size=11),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"),
                hovermode="x unified",
            )
            st.plotly_chart(fig_h, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Projections
# ═══════════════════════════════════════════════════════════════════════════════
with tab_proj:
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([3, 2, 2, 3])
    with ctrl1:
        growth_pct  = st.slider("📈 Annual Growth Rate", 3.0, 15.0, 7.0, 0.5, format="%.1f%%")
    with ctrl2:
        proj_start  = st.number_input("Start Year", min_value=2024, max_value=current_year, value=current_year)
    with ctrl3:
        target_year = st.number_input("🎯 Target Year", min_value=current_year+1,
                                      max_value=PROJECTION_END_YEAR, value=min(2040, PROJECTION_END_YEAR))
    with ctrl4:
        target_amount = st.select_slider(
            "🏁 Retirement Target",
            options=[250_000,500_000,750_000,1_000_000,1_250_000,1_500_000,
                     2_000_000,2_500_000,3_000_000,4_000_000,5_000_000],
            value=2_000_000,
            format_func=lambda v: f"${v/1e6:.2f}M" if v>=1e6 else f"${v//1000}K",
        )

    if view == _VIEW_NON:
        st.caption("ℹ️ Non-retirement accounts projected with growth only — no IRS contribution modeling.")
    else:
        st.caption("IRS limits: ✅ 2024–2025 confirmed · 📊 2026+ estimated. Year-end contributions.")

    if bal_history.empty:
        st.info("No balance data yet — use the **Balance Input** tab to save your first snapshot.")
    else:
        proj_df = project_retirement(
            display_accts, latest, growth_rate=growth_pct/100,
            excluded=_excluded, self_dob=self_dob, spouse_dob=spouse_dob,
            start_year=int(proj_start),
        )

        proj_at_ty = 0.0
        if not proj_df.empty and target_year in proj_df["year"].values:
            proj_at_ty = float(proj_df[proj_df["year"]==target_year]["balance"].sum())

        k1,k2,k3,k4,k5 = st.columns(5)
        if view == _VIEW_ALL:
            k1.metric("Total Balance",    _fc(_total_now))
            k2.metric("🎯 Retirement",    _fc(_ret_now))
            k3.metric("💼 Non-Ret",       _fc(_nonret_now))
        else:
            k1.metric("Combined Balance", _fc(_total_now))
            k2.metric(f"👤 {self_name}",  _fc(_self_now))
            k3.metric(f"👥 {spouse_name}",_fc(_spouse_now))
        gap     = target_amount - proj_at_ty
        ak_age  = target_year - self_dob.year
        pa_age  = target_year - spouse_dob.year
        k4.metric(f"Projected {target_year}", _fc(proj_at_ty),
                  delta=f"{_fc(proj_at_ty - target_amount, 0)} vs goal" if proj_at_ty else None)
        k5.metric(f"Gap to {_fc(target_amount,0)}",
                  _fc(max(gap,0),0) if gap>0 else "✅ On Track",
                  delta=f"{self_name} {ak_age} · {spouse_name} {pa_age} in {target_year}",
                  delta_color="off")

        st.divider()

        if proj_df.empty:
            st.info("No starting balances — record data in the Balance Input tab first.")
        else:
            st.subheader(f"🔮 Projection to {PROJECTION_END_YEAR}  ·  {growth_pct:.1f}% Annual Growth")
            proj_comb   = proj_df.groupby("year")["balance"].sum().reset_index()
            proj_self   = proj_df[proj_df["owner"]=="self"].groupby("year")["balance"].sum().reset_index()
            proj_spouse = proj_df[proj_df["owner"]=="spouse"].groupby("year")["balance"].sum().reset_index()

            fig_p = go.Figure()
            if view == _VIEW_ALL:
                pr = proj_df[proj_df["account_id"].isin(ret_ids)].groupby("year")["balance"].sum().reset_index()
                pn = proj_df[proj_df["account_id"].isin(nonret_ids)].groupby("year")["balance"].sum().reset_index()
                if not pr.empty:
                    fig_p.add_trace(go.Scatter(x=pr["year"], y=pr["balance"], name="🎯 Retirement",
                        fill="tozeroy", line=dict(color="#10b981",width=2), fillcolor="rgba(16,185,129,0.10)",
                        hovertemplate="Retirement %{x}: $%{y:,.0f}<extra></extra>"))
                if not pn.empty:
                    fig_p.add_trace(go.Scatter(x=pn["year"], y=pn["balance"], name="💼 Non-Retirement",
                        fill="tozeroy", line=dict(color="#3b82f6",width=2), fillcolor="rgba(59,130,246,0.10)",
                        hovertemplate="Non-Ret %{x}: $%{y:,.0f}<extra></extra>"))
            else:
                if not proj_self.empty:
                    fig_p.add_trace(go.Scatter(x=proj_self["year"], y=proj_self["balance"],
                        name=f"{self_name}", fill="tozeroy",
                        line=dict(color="#10b981",width=2), fillcolor="rgba(16,185,129,0.10)",
                        hovertemplate=f"{self_name} %{{x}}: $%{{y:,.0f}}<extra></extra>"))
                if not proj_spouse.empty:
                    fig_p.add_trace(go.Scatter(x=proj_spouse["year"], y=proj_spouse["balance"],
                        name=f"{spouse_name}", fill="tozeroy",
                        line=dict(color="#f59e0b",width=2), fillcolor="rgba(245,158,11,0.10)",
                        hovertemplate=f"{spouse_name} %{{x}}: $%{{y:,.0f}}<extra></extra>"))
            fig_p.add_trace(go.Scatter(x=proj_comb["year"], y=proj_comb["balance"], name="Combined",
                line=dict(color="#1e293b",width=3),
                hovertemplate="Combined %{x}: $%{y:,.0f}<extra></extra>"))
            fig_p.add_hline(y=target_amount, line_dash="dash", line_color="#dc2626", line_width=2,
                            annotation_text=f"🎯 {_fc(target_amount,0)}",
                            annotation_position="right", annotation_font=dict(size=11,color="#dc2626"))
            if target_year in proj_comb["year"].values:
                fig_p.add_vline(x=target_year, line_dash="dot", line_color="rgba(220,38,38,0.3)",
                                annotation_text=str(target_year), annotation_position="top",
                                annotation_font_size=11)
            max_p = proj_comb["balance"].max()
            for tgt, lbl in [(500_000,"$500K"),(1_000_000,"$1M"),(1_500_000,"$1.5M"),(2_000_000,"$2M"),(3_000_000,"$3M")]:
                if tgt != target_amount and max_p >= tgt * 0.8:
                    fig_p.add_hline(y=tgt, line_dash="dot", line_color="rgba(100,116,139,0.2)",
                                    annotation_text=lbl, annotation_position="right",
                                    annotation_font_size=10, annotation_font_color="#94a3b8")
            fig_p.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                height=420, margin=dict(l=0,r=90,t=8,b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, dtick=1, tickangle=-45),
                yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"),
                hovermode="x unified",
            )
            st.plotly_chart(fig_p, use_container_width=True)

            # Milestones
            st.subheader("🎯 Milestones")
            milestones = sorted(set([250_000,500_000,750_000,1_000_000,1_500_000,2_000_000,3_000_000,target_amount]))
            found = []
            for tgt in milestones:
                hit = proj_comb[proj_comb["balance"] >= tgt]
                lbl = f"${tgt/1e6:.2f}M" if tgt>=1e6 else f"${tgt//1000}K"
                if not hit.empty:
                    yr = int(hit.iloc[0]["year"])
                    found.append({"label":lbl,"year":yr,"ak":yr-self_dob.year,"pa":yr-spouse_dob.year,"reached":True})
                else:
                    found.append({"label":lbl,"reached":False})
            ms_cols = st.columns(min(len(found), 4))
            for i, m in enumerate(found):
                with ms_cols[i % 4]:
                    if m["reached"]:
                        st.metric(m["label"], str(m["year"]),
                                  delta=f"{self_name} {m['ak']} · {spouse_name} {m['pa']}")
                    else:
                        st.metric(m["label"], "Beyond 2040", delta="Not reached", delta_color="off")

            st.divider()

            # Annual Contributions by Account
            contrib_df = proj_df[proj_df["contribution"] > 0].copy()
            if not contrib_df.empty:
                st.subheader("💰 Annual Contributions by Account")
                fig_cont = px.bar(contrib_df, x="year", y="contribution", color="account_name",
                                  barmode="stack",
                                  labels={"contribution":"Contribution ($)","year":"Year","account_name":"Account"},
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_cont.update_traces(hovertemplate="%{fullData.name}<br>%{x}: $%{y:,.0f}<extra></extra>")
                fig_cont.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                                       height=300, margin=dict(l=0,r=0,t=8,b=0),
                                       legend=dict(orientation="h", y=-0.4, font_size=10),
                                       xaxis=dict(showgrid=False, dtick=1, tickangle=-45),
                                       yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
                st.plotly_chart(fig_cont, use_container_width=True)

            st.divider()

            # Cumulative Contributions vs Growth
            st.subheader("📊 Cumulative: Contributions vs. Growth")
            cumul = proj_df.groupby("year").agg(
                total_contrib=("contribution","sum"),
                total_growth=("growth_dollars","sum"),
            ).reset_index()
            cumul["cum_contrib"] = cumul["total_contrib"].cumsum()
            cumul["cum_growth"]  = cumul["total_growth"].cumsum()
            fig_cg = go.Figure()
            fig_cg.add_trace(go.Bar(x=cumul["year"], y=cumul["cum_contrib"],
                                    name="Cumulative Contributions", marker_color="#10b981",
                                    hovertemplate="Year %{x}<br>Contributions: $%{y:,.0f}<extra></extra>"))
            fig_cg.add_trace(go.Bar(x=cumul["year"], y=cumul["cum_growth"],
                                    name="Cumulative Growth", marker_color="#3b82f6",
                                    hovertemplate="Year %{x}<br>Growth: $%{y:,.0f}<extra></extra>"))
            fig_cg.update_layout(barmode="stack",
                                 paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f8fafc",
                                 height=300, margin=dict(l=0,r=0,t=8,b=0),
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                 xaxis=dict(showgrid=False, dtick=1, tickangle=-45),
                                 yaxis=dict(gridcolor="#e2e8f0", tickprefix="$", tickformat=",.0f"))
            st.plotly_chart(fig_cg, use_container_width=True)

            st.divider()

            # Full Projection Table
            with st.expander("📋 Full Projection Table", expanded=False):
                _confirmed = {y for y,v in IRS_LIMITS.items() if v.get("confirmed")}
                tbl = proj_comb.copy()
                tbl = tbl.merge(proj_self.rename(columns={"balance": self_name}), on="year", how="left")
                tbl = tbl.merge(proj_spouse.rename(columns={"balance": spouse_name}), on="year", how="left")
                tbl = tbl.merge(proj_df.groupby("year")["contribution"].sum().reset_index()
                                   .rename(columns={"contribution":"Contributions"}), on="year", how="left")
                tbl = tbl.merge(proj_df.groupby("year")["growth_dollars"].sum().reset_index()
                                   .rename(columns={"growth_dollars":"Growth $"}), on="year", how="left")
                if view in (_VIEW_RET, _VIEW_ALL):
                    tbl["IRS"] = tbl["year"].apply(lambda y: "✅" if y in _confirmed else "📊")
                tbl["vs Goal"] = tbl["balance"].apply(
                    lambda v: f"{'✅' if v>=target_amount else '❌'} "
                              f"{_fc(abs(v-target_amount),0)} {'ahead' if v>=target_amount else 'short'}"
                )
                tbl.rename(columns={"year":"Year","balance":"Combined"}, inplace=True)
                st.dataframe(tbl, hide_index=True, use_container_width=True,
                             column_config={
                                 "Combined":     st.column_config.NumberColumn(format="$%,.0f"),
                                 self_name:      st.column_config.NumberColumn(format="$%,.0f"),
                                 spouse_name:    st.column_config.NumberColumn(format="$%,.0f"),
                                 "Contributions":st.column_config.NumberColumn(format="$%,.0f"),
                                 "Growth $":     st.column_config.NumberColumn(format="$%,.0f"),
                             })


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Setup (Accounts, Manual Entries, Brokers)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_mgmt:
    st.markdown("#### ⚙️ Setup")
    sub_accts, sub_manual, sub_brokers = st.tabs([
        "🏦 Accounts", "📝 Manual Entries", "🏢 Brokers"
    ])

    # ── Accounts ──────────────────────────────────────────────────────────────
    with sub_accts:
        all_df = list_accounts(active_only=False)
        if not all_df.empty:
            owner_colors = {"self": "#059669", "spouse": "#d97706", "joint": "#2563eb"}
            for _, row in all_df.iterrows():
                aid       = row["account_id"]
                atype     = row.get("account_type", "")
                aowner    = row.get("owner", "")
                broker    = str(row.get("broker_name", row.get("broker", "")) or "")
                tstat     = str(row.get("tax_status", "") or "") or auto_tax_status(atype)
                is_active = str(row.get("active", "TRUE")).upper() in ("TRUE", "1", "YES")
                ts_icon, ts_label = TAX_STATUS_LABELS.get(tstat, ("🔵", tstat.replace("_", " ").title()))
                owner_color = owner_colors.get(aowner, "#64748b")
                card_bg     = "#f0fdf4" if is_active else "#f8fafc"
                card_border = "rgba(16,185,129,0.3)" if is_active else "#e2e8f0"
                badge_color = "#059669" if is_active else "#94a3b8"
                badge_text  = "🟢 Active" if is_active else "⚫ Inactive"

                c_card, c_btn = st.columns([7, 1])
                with c_card:
                    broker_part = f' &nbsp;·&nbsp; 🏢 {broker}' if broker else ''
                    st.markdown(
                        f'<div style="background:{card_bg};border:1px solid {card_border};'
                        f'border-radius:10px;padding:10px 14px;margin-bottom:6px;">'
                        f'<span style="font-size:18px">{acc_icon(atype)}</span>'
                        f'<span style="font-size:14px;font-weight:700;color:#1e293b;margin-left:8px">'
                        f'{row["account_name"]}</span>'
                        f'<span style="font-size:11px;color:#64748b;margin-left:6px">· {acc_label(atype)}</span>'
                        f'<span style="font-size:11px;font-weight:600;color:{owner_color};margin-left:10px">'
                        f'{aowner.title()}</span>'
                        f'<span style="font-size:10px;color:{badge_color};margin-left:12px;'
                        f'background:rgba(0,0,0,0.04);border-radius:6px;padding:1px 7px">{badge_text}</span>'
                        f'<br><span style="font-size:11px;color:#64748b;margin-top:3px;display:inline-block">'
                        f'{ts_icon} {ts_label}{broker_part}'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )
                with c_btn:
                    if is_active and st.button("🔴", key=f"deact_{aid}", help="Deactivate"):
                        deactivate_account(aid)
                        st.success("Deactivated.")
                        _accounts.clear(); st.rerun()
        else:
            st.info("No accounts yet. Add one below.")

        st.markdown("---")
        with st.expander("➕ Add New Account", expanded=False):
            brokers_df_add = list_brokers()
            br_opts = ["— None —"] + (brokers_df_add["broker_name"].tolist() if not brokers_df_add.empty else [])
            with st.form("add_account_form"):
                c1, c2, c3 = st.columns(3)
                with c1: aname  = st.text_input("Account Name")
                with c2: atype  = st.selectbox("Type", list(ACCOUNT_TYPES.keys()),
                                               format_func=lambda x: f"{acc_icon(x)} {acc_label(x)}")
                with c3: aowner = st.selectbox("Owner", ["self", "spouse", "joint"])
                c4, c5 = st.columns(2)
                with c4:
                    broker_sel = st.selectbox("Broker", br_opts)
                    broker_val = "" if broker_sel == "— None —" else broker_sel
                with c5:
                    ts_keys = list(TAX_STATUS_LABELS.keys())
                    tstat_sel = st.selectbox(
                        "Tax Status",
                        ts_keys,
                        index=2,
                        format_func=lambda k: f"{TAX_STATUS_LABELS[k][0]} {TAX_STATUS_LABELS[k][1]}",
                        help="Auto-set by type — adjust if needed",
                    )
                if st.form_submit_button("Add Account", type="primary"):
                    if aname:
                        aid = add_account(aname, atype, aowner, broker=broker_val, tax_stat=tstat_sel)
                        st.success(f"✅ Added: {aname} ({aid})")
                        _accounts.clear(); st.rerun()
                    else:
                        st.warning("Enter an account name.")

    # ── Manual Entries ────────────────────────────────────────────────────────
    with sub_manual:
        st.caption("Track real estate, auto, home value, liabilities, and other non-brokerage assets.")
        with st.expander("➕ Add Manual Entry", expanded=True):
            with st.form("add_manual_form"):
                mc1, mc2, mc3 = st.columns(3)
                with mc1: m_name  = st.text_input("Asset / Account Name", placeholder="e.g. Primary Home")
                with mc2: m_owner = st.selectbox("Owner", ["self", "spouse", "joint"], key="man_owner")
                with mc3: m_cat   = st.selectbox("Category",
                                                  ["Real Estate", "Auto", "Home Value", "Liability",
                                                   "Savings (External)", "Other"],
                                                  key="man_cat")
                mc4, mc5, mc6 = st.columns(3)
                with mc4: m_val   = st.number_input("Value ($)", min_value=0.0, step=1000.0,
                                                     format="%.2f", key="man_val")
                with mc5: m_date  = st.date_input("As Of Date", value=date.today(), key="man_date")
                with mc6: m_notes = st.text_input("Notes", placeholder="Optional", key="man_notes")
                if st.form_submit_button("Save Entry", type="primary"):
                    if m_name:
                        save_manual_entry(m_name, m_owner, m_cat, m_val, m_notes, m_date)
                        st.success(f"✅ Saved entry for {m_name}.")
                        st.rerun()
                    else:
                        st.warning("Enter an asset name.")

        manual_df = list_manual_entries()
        if not manual_df.empty:
            manual_df = manual_df.copy()
            manual_df["value"] = pd.to_numeric(manual_df["value"], errors="coerce")
            manual_df_disp = manual_df.sort_values("entry_date", ascending=False).reset_index(drop=True)
            st.markdown(f"**{len(manual_df_disp)} entries**")
            st.dataframe(
                manual_df_disp, use_container_width=True, hide_index=True,
                column_config={
                    "value":      st.column_config.NumberColumn("Value", format="$%,.2f"),
                    "entry_date": st.column_config.DateColumn("Date"),
                },
            )
        else:
            st.info("No manual entries yet.")

    # ── Brokers ───────────────────────────────────────────────────────────────
    with sub_brokers:
        brokers_all = list_brokers()
        if brokers_all.empty:
            st.info("No brokers yet. Seed the defaults or add your own below.")
            if st.button("🌱 Seed Default Brokers (Schwab, Fidelity, Robinhood, Vanguard, Webull, E*Trade)",
                         use_container_width=True):
                seed_brokers()
                st.success("Default brokers added.")
                st.rerun()
        else:
            st.markdown(f"**{len(brokers_all)} broker(s)**")
            for _, br in brokers_all.iterrows():
                bid     = br["broker_id"]
                is_bact = str(br.get("active", "TRUE")).upper() in ("TRUE", "1", "YES")
                bc1, bc2 = st.columns([6, 1])
                with bc1:
                    dot = "🟢" if is_bact else "⚫"
                    st.markdown(
                        f'<div style="padding:7px 12px;'
                        f'background:{"#f0fdf4" if is_bact else "#f8fafc"};'
                        f'border:1px solid {"#bbf7d0" if is_bact else "#e2e8f0"};'
                        f'border-radius:8px;margin-bottom:4px">'
                        f'{dot} <b>{br["broker_name"]}</b>'
                        f'<span style="font-size:10px;color:#94a3b8;margin-left:8px">#{bid}</span></div>',
                        unsafe_allow_html=True,
                    )
                with bc2:
                    btn_lbl  = "🔴" if is_bact else "🟢"
                    btn_help = "Deactivate" if is_bact else "Activate"
                    if st.button(btn_lbl, key=f"tog_br_{bid}", help=btn_help):
                        toggle_broker(bid); st.rerun()

        st.markdown("---")
        with st.expander("➕ Add Broker"):
            with st.form("add_broker_form"):
                br_name = st.text_input("Broker Name")
                if st.form_submit_button("Add Broker", type="primary"):
                    if br_name:
                        add_broker(br_name.strip())
                        st.success(f"✅ Added: {br_name}")
                        st.rerun()
                    else:
                        st.warning("Enter a broker name.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Market Alerts
# ═══════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown("#### 🔔 Market Alerts")
    st.info("Set alerts for market conditions. Nightly GitHub Actions job checks and notifies you.")

    alerts_df = list_alerts()
    if not alerts_df.empty:
        active_alerts = alerts_df[alerts_df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])]
        if not active_alerts.empty:
            for _, row in active_alerts.iterrows():
                c1, c2, c3 = st.columns([3,2,1])
                with c1: st.markdown(f"**{row['ticker']}** — {row['condition']} {row['threshold']}%")
                with c2: st.caption(f"Notify: {row.get('channels','push')}")
                with c3:
                    if st.button("🗑️", key=f"del_alert_{row['id']}", help="Delete"):
                        delete_alert(row["id"]); st.rerun()
        else:
            st.info("No active alerts.")
    else:
        st.info("No alerts set yet.")

    st.markdown("---")
    with st.expander("➕ Add Market Alert"):
        st.caption("Examples: SPY falls 1% in a day · QQQ falls 1% in a day · SPY falls 7% in a month")
        with st.form("add_alert_form"):
            c1,c2,c3,c4 = st.columns(4)
            with c1: ticker    = st.text_input("Ticker (e.g. SPY, QQQ)")
            with c2: condition = st.selectbox("Condition", ["falls more than","rises more than","falls more than (monthly)"])
            with c3: threshold = st.number_input("Threshold (%)", min_value=0.1, max_value=50.0, value=1.0, step=0.5)
            with c4: channels  = st.selectbox("Notify via", ["push","email","push,email"])
            if st.form_submit_button("Add Alert", type="primary"):
                if ticker:
                    add_alert(ticker.upper(), condition, threshold, channels)
                    st.success(f"✅ Alert added for {ticker.upper()}"); st.rerun()

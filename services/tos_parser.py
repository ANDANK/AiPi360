"""
ToS (Thinkorswim / Charles Schwab) account statement parser.

CSV section layout exported from ToS:
  Row 1  : Account Name, <name>
  Row 3  : Account Trade History   (section marker)
  Row 4  : (blank), Exec Time, Spread, Side, Qty, Pos Effect, Symbol, Exp, Strike, Type, Price, Net Price, Order Type
  Row 5+ : trade data rows  (col 0 always blank)
           Multi-leg (CALENDAR/DIAGONAL) continuation rows have blank cols 0-2
  ---
  Row N  : Equities                (section marker)
  Row N+1: Symbol, Qty, Trade Price, Mark, Mark Value, P/L Day, P/L Open, P/L%, Account Name, Description
  Row N+2+: equity rows
  ---
  Row M  : Options                 (section marker)
  Row M+1: Account Name, Symbol, Exp, Strike, Type, Qty, Trade Price, Mark, Mark Value, P/L Day, P/L Open, P/L%, Option Code
  Row M+2+: option rows
"""

import csv
import io
from collections import defaultdict
from datetime import date, datetime
from typing import Optional

import pandas as pd

# ─────────────────────────────── type helpers ──────────────────────────────────

def _s(v) -> str:
    return str(v).strip() if v is not None else ""


def _f(v) -> Optional[float]:
    s = _s(v).replace('"', "").replace("$", "").replace(",", "")
    if not s or s.upper() in ("N/A", "CREDIT", "DEBIT", ""):
        return None
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return None


def _i(v) -> Optional[int]:
    s = _s(v).replace("+", "")
    try:
        return int(s)
    except ValueError:
        return None


def _dt(v) -> Optional[datetime]:
    for fmt in ("%m/%d/%y %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%y"):
        try:
            return datetime.strptime(_s(v), fmt)
        except ValueError:
            pass
    return None


def _exp_date(v) -> Optional[date]:
    """Parse '14 Nov 25' → date."""
    try:
        return datetime.strptime(_s(v), "%d %b %y").date()
    except ValueError:
        return None


def _pct(v) -> Optional[float]:
    s = _s(v).replace("%", "").replace("+", "")
    try:
        return float(s)
    except ValueError:
        return None


def _cell(row: list, idx: int) -> str:
    return row[idx].strip() if idx < len(row) else ""


# ────────────────────────────── section parsers ────────────────────────────────

def _parse_trades(rows: list) -> list[dict]:
    """Parse Trade History rows (leading-blank column format)."""
    trades: list[dict] = []
    last_dt: Optional[datetime] = None
    last_spread: str = ""

    for row in rows:
        # Pad to 13 columns
        while len(row) < 13:
            row.append("")

        exec_raw    = _cell(row, 1)
        spread_type = _cell(row, 2)
        side        = _cell(row, 3)
        qty_raw     = _cell(row, 4)
        pos_effect  = _cell(row, 5)
        symbol      = _cell(row, 6)
        exp_raw     = _cell(row, 7)
        strike_raw  = _cell(row, 8)
        instr_type  = _cell(row, 9)
        price_raw   = _cell(row, 10)
        net_raw     = _cell(row, 11)
        order_type  = _cell(row, 12)

        if not symbol or "OVERALL" in symbol.upper():
            continue

        # Continuation row of a multi-leg spread (exec_raw is blank)
        is_continuation = (exec_raw == "" and symbol != "")
        dt = _dt(exec_raw) if not is_continuation else last_dt
        if dt:
            last_dt = dt
        if spread_type:
            last_spread = spread_type

        exp_d = _exp_date(exp_raw)
        is_option = instr_type in ("CALL", "PUT")

        # LEAPS: expiry > 1 year from trade date
        is_leaps = False
        if is_option and exp_d and dt:
            is_leaps = (exp_d - dt.date()).days > 365

        trade = {
            "datetime":         dt,
            "date_str":         dt.strftime("%Y-%m-%d") if dt else "",
            "spread_type":      spread_type or (last_spread if is_continuation else ""),
            "side":             side,
            "qty":              _i(qty_raw),
            "pos_effect":       pos_effect,
            "symbol":           symbol,
            "expiry":           exp_d,
            "expiry_str":       _s(exp_raw),
            "strike":           _f(strike_raw),
            "instr_type":       instr_type,
            "price":            _f(price_raw),
            "net_price":        _f(net_raw),
            "order_type":       order_type,
            "is_option":        is_option,
            "is_stock":         instr_type in ("STOCK", "ETF", ""),
            "is_leaps":         is_leaps,
            "is_continuation":  is_continuation,
        }
        trade["strategy"] = _classify_strategy(trade)
        trades.append(trade)

    return trades


def _parse_equities(rows: list) -> list[dict]:
    equities = []
    for row in rows:
        while len(row) < 10:
            row.append("")
        sym = _cell(row, 0)
        if not sym or sym in ("Symbol",) or "OVERALL" in sym.upper():
            continue
        equities.append({
            "symbol":      sym,
            "qty":         _i(_cell(row, 1)),
            "cost_basis":  _f(_cell(row, 2)),
            "mark":        _f(_cell(row, 3)),
            "mark_value":  _f(_cell(row, 4)),
            "pl_day":      _f(_cell(row, 5)),
            "pl_open":     _f(_cell(row, 6)),
            "pl_pct":      _pct(_cell(row, 7)),
            "account":     _cell(row, 8),
            "description": _cell(row, 9),
        })
    return equities


def _parse_options(rows: list) -> list[dict]:
    opts = []
    for row in rows:
        while len(row) < 13:
            row.append("")
        sym = _cell(row, 1)
        if not sym or sym in ("Symbol", "Account Name") or "OVERALL" in sym.upper():
            continue
        exp_d = _exp_date(_cell(row, 2))
        qty   = _i(_cell(row, 5))
        opts.append({
            "account":     _cell(row, 0),
            "symbol":      sym,
            "expiry":      exp_d,
            "expiry_str":  _cell(row, 2),
            "strike":      _f(_cell(row, 3)),
            "opt_type":    _cell(row, 4),
            "qty":         qty,
            "cost_basis":  _f(_cell(row, 6)),
            "mark":        _f(_cell(row, 7)),
            "mark_value":  _f(_cell(row, 8)),
            "pl_day":      _f(_cell(row, 9)),
            "pl_open":     _f(_cell(row, 10)),
            "pl_pct":      _pct(_cell(row, 11)),
            "option_code": _cell(row, 12),
            "is_short":    qty is not None and qty < 0,
            "days_to_exp": (exp_d - date.today()).days if exp_d else None,
        })
    return opts


# ───────────────────────── strategy classification ────────────────────────────

def _classify_strategy(t: dict) -> str:
    spread = t.get("spread_type", "")
    instr  = t.get("instr_type", "")
    side   = t.get("side", "")
    pos    = t.get("pos_effect", "")
    leaps  = t.get("is_leaps", False)

    if spread in ("CALENDAR",):
        return "Calendar Spread"
    if spread in ("DIAGONAL",):
        return "Diagonal Spread"

    if instr == "STOCK":
        return "Stock Swing"
    if instr == "ETF":
        return "ETF Trade"

    if instr in ("CALL", "PUT"):
        if pos == "TO OPEN":
            if side == "BUY":
                return ("LEAPS Call" if instr == "CALL" else "LEAPS Put") if leaps else (
                    "Long Call" if instr == "CALL" else "Long Put"
                )
            else:  # SELL TO OPEN
                return "Cash Secured Put" if instr == "PUT" else "Covered Call"
        else:  # TO CLOSE
            return f"Close {instr}"
    return "Other"


# ──────────────────────────── main entry point ────────────────────────────────

def parse_tos_csv(content: str) -> dict:
    """
    Parse a ToS/Schwab account statement CSV.
    Returns:
        account_name : str
        trades       : list[dict]   — trade history
        equities     : list[dict]   — current equity open positions
        options      : list[dict]   — current option open positions
    """
    reader = csv.reader(io.StringIO(content))
    rows   = [r for r in reader]

    # Account name (row 1)
    account_name = "Unknown Account"
    if rows and len(rows[0]) >= 2 and rows[0][0].strip() == "Account Name":
        account_name = rows[0][1].strip()

    # Find section boundaries
    trade_start = eq_start = opt_start = None
    for i, row in enumerate(rows):
        first = row[0].strip() if row else ""
        if first == "Account Trade History":
            trade_start = i + 2    # skip label + header row
        elif first == "Equities":
            eq_start    = i + 2
        elif first == "Options":
            opt_start   = i + 2

    trades   = _parse_trades(rows[trade_start : eq_start - 2 if eq_start else len(rows)]) \
               if trade_start else []
    equities = _parse_equities(rows[eq_start  : opt_start - 2 if opt_start else len(rows)]) \
               if eq_start else []
    options  = _parse_options(rows[opt_start :]) if opt_start else []

    return {
        "account_name": account_name,
        "trades":       trades,
        "equities":     equities,
        "options":      options,
    }


# ─────────────────────────── P&L matching engine ─────────────────────────────

# ── Stock split history ────────────────────────────────────────────────────────
# Robinhood CSV does NOT always export SPL records for large-cap stocks.
# Without split adjustment, FIFO matches post-split sells against pre-split
# cost basis → phantom losses (e.g. AMZN 20:1 split: cost $3,420 → $171).
#
# Format: { "SYMBOL": [(effective_date, ratio), ...] }
# ratio > 1 = forward split (more shares, lower price)
# ratio < 1 = reverse split (fewer shares, higher price)
_STOCK_SPLITS: dict[str, list[tuple]] = {
    "AMZN": [(date(2022, 6, 6),   20.0)],   # 20:1 Jun 2022
    "TSLA": [(date(2020, 8, 31),   5.0),     # 5:1 Aug 2020
             (date(2022, 8, 25),   3.0)],    # 3:1 Aug 2022
    "NVDA": [(date(2021, 7, 20),   4.0),     # 4:1 Jul 2021
             (date(2024, 6, 10),  10.0)],    # 10:1 Jun 2024
    "AAPL": [(date(2020, 8, 31),   4.0)],    # 4:1 Aug 2020
    "GOOGL": [(date(2022, 7, 18), 20.0)],   # 20:1 Jul 2022
    "GOOG":  [(date(2022, 7, 18), 20.0)],
    "SHOP":  [(date(2022, 6, 29), 10.0)],   # 10:1 Jun 2022
    "DXCM":  [(date(2022, 6, 10),  4.0)],   # 4:1 Jun 2022
}


def compute_realized_pnl(trades: list[dict]) -> pd.DataFrame:
    """
    FIFO-match open/close pairs from trade history.
    Options multiplier = 100.  Stocks = 1.

    Inline split adjustment: as the chronological scan crosses a known split
    date, all lots still in the FIFO queue are repriced and re-quantified.
    This correctly handles positions that straddled a split without touching
    lots that were already closed before the split date.

    Returns DataFrame sorted by close_date descending.
    """
    # Group by instrument key
    groups: dict[tuple, list] = defaultdict(list)
    for t in trades:
        if t.get("is_continuation"):
            continue
        if t.get("is_option"):
            key = (t["symbol"],
                   str(t.get("expiry", "")),
                   str(t.get("strike", "")),
                   t.get("instr_type", ""))
        else:
            key = (t["symbol"], "STOCK", "", "")
        if t.get("datetime") and t.get("symbol"):
            groups[key].append(t)

    records = []
    for key, grp in groups.items():
        symbol      = key[0]
        is_option   = key[1] not in ("STOCK", "")
        multiplier  = 100 if is_option else 1
        sorted_grp  = sorted(grp, key=lambda x: x["datetime"] or datetime.min)

        longs: list[dict]  = []   # BUY TO OPEN queue
        shorts: list[dict] = []   # SELL TO OPEN queue

        # Prepare inline split schedule for this symbol (stocks only)
        pending_splits: list[tuple] = []
        if not is_option and symbol in _STOCK_SPLITS:
            pending_splits = sorted(_STOCK_SPLITS[symbol])   # [(date, ratio), ...]
        split_idx = 0   # pointer to next unapplied split

        for t in sorted_grp:
            side  = t.get("side", "")
            pos   = t.get("pos_effect", "")
            qty   = abs(t.get("qty") or 0)
            price = t.get("price")
            dt    = t.get("datetime")
            # Skip only if qty is missing; price=0 is valid for OEXP/OASGN
            if not qty:
                continue
            # For non-close trades, price must exist; for close trades, price can be 0
            if price is None and pos != "TO CLOSE":
                continue
            # Ensure price is numeric
            if price is None:
                price = 0

            # ── Apply any stock splits that occurred before this trade ─────────
            if dt and split_idx < len(pending_splits):
                while split_idx < len(pending_splits):
                    split_date, ratio = pending_splits[split_idx]
                    if dt.date() < split_date:
                        break   # this split hasn't happened yet
                    # Split happened — adjust all open lots still in queue
                    for lot in longs:
                        lot["price"] /= ratio
                        lot["qty"]   *= ratio
                    split_idx += 1

            if pos == "TO OPEN":
                queue = longs if side == "BUY" else shorts
                queue.append({"dt": dt, "qty": qty, "price": price, "trade": t})

            elif pos == "TO CLOSE":
                # SELL TO CLOSE → close longs;  BUY TO CLOSE → close shorts
                close_longs  = (side == "SELL")
                source_queue = longs if close_longs else shorts
                remaining    = qty

                while remaining > 0 and source_queue:
                    o  = source_queue[0]
                    mq = min(remaining, o["qty"])
                    if close_longs:
                        pnl = (price - o["price"]) * mq * multiplier
                        pnl_pct = ((price - o["price"]) / o["price"] * 100) if o["price"] else 0
                    else:
                        pnl = (o["price"] - price) * mq * multiplier
                        pnl_pct = ((o["price"] - price) / o["price"] * 100) if o["price"] else 0

                    hold_days = (dt - o["dt"]).days if dt and o["dt"] else 0
                    strat     = _classify_strategy(o["trade"])

                    records.append({
                        "symbol":      symbol,
                        "expiry_str":  key[1],
                        "strike":      key[2],
                        "opt_type":    key[3],
                        "strategy":    strat,
                        "direction":   "Long" if close_longs else "Short",
                        "open_date":   o["dt"],
                        "close_date":  dt,
                        "hold_days":   hold_days,
                        "qty":         mq,
                        "open_price":  o["price"],
                        "close_price": price,
                        "pnl":         round(pnl, 2),
                        "pnl_pct":     round(pnl_pct, 1),
                        "multiplier":  multiplier,
                        "winner":      pnl > 0,
                    })
                    o["qty"]   -= mq
                    remaining  -= mq
                    if o["qty"] <= 0:
                        source_queue.pop(0)

    if not records:
        return pd.DataFrame(columns=["symbol","strategy","open_date","close_date",
                                      "hold_days","pnl","pnl_pct","winner"])
    df = pd.DataFrame(records)
    df["open_date"]  = pd.to_datetime(df["open_date"])
    df["close_date"] = pd.to_datetime(df["close_date"])
    return df.sort_values("close_date", ascending=False).reset_index(drop=True)


# ────────────────────────── delta-merge helper ────────────────────────────────

def _trade_sig(t: dict) -> str:
    """Unique fingerprint for deduplication across delta uploads."""
    return "|".join([
        t.get("date_str", ""),
        t.get("symbol", ""),
        t.get("side", ""),
        str(t.get("qty", "")),
        str(t.get("price", "")),
        t.get("expiry_str", ""),
        str(t.get("strike", "")),
        t.get("instr_type", ""),
    ])


# ══════════════════════════════════════════════════════════════════════════════
# ROBINHOOD PARSER
# ══════════════════════════════════════════════════════════════════════════════
#
# RH CSV columns:
#   Activity Date | Process Date | Settle Date | Instrument | Description
#   | Trans Code | Quantity | Price | Amount
#
# Trans Code → our (side, pos_effect, is_option):
#   BTO  → BUY  / TO OPEN  / option
#   STO  → SELL / TO OPEN  / option
#   BTC  → BUY  / TO CLOSE / option
#   STC  → SELL / TO CLOSE / option
#   Buy  → BUY  / TO OPEN  / stock
#   Sell → SELL / TO CLOSE / stock
#   OEXP → BUY  / TO CLOSE / option  (expired worthless, price=0)
#   OASGN→ BUY  / TO CLOSE / option  (assigned, price=0; stock row follows)
#   OEXRC→ SELL / TO CLOSE / option  (exercised, price=0)
#
# Option Description format:  "{SYMBOL} {M/D/YYYY} {Put|Call} ${STRIKE}"
#   e.g.  "SOFI 5/8/2026 Put $16.00"
#         "NOW 1/21/2028 Call $85.00"
# ──────────────────────────────────────────────────────────────────────────────

import re as _re


def _rh_clean(content: str) -> str:
    """Strip UTF-8 BOM and normalise line endings."""
    return content.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")


def _rh_delimiter(content: str) -> str:
    """
    Detect tab vs comma by looking at the ACTUAL data-header line
    (the one containing 'Activity Date'), not necessarily the first line.
    """
    for line in _rh_clean(content).split("\n"):
        if "Activity Date" in line:
            return "\t" if line.count("\t") > line.count(",") else ","
    # Fallback: check first line
    first = _rh_clean(content).split("\n")[0]
    return "\t" if first.count("\t") > first.count(",") else ","


def _rh_find_header(lines: list[str], delim: str) -> tuple[int, str | None]:
    """
    Find the index of the data-header row (containing 'Activity Date' and
    'Trans Code') and optionally extract the account name from a preamble row.
    Returns (header_idx, detected_account_name).
    """
    acct_name: str | None = None

    for i, line in enumerate(lines):
        cols = [c.strip().strip('"') for c in line.split(delim)]  # strip quotes
        # Preamble row: "Account name  <name>"
        if cols and cols[0].lower() in ("account name", "account"):
            if len(cols) > 1 and cols[1]:
                acct_name = cols[1]
        # Actual data header
        if "Activity Date" in cols and "Trans Code" in cols:
            return i, acct_name

    return -1, acct_name   # not found


def peek_rh_account(content: str) -> str:
    """
    Fast scan — return detected account name without full parse.
    Works whether headers are on row 1 (no preamble) or after a preamble.
    Falls back to 'Robinhood Account' if no name found.
    """
    content = _rh_clean(content)
    delim   = _rh_delimiter(content)
    _, name = _rh_find_header(content.split("\n"), delim)
    return name or "Robinhood Account"


# ── Robinhood trans code master table ─────────────────────────────────────────
# cat:
#   "option"    → option trade   (feeds P&L engine)
#   "stock"     → stock/ETF trade (feeds P&L engine)
#   "cash"      → cash flow      (feeds deposit/withdrawal summary)
#   "corporate" → corporate action (recorded, no P&L)
#   "skip"      → ignore entirely (unknown / irrelevant)

_RH_MASTER: dict[str, dict] = {
    # ── Option trades ─────────────────────────────────────────────────────────
    "BTO":   {"cat": "option", "side": "BUY",  "pos_effect": "TO OPEN",
              "note": "Buy to Open"},
    "STO":   {"cat": "option", "side": "SELL", "pos_effect": "TO OPEN",
              "note": "Sell to Open (CSP / CC)"},
    "BTC":   {"cat": "option", "side": "BUY",  "pos_effect": "TO CLOSE",
              "note": "Buy to Close"},
    "STC":   {"cat": "option", "side": "SELL", "pos_effect": "TO CLOSE",
              "note": "Sell to Close"},
    "OEXP":  {"cat": "option", "side": "BUY",  "pos_effect": "TO CLOSE",
              "price_override": 0.0,
              "note": "Option Expired (worthless) → close @ $0"},
    "OASGN": {"cat": "option", "side": "BUY",  "pos_effect": "TO CLOSE",
              "price_override": 0.0,
              "note": "Option Assigned → close option @ $0; stock row follows"},
    "OEXCS": {"cat": "option", "side": "SELL", "pos_effect": "TO CLOSE",
              "price_override": 0.0,
              "note": "Option Exercised (you exercised a call) → close @ $0"},
    # legacy spelling seen in some exports
    "OEXRC": {"cat": "option", "side": "SELL", "pos_effect": "TO CLOSE",
              "price_override": 0.0,
              "note": "Option Exercise (alt code)"},

    # ── Stock / ETF trades ────────────────────────────────────────────────────
    "Buy":   {"cat": "stock", "side": "BUY",  "pos_effect": "TO OPEN",
              "note": "Stock / ETF purchase"},
    "Sell":  {"cat": "stock", "side": "SELL", "pos_effect": "TO CLOSE",
              "note": "Stock / ETF sale"},
    "LIQ":   {"cat": "stock", "side": "SELL", "pos_effect": "TO CLOSE",
              "note": "Liquidation (forced sale)"},

    # ── Cash flows ────────────────────────────────────────────────────────────
    "ACH":   {"cat": "cash", "cash_type": "Transfer",
              "note": "ACH deposit (+) or withdrawal (-)"},
    "INT":   {"cat": "cash", "cash_type": "Interest",
              "note": "Interest income"},
    "CDIV":  {"cat": "cash", "cash_type": "Dividend",
              "note": "Cash dividend"},
    "RTP":   {"cat": "cash", "cash_type": "Return of Capital",
              "note": "Return of capital / tax-related payment"},
    "ITRF":  {"cat": "cash", "cash_type": "Transfer",
              "note": "Internal transfer between RH accounts"},
    "T/A":   {"cat": "cash", "cash_type": "Transfer",
              "note": "Transfer and Assignment (account transfer in/out)"},
    "GMPC":  {"cat": "cash", "cash_type": "Gold Credit",
              "note": "Robinhood Gold Monthly Payment Credit"},
    "GOLD":  {"cat": "cash", "cash_type": "Gold Fee",
              "note": "Robinhood Gold subscription fee"},
    "FEE":   {"cat": "cash", "cash_type": "Fee",
              "note": "Regulatory / trading fee"},
    "LCAP":  {"cat": "cash", "cash_type": "Distribution",
              "note": "Long-term capital gain distribution (ETF)"},
    "SPR":   {"cat": "cash", "cash_type": "Special Payment",
              "note": "Special payment / redistribution"},

    # ── Corporate actions (record only, no P&L or cash impact) ───────────────
    "SPL":   {"cat": "corporate",
              "note": "Stock split — adjusts share count, not a sale"},
    "OCA":   {"cat": "corporate",
              "note": "Option Contract Adjustment (post-split)"},
    "SOFF":  {"cat": "corporate",
              "note": "Spinoff — shares received from corporate spinoff"},
    "SXCH":  {"cat": "corporate",
              "note": "Stock Exchange — M&A share swap"},
    "CONV":  {"cat": "corporate",
              "note": "Conversion (e.g., preferred → common)"},
    "ACATO": {"cat": "corporate",
              "note": "Acquisition To — shares received in tender / merger"},
    "REC":   {"cat": "corporate",
              "note": "Receipt of shares (transfer in / gift)"},
}

_RH_OPT_RE = _re.compile(
    r"^(\w[\w.\-]*)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(Put|Call)\s+\$(\d+\.?\d*)",
    _re.IGNORECASE,
)
# Note: [\w.\-]* (not +) allows single-character tickers like F, T, X, C, V


_RH_DESC_STRIP = (
    "option expiration for ",
    "option exercise for ",
    "option assignment for ",
    "assigned - ",
)


def _parse_rh_opt_desc(desc: str) -> dict:
    """
    Parse option details from a Robinhood description field.
    Handles both bare format  'SOFI 5/8/2026 Put $16.00'
    and prefixed format       'Option Expiration for SOFI 5/1/2026 Put $16.00'.
    Returns {expiry, opt_type (CALL/PUT), strike} or {} if not an option.
    """
    raw = desc.strip().splitlines()[0].strip()   # first line only
    lower = raw.lower()
    for prefix in _RH_DESC_STRIP:
        if lower.startswith(prefix):
            raw = raw[len(prefix):]
            break
    m = _RH_OPT_RE.match(raw)
    if not m:
        return {}
    _, date_str, opt_type, strike_str = m.groups()
    try:
        exp = datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        exp = None
    return {
        "expiry":   exp,
        "opt_type": opt_type.upper(),
        "strike":   _f(strike_str),
    }


def parse_rh_csv(content: str,
                 account_name: str = "Robinhood Account") -> dict:
    """
    Parse a Robinhood activity CSV export.

    Returns:
        account_name : str
        trades       : list[dict]   — option + stock trades (P&L engine)
        cash_flows   : list[dict]   — ACH / dividends / fees / transfers
        corporates   : list[dict]   — splits / spinoffs / M&A (informational)
        equities     : []           — RH CSV has no open-position snapshot
        options      : []
        broker       : 'robinhood'

    Trans-code coverage:
        option  : BTO STO BTC STC OEXP OASGN OEXCS OEXRC
        stock   : Buy Sell LIQ
        cash    : ACH INT CDIV RTP ITRF T/A GMPC GOLD FEE LCAP SPR
        corporate: SPL OCA SOFF SXCH CONV ACATO REC
    """
    content = _rh_clean(content)

    # Use csv.DictReader directly to handle multiline quoted fields properly
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    trades     : list[dict] = []
    cash_flows : list[dict] = []
    corporates : list[dict] = []

    for row in rows:
        trans_code  = _s(row.get("Trans Code", ""))
        instrument  = _s(row.get("Instrument", ""))
        description = _s(row.get("Description", "")).replace("\n", " ")
        act_raw     = _s(row.get("Activity Date", ""))
        qty_raw     = _s(row.get("Quantity", ""))
        price_raw   = _s(row.get("Price", ""))
        amount_raw  = _s(row.get("Amount", ""))

        meta = _RH_MASTER.get(trans_code)
        if meta is None:
            continue           # truly unknown code — silently skip

        cat = meta["cat"]

        # Parse date
        dt = None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(act_raw, fmt)
                break
            except ValueError:
                pass
        date_str = dt.strftime("%Y-%m-%d") if dt else ""

        # ── Cash flow ─────────────────────────────────────────────────────────
        if cat == "cash":
            amount = _f(amount_raw)
            cash_flows.append({
                "datetime":   dt,
                "date_str":   date_str,
                "trans_code": trans_code,
                "cash_type":  meta.get("cash_type", "Other"),
                "instrument": instrument,
                "description":description,
                "amount":     amount,
                "note":       meta.get("note", ""),
            })
            continue

        # ── Corporate action ──────────────────────────────────────────────────
        if cat == "corporate":
            corporates.append({
                "datetime":   dt,
                "date_str":   date_str,
                "trans_code": trans_code,
                "instrument": instrument,
                "description":description,
                "qty":        _i(qty_raw),
                "note":       meta.get("note", ""),
            })
            continue

        # ── Trade (option or stock) ───────────────────────────────────────────
        side    = meta["side"]
        pos     = meta["pos_effect"]
        is_opt  = (cat == "option")

        # Use float qty for stocks (handles fractional share dividend reinvestment),
        # int qty for options (always whole contracts).
        if is_opt:
            qty_abs = abs(_i(qty_raw) or 0)
        else:
            qty_abs = abs(_f(qty_raw) or 0.0)
        qty = -qty_abs if side == "SELL" else qty_abs

        # OEXP/OASGN rows have empty Quantity; always 1 contract
        if trans_code in ("OEXP", "OASGN", "OEXCS", "OEXRC") and qty == 0:
            qty = 1 if side == "BUY" else -1

        price   = _f(price_raw)
        if "price_override" in meta and (price is None or price == 0.0):
            price = meta["price_override"]

        expiry     : Optional[date]  = None
        expiry_str : str             = ""
        strike     : Optional[float] = None
        instr_type : str             = "STOCK"

        if is_opt:
            opt        = _parse_rh_opt_desc(description)
            expiry     = opt.get("expiry")
            expiry_str = expiry.strftime("%d %b %y") if expiry else ""
            strike     = opt.get("strike")
            instr_type = opt.get("opt_type", "CALL")

        is_assignment_delivery = (
            not is_opt and "option assigned" in description.lower()
        )
        is_leaps = (
            is_opt and expiry and dt is not None
            and (expiry - dt.date()).days > 365
        )

        trade = {
            "datetime":               dt,
            "date_str":               date_str,
            "spread_type":            "",
            "side":                   side,
            "qty":                    qty,
            "pos_effect":             pos,
            "symbol":                 instrument,
            "expiry":                 expiry,
            "expiry_str":             expiry_str,
            "strike":                 strike,
            "instr_type":             instr_type,
            "price":                  price,
            "net_price":              price,
            "order_type":             "MKT",
            "is_option":              is_opt,
            "is_stock":               not is_opt,
            "is_leaps":               is_leaps,
            "is_continuation":        False,
            "broker":                 "Robinhood",
            "rh_trans_code":          trans_code,
            "is_assignment_delivery": is_assignment_delivery,
        }
        trade["strategy"] = _classify_strategy(trade)
        if is_assignment_delivery:
            trade["strategy"] = "CSP Assignment (stock)"
        trades.append(trade)

    return {
        "account_name": account_name,
        "trades":       trades,
        "cash_flows":   cash_flows,
        "corporates":   corporates,
        "equities":     [],
        "options":      [],
        "broker":       "Robinhood",
    }


# ── Auto-detect broker format ─────────────────────────────────────────────────

def detect_broker(content: str) -> str:
    """
    Return 'tos', 'robinhood', or 'unknown' based on CSV header fingerprint.

    ToS:         first row is  'Account Name,<name>,...'  (comma, capital N)
    Robinhood:   may have      'Account name<tab><name>'  (tab, lowercase n)
                 followed by the data header with 'Activity Date' + 'Trans Code'
    """
    snippet = _rh_clean(content)[:800]
    # ToS: always starts with 'Account Name' + comma (capital N, comma-sep)
    if snippet.startswith("Account Name,"):
        return "tos"
    # Robinhood: data header row contains both of these column names
    if "Activity Date" in snippet and "Trans Code" in snippet:
        return "robinhood"
    return "unknown"


def parse_broker_csv(content: str,
                     rh_account_name: str = "Robinhood Account") -> dict:
    """
    Detect broker format and call the correct parser.
    Returns the standard {account_name, trades, equities, options} dict.
    """
    broker = detect_broker(content)
    if broker == "tos":
        return parse_tos_csv(content)
    if broker == "robinhood":
        return parse_rh_csv(content, account_name=rh_account_name)
    raise ValueError(
        "Unrecognised CSV format. Expected a ToS/Schwab or Robinhood export."
    )


# ─────────────────────────────────────────────────────────────────────────────
def merge_upload(existing: dict, new_parsed: dict) -> dict:
    """
    Merge a delta upload into existing account data.
    - Trades: append new (deduplicated by fingerprint).
    - Equities / Options: replace entirely (snapshot of current positions).
    """
    if not existing:
        return new_parsed

    # Deduplicate trades
    seen_trades = {_trade_sig(t) for t in existing.get("trades", [])}
    added_trades = [t for t in new_parsed["trades"] if _trade_sig(t) not in seen_trades]

    # Deduplicate cash_flows by (date_str, trans_code, amount)
    def _cf_sig(c):
        return f"{c.get('date_str')}|{c.get('trans_code')}|{c.get('amount')}"

    seen_cf = {_cf_sig(c) for c in existing.get("cash_flows", [])}
    added_cf = [c for c in new_parsed.get("cash_flows", []) if _cf_sig(c) not in seen_cf]

    return {
        "account_name": new_parsed["account_name"],
        "trades":       existing["trades"] + added_trades,
        "cash_flows":   existing.get("cash_flows", []) + added_cf,
        "corporates":   new_parsed.get("corporates", []),   # always replace
        "equities":     new_parsed["equities"],
        "options":      new_parsed["options"],
        "last_import":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        "import_count": existing.get("import_count", 1) + 1,
    }

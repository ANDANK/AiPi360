"""
Nightly job — check market alerts (SPY, QQQ etc.) and notify if triggered.
Fetches prices from Yahoo Finance (yfinance — free, no API key needed).
"""
import os, sys, json, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date


def _gsheet_client():
    import gspread
    from google.oauth2.service_account import Credentials
    creds_dict = json.loads(os.environ.get("GSHEET_CREDENTIALS", "{}"))
    scopes     = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_alerts():
    import pandas as pd
    client = _gsheet_client()
    sh     = client.open_by_key(os.environ["SPREADSHEET_ID"])
    try:
        ws = sh.worksheet("market_alerts")
    except Exception:
        return []
    data = ws.get_all_records()
    if not data:
        return []
    df = pd.DataFrame(data)
    return df[df["active"].astype(str).str.upper().isin(["TRUE","1","YES"])].to_dict("records")


def _get_price_change(ticker: str, period: str = "1d") -> float | None:
    """Returns % change for the period. Requires yfinance."""
    try:
        import yfinance as yf
        t    = yf.Ticker(ticker)
        hist = t.history(period="1mo" if "month" in period else "5d")
        if len(hist) < 2:
            return None
        if "month" in period:
            pct = (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100
        else:
            pct = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100
        return round(pct, 2)
    except Exception:
        return None


def _send_push(title, message):
    topic = os.environ.get("NTFY_TOPIC", "")
    if not topic:
        return
    requests.post(f"https://ntfy.sh/{topic}", data=message.encode(),
                  headers={"Title": title, "Priority": "urgent", "Tags": "warning"},
                  timeout=10)


def main():
    print(f"Checking market alerts for {date.today()}…")
    alerts = _get_alerts()
    if not alerts:
        print("No active alerts.")
        return

    triggered = []
    for a in alerts:
        ticker    = a.get("ticker", "").upper()
        condition = a.get("condition", "").lower()
        threshold = float(a.get("threshold", 0) or 0)
        period    = "monthly" if "month" in condition else "daily"
        change    = _get_price_change(ticker, period)

        if change is None:
            print(f"Could not get price for {ticker}")
            continue

        is_fall = "falls" in condition
        triggered_flag = (is_fall and change <= -threshold) or (not is_fall and change >= threshold)
        print(f"{ticker}: {change:+.2f}% ({period}) — {'TRIGGERED' if triggered_flag else 'ok'}")

        if triggered_flag:
            direction = "fell" if change < 0 else "rose"
            msg = f"{ticker} {direction} {abs(change):.2f}% ({period}) — threshold: {threshold}%"
            triggered.append({"ticker": ticker, "msg": msg, "channels": a.get("channels","push")})

    if not triggered:
        print("No alerts triggered.")
        return

    for t in triggered:
        if "push" in t["channels"]:
            try:
                _send_push(f"📉 Market Alert: {t['ticker']}", t["msg"])
            except Exception as e:
                print(f"Push failed: {e}")
        print(f"Alert sent: {t['msg']}")


if __name__ == "__main__":
    main()

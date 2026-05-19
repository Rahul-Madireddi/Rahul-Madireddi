"""
S&P 500 Covered Call Backtester
=================================
Runs the same 5% OTM weekly covered call strategy across every stock
currently in the S&P 500 and ranks/compares the results.

⚠️  SURVIVORSHIP BIAS NOTE: We use today's S&P 500 membership list.
    Companies that were delisted or removed over the past 5 years are
    not included, which slightly flatters the results.

How it works:
  1. Scrape the current S&P 500 ticker list from Wikipedia.
  2. Batch-download 5 years of daily close prices for all ~503 tickers
     in a single yfinance call (much faster than individual downloads).
  3. For every ticker, simulate the covered call strategy:
       - Buy shares on the first day of the window.
       - Every Monday: sell a 5% OTM call expiring Friday, collect the
         premium, immediately buy fractional shares with it.
       - If the stock closes Friday above the strike, the call is
         exercised: sell at strike, buy back at market.
  4. Compare covered-call return vs. plain buy-and-hold for each stock.
  5. Save a summary CSV and a multi-panel chart.
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
import time
import warnings
import requests
from io import StringIO
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")   # suppress yfinance noise

# ── Settings ─────────────────────────────────────────────────────────────────
YEARS_OF_DATA    = 5
INITIAL_CAPITAL  = 10_000.0
OTM_PCT          = 0.05      # 5% out of the money
RISK_FREE_RATE   = 0.04      # simplified flat annual rate
VOL_LOOKBACK     = 20        # days for historical volatility
OPTION_SLIPPAGE  = 0.05      # sell calls at 95% of Black-Scholes fair value
STOCK_COMMISSION = 0.001     # 0.1% on stock purchases
MIN_WEEKS        = 100       # skip tickers with fewer than this many weeks of data
OUTPUT_CSV       = "sp500_results.csv"
OUTPUT_CHART     = "sp500_covered_call_chart.png"


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Get the S&P 500 ticker list
# ══════════════════════════════════════════════════════════════════════════════

def get_sp500_tickers() -> list[str]:
    """
    Scrapes the current S&P 500 component list from Wikipedia.
    Uses a browser-style User-Agent header because Wikipedia blocks the
    default Python urllib agent with a 403 error.
    Replaces dots with hyphens so yfinance can find tickers like BRK-B.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    print("Fetching S&P 500 ticker list from Wikipedia…")
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    tables = pd.read_html(StringIO(resp.text))
    df = tables[0]   # first table on the page is the component list
    tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
    print(f"  Found {len(tickers)} tickers")
    return tickers


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Batch download all close prices
# ══════════════════════════════════════════════════════════════════════════════

def download_all_prices(tickers: list[str], years: int) -> pd.DataFrame:
    """
    Downloads close prices for all tickers in a single yfinance call.
    This is ~50x faster than downloading each ticker individually.
    Returns a DataFrame with dates as the index and tickers as columns.
    """
    end   = datetime.today()
    start = end - timedelta(days=years * 365 + 90)   # +90-day volatility warm-up buffer

    print(f"\nBatch-downloading {years}-year price history for {len(tickers)} tickers…")
    print("  (this takes ~30–60 seconds)")

    raw = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        progress=True,
        auto_adjust=True,
    )

    # yfinance returns a multi-level column index: (PriceType, Ticker)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        # Edge case: only one ticker returned
        prices = raw[["Close"]]
        prices.columns = tickers[:1]

    prices.index.name = "date"
    print(f"  Got {prices.shape[0]} trading days × {prices.shape[1]} tickers")
    return prices


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Black-Scholes helper (same as covered_call_backtester.py)
# ══════════════════════════════════════════════════════════════════════════════

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes call price per share."""
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return max(0.0, S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2))


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Single-ticker covered call backtest
# ══════════════════════════════════════════════════════════════════════════════

def backtest_one(ticker: str, close_series: pd.Series) -> dict | None:
    """
    Runs the full covered call simulation for one ticker.
    Returns a results dict, or None if the ticker has insufficient data.

    This is the same logic as covered_call_backtester.py, condensed into
    a single function so we can call it 500 times efficiently.
    """
    try:
        # ── Build a clean price DataFrame ─────────────────────────────────
        df = close_series.dropna().to_frame("close")

        # Need at least VOL_LOOKBACK days for warm-up + enough weeks to be meaningful
        if len(df) < VOL_LOOKBACK + 60:
            return None

        # ── Historical volatility (annualised) ────────────────────────────
        log_ret = np.log(df["close"] / df["close"].shift(1))
        df["hv"] = log_ret.rolling(VOL_LOOKBACK).std() * math.sqrt(252)
        df["hv"] = df["hv"].fillna(0.30)   # 30% default during warm-up

        # ── Trim to the true 5-year window (drop warm-up buffer) ──────────
        cutoff = df.index[0] + timedelta(days=90)
        df = df[df.index >= cutoff].copy()
        if len(df) < 60:
            return None

        # ── Identify weekly (Monday → Friday) trading pairs ───────────────
        iso_id = df.index.to_series().apply(
            lambda d: f"{d.isocalendar()[0]}-{d.isocalendar()[1]:02d}"
        )
        weeks = [
            (g.index[0], g.index[-1])
            for _, g in df.groupby(iso_id, sort=True)
            if len(g) >= 2
        ]

        if len(weeks) < MIN_WEEKS:
            return None

        # ── Simulate the strategy ─────────────────────────────────────────
        first_price    = df["close"].iloc[0]
        current_shares = INITIAL_CAPITAL / (first_price * (1 + STOCK_COMMISSION))
        initial_shares = current_shares

        shares_on_date  = {}
        total_premium   = 0.0
        exercised_count = 0

        for week_open, week_close in weeks:
            mon_price = df.loc[week_open, "close"]
            sigma     = df.loc[week_open, "hv"]
            strike    = mon_price * (1.0 + OTM_PCT)

            week_len = len(df.loc[week_open:week_close])
            T        = max(week_len - 1, 1) / 252.0

            theo    = _bs_call(mon_price, strike, T, RISK_FREE_RATE, sigma)
            premium = theo * (1.0 - OPTION_SLIPPAGE) * current_shares

            # Reinvest premium into shares
            current_shares += premium / (mon_price * (1.0 + STOCK_COMMISSION))
            total_premium  += premium
            shares_on_date[week_open] = current_shares

            # Friday exercise check
            fri_price = df.loc[week_close, "close"]
            if fri_price > strike:
                exercised_count += 1
                proceeds        = current_shares * strike
                current_shares  = proceeds / (fri_price * (1.0 + STOCK_COMMISSION))
            shares_on_date[week_close] = current_shares

        # ── Daily portfolio value ─────────────────────────────────────────
        pv_list       = []
        running_sh    = initial_shares
        for date in df.index:
            if date in shares_on_date:
                running_sh = shares_on_date[date]
            pv_list.append(running_sh * df.loc[date, "close"])

        # ── Metrics ───────────────────────────────────────────────────────
        final_val    = pv_list[-1]
        cc_return    = (final_val - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
        bh_return    = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100

        pv   = np.array(pv_list)
        peak = np.maximum.accumulate(pv)
        max_dd = float(((peak - pv) / peak).max() * 100)

        return {
            "ticker":        ticker,
            "cc_return":     round(cc_return, 2),
            "bh_return":     round(bh_return, 2),
            "vs_bh":         round(cc_return - bh_return, 2),   # how much cc beat/lost to bh
            "final_value":   round(final_val, 2),
            "premium_total": round(total_premium, 2),
            "weeks":         len(weeks),
            "exercised":     exercised_count,
            "exercise_pct":  round(exercised_count / len(weeks) * 100, 1),
            "max_drawdown":  round(max_dd, 2),
        }

    except Exception:
        return None   # silently skip broken tickers


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Run all tickers
# ══════════════════════════════════════════════════════════════════════════════

def run_all(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Loops over every ticker column in prices_df, runs backtest_one(),
    and collects results into a DataFrame sorted by covered-call return.
    """
    tickers = prices_df.columns.tolist()
    results = []
    failed  = []

    print(f"\nRunning covered call backtest on {len(tickers)} tickers…")
    t0 = time.time()

    for i, ticker in enumerate(tickers, 1):
        result = backtest_one(ticker, prices_df[ticker])
        if result:
            results.append(result)
        else:
            failed.append(ticker)

        # Progress update every 50 tickers
        if i % 50 == 0 or i == len(tickers):
            elapsed = time.time() - t0
            print(f"  {i:>3}/{len(tickers)}  "
                  f"({len(results)} succeeded, {len(failed)} skipped)  "
                  f"[{elapsed:.0f}s]")

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values("cc_return", ascending=False).reset_index(drop=True)
    df_results.index += 1   # rank starts at 1

    if failed:
        print(f"\n  Skipped {len(failed)} tickers (insufficient data): "
              f"{', '.join(failed[:10])}{'…' if len(failed) > 10 else ''}")

    return df_results


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Summary statistics
# ══════════════════════════════════════════════════════════════════════════════

def print_summary(df: pd.DataFrame) -> None:
    """Prints a concise statistical breakdown of the full results."""

    cc   = df["cc_return"]
    bh   = df["bh_return"]
    diff = df["vs_bh"]

    winners = (diff >= 0).sum()    # tickers where cc beat buy-and-hold
    losers  = (diff <  0).sum()

    print("\n" + "=" * 68)
    print("  S&P 500 COVERED CALL BACKTEST — SUMMARY")
    print("=" * 68)
    print(f"  Tickers analysed              : {len(df)}")
    print(f"  CC beat buy-and-hold          : {winners} ({winners/len(df)*100:.1f}%)")
    print(f"  CC lagged buy-and-hold        : {losers}  ({losers/len(df)*100:.1f}%)")
    print()
    print(f"  {'Metric':<32}  {'CC Return':>10}  {'BH Return':>10}")
    print(f"  {'─'*32}  {'─'*10}  {'─'*10}")
    print(f"  {'Best return':<32}  {cc.max():>+9.1f}%  {bh.max():>+9.1f}%")
    print(f"  {'Median return':<32}  {cc.median():>+9.1f}%  {bh.median():>+9.1f}%")
    print(f"  {'Mean return':<32}  {cc.mean():>+9.1f}%  {bh.mean():>+9.1f}%")
    print(f"  {'Worst return':<32}  {cc.min():>+9.1f}%  {bh.min():>+9.1f}%")
    print(f"  {'Stocks with positive return':<32}  "
          f"{(cc>0).sum():>9}   {(bh>0).sum():>9}")
    print()
    print(f"  Avg covered-call drag vs BH   : {diff.mean():>+9.1f}%")
    print(f"  Median covered-call drag vs BH: {diff.median():>+9.1f}%")
    print("=" * 68)

    # Top 15
    print("\n  TOP 15 — Best covered call return:")
    print(f"  {'Rank':<5}  {'Ticker':<6}  {'CC Return':>10}  {'BH Return':>10}  "
          f"{'vs BH':>8}  {'Exercised':>10}  {'Max DD':>8}")
    print("  " + "─" * 65)
    for rank, row in df.head(15).iterrows():
        print(f"  {rank:<5}  {row['ticker']:<6}  {row['cc_return']:>+9.1f}%  "
              f"{row['bh_return']:>+9.1f}%  {row['vs_bh']:>+7.1f}%  "
              f"{row['exercised']:>5}/{row['weeks']:<4}  "
              f"{row['max_drawdown']:>7.1f}%")

    # Bottom 15
    print("\n  BOTTOM 15 — Worst covered call return:")
    print(f"  {'Rank':<5}  {'Ticker':<6}  {'CC Return':>10}  {'BH Return':>10}  "
          f"{'vs BH':>8}  {'Exercised':>10}  {'Max DD':>8}")
    print("  " + "─" * 65)
    for rank, row in df.tail(15).sort_values("cc_return").iterrows():
        print(f"  {rank:<5}  {row['ticker']:<6}  {row['cc_return']:>+9.1f}%  "
              f"{row['bh_return']:>+9.1f}%  {row['vs_bh']:>+7.1f}%  "
              f"{row['exercised']:>5}/{row['weeks']:<4}  "
              f"{row['max_drawdown']:>7.1f}%")

    print()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Charts
# ══════════════════════════════════════════════════════════════════════════════

def plot_summary(df: pd.DataFrame, output_file: str) -> None:
    """
    Four-panel chart:
      1. Scatter: buy-and-hold return vs covered call return (one dot per stock)
      2. Histogram: distribution of covered-call drag (cc_return - bh_return)
      3. Bar chart: top 25 stocks by covered call return
      4. Bar chart: bottom 25 stocks by covered call return
    """
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle(
        f"S&P 500 Covered Call Backtest  |  5% OTM Weekly Calls  |  5 Years  |  "
        f"n = {len(df)} stocks",
        fontsize=13, fontweight="bold", y=0.99,
    )

    gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.30)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    cc   = df["cc_return"]
    bh   = df["bh_return"]
    diff = df["vs_bh"]

    # ── Panel 1: scatter CC vs BH ─────────────────────────────────────────────
    colors = ["#2ca02c" if d >= 0 else "#d62728" for d in diff]
    ax1.scatter(bh, cc, c=colors, s=12, alpha=0.55, edgecolors="none")

    # y = x line: if a dot falls on this line the strategy matched buy-and-hold exactly
    lim = max(abs(bh.min()), abs(bh.max()), abs(cc.min()), abs(cc.max())) * 1.05
    ax1.plot([-lim, lim], [-lim, lim], color="gray", linestyle="--",
             linewidth=0.8, label="CC = BH (breakeven)")
    ax1.set_xlim(-lim, lim)
    ax1.set_ylim(-lim, lim)
    ax1.axhline(0, color="black", linewidth=0.4)
    ax1.axvline(0, color="black", linewidth=0.4)
    ax1.set_xlabel("Buy-and-Hold Return (%)", fontsize=10)
    ax1.set_ylabel("Covered Call Return (%)", fontsize=10)
    ax1.set_title("Covered Call vs Buy-and-Hold (per stock)", fontsize=10)
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.2)

    # ── Panel 2: histogram of drag ────────────────────────────────────────────
    ax2.hist(diff, bins=40, color="#1f77b4", alpha=0.8, edgecolor="white", linewidth=0.3)
    ax2.axvline(0,            color="gray",    linestyle="--", linewidth=0.9, label="Breakeven")
    ax2.axvline(diff.median(), color="#d62728", linestyle="-",  linewidth=1.2,
                label=f"Median drag: {diff.median():+.1f}%")
    ax2.set_xlabel("Covered Call Return minus Buy-and-Hold (%)", fontsize=10)
    ax2.set_ylabel("Number of stocks", fontsize=10)
    ax2.set_title("Distribution of Covered-Call Drag", fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.2, axis="y")

    # ── Panel 3: top 25 ───────────────────────────────────────────────────────
    top25 = df.head(25)
    bar_colors_top = ["#2ca02c" if v >= 0 else "#d62728" for v in top25["cc_return"]]
    ax3.barh(top25["ticker"][::-1], top25["cc_return"][::-1],
             color=bar_colors_top[::-1], alpha=0.85)
    ax3.axvline(0, color="black", linewidth=0.5)
    ax3.set_xlabel("Covered Call Return (%)", fontsize=10)
    ax3.set_title("Top 25 Stocks by Covered Call Return", fontsize=10)
    ax3.grid(alpha=0.2, axis="x")
    ax3.tick_params(axis="y", labelsize=7)

    # ── Panel 4: bottom 25 ───────────────────────────────────────────────────
    bot25 = df.tail(25).sort_values("cc_return")
    bar_colors_bot = ["#2ca02c" if v >= 0 else "#d62728" for v in bot25["cc_return"]]
    ax4.barh(bot25["ticker"], bot25["cc_return"],
             color=bar_colors_bot, alpha=0.85)
    ax4.axvline(0, color="black", linewidth=0.5)
    ax4.set_xlabel("Covered Call Return (%)", fontsize=10)
    ax4.set_title("Bottom 25 Stocks by Covered Call Return", fontsize=10)
    ax4.grid(alpha=0.2, axis="x")
    ax4.tick_params(axis="y", labelsize=7)

    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"  Chart saved → {output_file}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 68)
    print("  S&P 500 COVERED CALL BACKTESTER")
    print("  5% OTM weekly calls, premium reinvested into fractional shares")
    print("  Starting capital per stock: $10,000   |   5-year window")
    print("=" * 68)

    # 1. Tickers
    tickers = get_sp500_tickers()

    # 2. Batch download
    prices = download_all_prices(tickers, YEARS_OF_DATA)

    # 3. Backtest every ticker
    results_df = run_all(prices)

    # 4. Print summary
    print_summary(results_df)

    # 5. Save CSV (open it in Excel for a full sortable table)
    results_df.to_csv(OUTPUT_CSV)
    print(f"  Full results saved → {OUTPUT_CSV}  ({len(results_df)} rows)")

    # 6. Save chart
    print()
    plot_summary(results_df, OUTPUT_CHART)


if __name__ == "__main__":
    main()

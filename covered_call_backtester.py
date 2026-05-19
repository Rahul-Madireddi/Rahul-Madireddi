"""
AAPL Covered Call Backtester
==============================
Strategy:
  1. Buy AAPL shares with $10,000 on day 1.
  2. Every Monday, sell a covered call at a strike 5% above the current price,
     expiring that same Friday (a "weekly" call).
  3. Collect the option premium and immediately reinvest it into fractional
     AAPL shares — no cash is ever left idle.
  4. At Friday's close:
       - If AAPL closed BELOW the strike → call expires worthless. Keep all
         your shares. Repeat next week.
       - If AAPL closed ABOVE the strike → call is exercised. Your shares get
         called away at the strike price (you miss the upside). You immediately
         buy back at the market price so the position continues.

NOTE on option pricing: Free historical options data is not available. We
estimate the fair value of each weekly call using the Black-Scholes formula,
which is the industry-standard model for this purpose.
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import math

# ── Settings ─────────────────────────────────────────────────────────────────
TICKER            = "AAPL"
YEARS_OF_DATA     = 5
INITIAL_CAPITAL   = 10_000.0
OTM_PCT           = 0.05     # strike = monday_close * 1.05
RISK_FREE_RATE    = 0.04     # 4% annualised (simplified flat rate)
VOL_LOOKBACK      = 20       # trading days used to estimate historical volatility
OPTION_SLIPPAGE   = 0.05     # sell calls at 95% of Black-Scholes value (bid-ask spread)
STOCK_COMMISSION  = 0.001    # 0.1% on every stock purchase


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def norm_cdf(x: float) -> float:
    """
    Cumulative distribution function of the standard normal distribution.
    We compute it from scratch so we don't need scipy.
    (This is the probability that a random number from a bell curve is ≤ x.)
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_call(S: float, K: float, T: float,
                        r: float, sigma: float) -> float:
    """
    Returns the fair value of a European call option per share.

    S     = stock price today
    K     = strike price  (we use S * 1.05 for 5% OTM)
    T     = time to expiry in YEARS (1 week ≈ 5/252 ≈ 0.020)
    r     = annual risk-free interest rate
    sigma = annualised volatility (e.g. 0.30 = 30%)

    The formula assumes log-normally distributed returns, which is a standard
    simplification used across the industry.
    """
    if T <= 0 or sigma <= 0:
        return max(0.0, S - K)   # at expiry: just what's in the money

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return max(0.0, S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2))


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Download price data
# ══════════════════════════════════════════════════════════════════════════════

def download_data(ticker: str, years: int) -> pd.DataFrame:
    """Downloads daily OHLCV data. Adds extra buffer for the volatility warm-up."""
    end   = datetime.today()
    start = end - timedelta(days=years * 365 + 90)   # 90-day buffer

    print(f"Downloading {years} years of {ticker} data from Yahoo Finance…")
    raw = yf.download(ticker,
                      start=start.strftime("%Y-%m-%d"),
                      end=end.strftime("%Y-%m-%d"),
                      progress=False)

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw[["Close", "Volume"]].copy()
    df.columns = ["close", "volume"]
    df.index.name = "date"
    df = df.dropna()

    print(f"  {len(df)} trading days  "
          f"({df.index[0].date()} → {df.index[-1].date()})")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Calculate historical (realised) volatility
# ══════════════════════════════════════════════════════════════════════════════

def add_hist_vol(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a column 'hist_vol' — the annualised standard deviation of daily
    log-returns over the past VOL_LOOKBACK days.

    We use this as our proxy for implied volatility when pricing options.
    For AAPL this is typically in the 25–40% range.
    """
    df = df.copy()
    log_ret       = np.log(df["close"] / df["close"].shift(1))
    df["hist_vol"] = log_ret.rolling(VOL_LOOKBACK).std() * math.sqrt(252)
    df["hist_vol"] = df["hist_vol"].fillna(0.30)   # default until enough history
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Identify week boundaries in the trading calendar
# ══════════════════════════════════════════════════════════════════════════════

def get_weekly_pairs(df: pd.DataFrame) -> list[tuple]:
    """
    Returns a list of (week_open_date, week_close_date) pairs where both
    dates are actual trading days (no weekends / holidays).
    Skips any week that has fewer than 2 trading days (e.g. holiday-shortened).
    """
    iso_week_id = df.index.to_series().apply(
        lambda d: f"{d.isocalendar()[0]}-{d.isocalendar()[1]:02d}"
    )
    weeks = []
    for _, group in df.groupby(iso_week_id, sort=True):
        if len(group) >= 2:
            weeks.append((group.index[0], group.index[-1]))
    return weeks


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Run the backtest week by week
# ══════════════════════════════════════════════════════════════════════════════

def run_backtest(df_full: pd.DataFrame):
    """
    Simulates the covered-call strategy.

    Returns:
      weekly_records   — one dict per week (strike, premium, exercise status…)
      portfolio_values — daily portfolio value (list, same length as df_range)
      df_range         — the price DataFrame for the 5-year window only
    """
    # ── Trim to the true 5-year window (drop the warm-up buffer) ─────────────
    cutoff    = df_full.index[0] + timedelta(days=90)
    df_range  = df_full[df_full.index >= cutoff].copy()

    # ── Initialise position: buy as many shares as possible on day 1 ─────────
    open_price = df_range["close"].iloc[0]
    shares     = INITIAL_CAPITAL / (open_price * (1 + STOCK_COMMISSION))
    print(f"  Opening position: {shares:.4f} shares at ${open_price:.2f}  "
          f"({df_range.index[0].date()})")

    # ── Build week list from the 5-year window ────────────────────────────────
    weeks = get_weekly_pairs(df_range)

    # We track shares as a running number; portfolio value = shares × daily close
    # Build a mapping  date → shares  that we update at Monday (buy) and Friday (exercise).
    shares_on_date = {}    # only dates where shares change
    current_shares = shares

    weekly_records = []
    total_premium_usd = 0.0

    for week_open, week_close in weeks:
        # ── MONDAY — sell the call, buy shares with premium ───────────────────
        monday_price = df_range.loc[week_open, "close"]
        sigma        = df_range.loc[week_open, "hist_vol"]

        # Strike: 5% above Monday's close
        strike = monday_price * (1.0 + OTM_PCT)

        # Time to expiry: number of trading days this week minus 1, converted to years
        week_slice  = df_range.loc[week_open:week_close]
        T_days      = max(len(week_slice) - 1, 1)
        T_years     = T_days / 252.0

        # Fair value per share → apply slippage (we sell at bid, not mid)
        theo_price  = black_scholes_call(monday_price, strike, T_years,
                                          RISK_FREE_RATE, sigma)
        sell_price  = theo_price * (1.0 - OPTION_SLIPPAGE)
        premium_usd = sell_price * current_shares    # total dollars collected

        # Reinvest premium: buy fractional shares at Monday's close
        new_shares          = premium_usd / (monday_price * (1.0 + STOCK_COMMISSION))
        current_shares     += new_shares
        total_premium_usd  += premium_usd

        # Record shares at start of week (after premium reinvestment)
        shares_on_date[week_open] = current_shares

        # ── FRIDAY — check if the call was exercised ──────────────────────────
        friday_price   = df_range.loc[week_close, "close"]
        exercised      = friday_price > strike
        shares_pre_ex  = current_shares

        if exercised:
            # Shares are called away at strike → proceeds → buy back at market
            proceeds       = current_shares * strike
            current_shares = proceeds / (friday_price * (1.0 + STOCK_COMMISSION))

        shares_on_date[week_close] = current_shares   # may or may not have changed

        weekly_records.append({
            "week_open":    week_open,
            "week_close":   week_close,
            "monday_price": monday_price,
            "strike":       strike,
            "friday_price": friday_price,
            "sigma_pct":    sigma * 100,
            "theo_premium": theo_price,
            "sell_premium": sell_price,
            "premium_usd":  premium_usd,
            "new_shares":   new_shares,
            "shares_after": current_shares,
            "exercised":    exercised,
        })

    # ── Build daily portfolio-value series ────────────────────────────────────
    # Walk every trading day; whenever shares_on_date has an entry, update
    # the running share count.
    portfolio_values = []
    running_shares   = shares   # initial value before any week
    for date in df_range.index:
        if date in shares_on_date:
            running_shares = shares_on_date[date]
        portfolio_values.append(running_shares * df_range.loc[date, "close"])

    print(f"  Simulated {len(weeks)} weeks  |  "
          f"total premium collected: ${total_premium_usd:,.2f}")

    return weekly_records, portfolio_values, df_range


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Performance metrics
# ══════════════════════════════════════════════════════════════════════════════

def calculate_metrics(weekly_records, portfolio_values, df_range):
    """Computes the headline numbers."""
    final_value  = portfolio_values[-1]
    total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    first_price  = df_range["close"].iloc[0]
    last_price   = df_range["close"].iloc[-1]
    bh_return    = (last_price - first_price) / first_price * 100

    # Shares accumulated: start vs. end
    initial_shares = INITIAL_CAPITAL / (first_price * (1 + STOCK_COMMISSION))
    final_shares   = portfolio_values[-1] / last_price

    exercised_count   = sum(1 for w in weekly_records if w["exercised"])
    unexercised_count = len(weekly_records) - exercised_count
    total_premium     = sum(w["premium_usd"] for w in weekly_records)

    # Max drawdown
    pv        = np.array(portfolio_values)
    peak      = np.maximum.accumulate(pv)
    drawdowns = (peak - pv) / peak
    max_dd    = drawdowns.max() * 100

    return {
        "final_value":        round(final_value, 2),
        "total_return":       round(total_return, 2),
        "bh_return":          round(bh_return, 2),
        "total_premium":      round(total_premium, 2),
        "initial_shares":     round(initial_shares, 4),
        "final_shares":       round(final_shares, 4),
        "weeks_total":        len(weekly_records),
        "weeks_exercised":    exercised_count,
        "weeks_unexercised":  unexercised_count,
        "max_drawdown":       round(max_dd, 2),
    }


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Chart
# ══════════════════════════════════════════════════════════════════════════════

def plot_results(df_range, weekly_records, portfolio_values,
                  output_file="covered_call_chart.png"):
    """
    Three-panel chart:
      1. AAPL price + weekly strike prices
      2. Weekly premium collected ($)
      3. Covered-call portfolio vs. buy-and-hold benchmark
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12),
                              gridspec_kw={"height_ratios": [3, 1.2, 1.5]},
                              sharex=True)
    fig.suptitle("AAPL Covered Call Strategy  |  5% OTM Weekly Calls  |  5-Year Backtest",
                 fontsize=13, fontweight="bold", y=0.995)

    ax1, ax2, ax3 = axes

    # ── Panel 1: price + strike levels ────────────────────────────────────────
    ax1.plot(df_range.index, df_range["close"],
             color="#333333", linewidth=0.9, label="AAPL Close", alpha=0.8, zorder=2)

    exercised   = [w for w in weekly_records if     w["exercised"]]
    unexercised = [w for w in weekly_records if not w["exercised"]]

    if unexercised:
        ax1.scatter([w["week_open"] for w in unexercised],
                    [w["strike"]    for w in unexercised],
                    marker="_", color="#2ca02c", s=25, linewidths=1.5,
                    alpha=0.55, label="Strike (expired worthless)", zorder=3)
    if exercised:
        ax1.scatter([w["week_open"] for w in exercised],
                    [w["strike"]    for w in exercised],
                    marker="_", color="#d62728", s=55, linewidths=2.5,
                    alpha=0.9, label="Strike (exercised — upside capped)", zorder=4)

    ax1.set_ylabel("Price (USD)", fontsize=10)
    ax1.legend(fontsize=8, loc="upper left")
    ax1.grid(alpha=0.25)

    # ── Panel 2: premium bar chart ────────────────────────────────────────────
    bar_colors = ["#d62728" if w["exercised"] else "#2ca02c" for w in weekly_records]
    ax2.bar([w["week_open"] for w in weekly_records],
            [w["premium_usd"] for w in weekly_records],
            color=bar_colors, width=4, alpha=0.75)
    ax2.set_ylabel("Premium ($)", fontsize=10)
    ax2.grid(alpha=0.25, axis="y")
    ax2.legend(handles=[
        mpatches.Patch(color="#2ca02c", label="Expired worthless"),
        mpatches.Patch(color="#d62728", label="Exercised"),
    ], fontsize=8, loc="upper left")

    # ── Panel 3: portfolio value vs buy-and-hold ──────────────────────────────
    first_price = df_range["close"].iloc[0]
    bh_values   = df_range["close"] / first_price * INITIAL_CAPITAL

    ax3.plot(df_range.index, portfolio_values,
             color="#2ca02c", linewidth=1.6, label="Covered call strategy")
    ax3.plot(df_range.index, bh_values,
             color="#1f77b4", linewidth=1.6, linestyle="--", label="Buy and hold AAPL")
    ax3.axhline(y=INITIAL_CAPITAL, color="gray", linestyle=":", linewidth=0.8,
                label=f"Starting capital ${INITIAL_CAPITAL:,.0f}")
    ax3.set_ylabel("Portfolio Value (USD)", fontsize=10)
    ax3.set_xlabel("Date", fontsize=10)
    ax3.legend(fontsize=8, loc="upper left")
    ax3.grid(alpha=0.25)

    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"  Chart saved → {output_file}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  AAPL Covered Call Backtester")
    print("  Strategy : sell 5% OTM call every Monday, expiry Friday")
    print("  Premium  : reinvested into fractional AAPL shares immediately")
    print("=" * 65)

    # 1. Data
    df = download_data(TICKER, YEARS_OF_DATA)
    df = add_hist_vol(df)

    # 2. Backtest
    print("\nRunning simulation…")
    weekly_records, portfolio_values, df_range = run_backtest(df)

    # 3. Metrics
    m = calculate_metrics(weekly_records, portfolio_values, df_range)

    # 4. Print results
    print("\n" + "=" * 65)
    print("  RESULTS")
    print("=" * 65)
    print(f"  Starting capital          : ${INITIAL_CAPITAL:>10,.2f}")
    print(f"  Ending portfolio value    : ${m['final_value']:>10,.2f}")
    print(f"  ─────────────────────────────────────────")
    print(f"  Covered call return       : {m['total_return']:>+9.2f}%")
    print(f"  Buy-and-hold AAPL return  : {m['bh_return']:>+9.2f}%")
    print(f"  ─────────────────────────────────────────")
    print(f"  Total premium collected   : ${m['total_premium']:>10,.2f}")
    print(f"  Shares at start           : {m['initial_shares']:>10.4f}")
    print(f"  Shares at end             : {m['final_shares']:>10.4f}  "
          f"(+{m['final_shares']-m['initial_shares']:.4f} from reinvestment)")
    print(f"  ─────────────────────────────────────────")
    print(f"  Weeks simulated           : {m['weeks_total']:>10}")
    print(f"  Calls expired worthless   : {m['weeks_unexercised']:>10}  "
          f"({m['weeks_unexercised']/m['weeks_total']*100:.1f}%)")
    print(f"  Calls exercised (capped)  : {m['weeks_exercised']:>10}  "
          f"({m['weeks_exercised']/m['weeks_total']*100:.1f}%)")
    print(f"  Max drawdown              : {m['max_drawdown']:>9.2f}%")
    print("=" * 65)

    # 5. Last 15 weeks detail
    print(f"\n  Last 15 weeks (of {m['weeks_total']} total):")
    print(f"  {'Mon Date':<12}  {'Mon $':>7}  {'Strike':>7}  {'Fri $':>7}  "
          f"{'σ':>5}  {'Premium':>8}  Status")
    print("  " + "─" * 66)
    for w in weekly_records[-15:]:
        status = "EXERCISED ▲" if w["exercised"] else "expired  ·"
        print(f"  {str(w['week_open'].date()):<12}  "
              f"{w['monday_price']:>7.2f}  "
              f"{w['strike']:>7.2f}  "
              f"{w['friday_price']:>7.2f}  "
              f"{w['sigma_pct']:>4.1f}%  "
              f"${w['premium_usd']:>7.2f}  "
              f"{status}")

    # 6. Chart
    print()
    plot_results(df_range, weekly_records, portfolio_values)


if __name__ == "__main__":
    main()

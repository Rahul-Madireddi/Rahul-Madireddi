"""
Moving Average Crossover Backtester
====================================
This script tests a simple trading strategy on the SPY ETF (which tracks the S&P 500).

Strategy logic:
  - BUY  when the 20-day average price crosses ABOVE the 50-day average price
  - SELL when the 20-day average price crosses BELOW the 50-day average price

Think of the moving averages as "smoothed" versions of the price.
The 20-day is more sensitive (reacts faster), the 50-day is slower.
When the fast line crosses the slow line going up, the market may be gaining momentum.
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import yfinance as yf          # downloads free historical stock data from Yahoo Finance
import pandas as pd            # used for tables of data (DataFrames)
import numpy as np             # math helpers (used for drawdown calculation)
import matplotlib               # plotting library
matplotlib.use("Agg")          # use non-interactive backend so it works without a screen
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# ── Settings (change these to experiment) ────────────────────────────────────
TICKER          = "SPY"        # the ETF we're trading
YEARS_OF_DATA   = 5            # how many years of history to download
INITIAL_CAPITAL = 10_000.0     # starting cash in dollars
SHORT_WINDOW    = 20           # "fast" moving average period (days)
LONG_WINDOW     = 50           # "slow" moving average period (days)
COMMISSION_PCT  = 0.001        # 0.1% commission per trade (realistic for retail brokers)
SLIPPAGE_PCT    = 0.0005       # 0.05% slippage — we assume fills are slightly worse than quoted


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Download historical price data
# ══════════════════════════════════════════════════════════════════════════════

def download_data(ticker: str, years: int) -> pd.DataFrame:
    """
    Downloads daily closing prices from Yahoo Finance.
    Returns a DataFrame (think: a spreadsheet) indexed by date.
    """
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=years * 365 + 30)  # +30 days buffer for MA warm-up

    print(f"Downloading {years} years of {ticker} data from Yahoo Finance…")
    raw = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"),
                               end=end_date.strftime("%Y-%m-%d"),
                               progress=False)

    # yfinance sometimes returns a multi-level column index — flatten it
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    # We only need the "Close" (closing price) and "Volume" columns
    df = raw[["Close", "Volume"]].copy()
    df.columns = ["close", "volume"]
    df.index.name = "date"
    df = df.dropna()  # remove any days with missing data

    print(f"  Downloaded {len(df)} trading days "
          f"({df.index[0].date()} → {df.index[-1].date()})")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Calculate moving averages and crossover signals
# ══════════════════════════════════════════════════════════════════════════════

def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds three new columns to the price table:
      sma_short  — 20-day simple moving average
      sma_long   — 50-day simple moving average
      signal     — +1 means BUY today, -1 means SELL today, 0 means do nothing
    """
    df = df.copy()

    # A simple moving average is just the average closing price over the last N days.
    # Example: the 3-day SMA on day 5 = (close[3] + close[4] + close[5]) / 3
    df["sma_short"] = df["close"].rolling(window=SHORT_WINDOW).mean()
    df["sma_long"]  = df["close"].rolling(window=LONG_WINDOW).mean()

    # "position" tracks whether the short MA is above (1) or below (0) the long MA
    df["position"] = np.where(df["sma_short"] > df["sma_long"], 1, 0)

    # A CROSSOVER happens when position flips from one day to the next.
    # diff() gives us +1 when it flipped from 0→1 (buy) and -1 when 1→0 (sell).
    df["signal"] = df["position"].diff().fillna(0).astype(int)

    # Drop rows where the MAs haven't had enough data to compute yet
    df = df.dropna(subset=["sma_short", "sma_long"]).copy()

    buy_count  = (df["signal"] ==  1).sum()
    sell_count = (df["signal"] == -1).sum()
    print(f"  Found {buy_count} buy signals and {sell_count} sell signals")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Simulate the trades
# ══════════════════════════════════════════════════════════════════════════════

def run_backtest(df: pd.DataFrame) -> tuple[list[dict], list[float]]:
    """
    Walks through each trading day in order and acts on buy/sell signals.

    Returns:
      trades           — list of individual trade records (buy price, sell price, profit, etc.)
      portfolio_values — list of total portfolio value at the close of each day
    """
    cash        = INITIAL_CAPITAL   # how much cash we currently hold
    shares      = 0                 # how many shares we currently own
    buy_price   = 0.0               # the price at which we last bought

    trades           = []           # we'll append a dict for every completed round-trip (buy+sell)
    portfolio_values = []           # daily snapshot of total value

    for date, row in df.iterrows():
        price  = row["close"]
        signal = row["signal"]

        # ── BUY signal ──────────────────────────────────────────────────────
        if signal == 1 and shares == 0 and cash > 0:
            # Slippage: assume we pay slightly more than the closing price
            fill_price = price * (1 + SLIPPAGE_PCT)

            # Commission: we pay a percentage of the total purchase amount
            max_spend   = cash / (1 + COMMISSION_PCT)   # leave room to pay commission
            shares      = max_spend / fill_price         # fractional shares allowed
            commission  = shares * fill_price * COMMISSION_PCT
            cash        = cash - (shares * fill_price) - commission
            buy_price   = fill_price

        # ── SELL signal ─────────────────────────────────────────────────────
        elif signal == -1 and shares > 0:
            # Slippage: assume we receive slightly less than the closing price
            fill_price = price * (1 - SLIPPAGE_PCT)
            proceeds   = shares * fill_price
            commission = proceeds * COMMISSION_PCT
            cash       = cash + proceeds - commission

            # Record the trade result
            profit_pct = (fill_price - buy_price) / buy_price * 100
            trades.append({
                "sell_date":  date,
                "buy_price":  round(buy_price, 4),
                "sell_price": round(fill_price, 4),
                "profit_pct": round(profit_pct, 2),
                "winner":     profit_pct > 0,
            })

            shares    = 0
            buy_price = 0.0

        # ── Daily portfolio snapshot ─────────────────────────────────────────
        # Total value = cash in hand  +  current market value of shares we hold
        portfolio_values.append(cash + shares * price)

    return trades, portfolio_values


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Calculate performance metrics
# ══════════════════════════════════════════════════════════════════════════════

def calculate_metrics(portfolio_values: list[float],
                       trades: list[dict],
                       df: pd.DataFrame) -> dict:
    """
    Computes the summary statistics we print at the end.
    """
    # ── Total return ────────────────────────────────────────────────────────
    final_value  = portfolio_values[-1]
    total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    # ── Buy-and-hold: what if we just bought on day 1 and never sold? ───────
    first_price    = df["close"].iloc[0]
    last_price     = df["close"].iloc[-1]
    bh_return      = (last_price - first_price) / first_price * 100

    # ── Win rate ─────────────────────────────────────────────────────────────
    # Of all the trades that were closed (sold), what fraction made money?
    if trades:
        win_rate = sum(1 for t in trades if t["winner"]) / len(trades) * 100
    else:
        win_rate = 0.0

    # ── Maximum drawdown ─────────────────────────────────────────────────────
    # The worst peak-to-trough decline the portfolio suffered at any point.
    # Example: portfolio goes $10k → $12k → $9k.  Drawdown = (12k - 9k) / 12k = 25%.
    pv        = np.array(portfolio_values)
    peak      = np.maximum.accumulate(pv)   # running maximum up to each day
    drawdowns = (peak - pv) / peak           # percentage drop from the peak
    max_dd    = drawdowns.max() * 100

    return {
        "final_value":  round(final_value, 2),
        "total_return": round(total_return, 2),
        "bh_return":    round(bh_return, 2),
        "num_trades":   len(trades),
        "win_rate":     round(win_rate, 2),
        "max_drawdown": round(max_dd, 2),
    }


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Draw and save the chart
# ══════════════════════════════════════════════════════════════════════════════

def plot_results(df: pd.DataFrame,
                  portfolio_values: list[float],
                  output_file: str = "backtest_chart.png") -> None:
    """
    Creates a two-panel chart:
      Top panel    — SPY closing price with both moving averages and trade arrows
      Bottom panel — total portfolio value over time
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                    gridspec_kw={"height_ratios": [3, 1]},
                                    sharex=True)
    fig.suptitle("SPY Moving Average Crossover Backtest", fontsize=15, fontweight="bold")

    # ── Top panel: price + moving averages + signals ─────────────────────────
    ax1.plot(df.index, df["close"],     color="#444444", linewidth=1.0,
             label="SPY Close", alpha=0.7)
    ax1.plot(df.index, df["sma_short"], color="#1f77b4", linewidth=1.5,
             label=f"{SHORT_WINDOW}-day SMA")
    ax1.plot(df.index, df["sma_long"],  color="#ff7f0e", linewidth=1.5,
             label=f"{LONG_WINDOW}-day SMA")

    # Draw a green upward arrow on every BUY day
    buys  = df[df["signal"] ==  1]
    sells = df[df["signal"] == -1]

    ax1.scatter(buys.index,  buys["close"]  * 0.985, marker="^", color="green",
                zorder=5, s=80, label="Buy signal")
    ax1.scatter(sells.index, sells["close"] * 1.015, marker="v", color="red",
                zorder=5, s=80, label="Sell signal")

    ax1.set_ylabel("Price (USD)", fontsize=11)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.3)

    # ── Bottom panel: portfolio value ─────────────────────────────────────────
    ax2.plot(df.index, portfolio_values, color="#2ca02c", linewidth=1.5,
             label="Portfolio value")
    ax2.axhline(y=INITIAL_CAPITAL, color="gray", linestyle="--",
                linewidth=0.8, label=f"Starting capital ${INITIAL_CAPITAL:,.0f}")
    ax2.set_ylabel("Portfolio Value (USD)", fontsize=11)
    ax2.set_xlabel("Date", fontsize=11)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(alpha=0.3)

    # Format the x-axis to show readable dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"\n  Chart saved → {output_file}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — tie everything together
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print("  MA Crossover Backtester — SPY")
    print("=" * 55)

    # 1. Get data
    df = download_data(TICKER, YEARS_OF_DATA)

    # 2. Add moving averages and crossover signals
    print("\nCalculating moving averages and signals…")
    df = add_signals(df)

    # 3. Run the simulated trades
    print("\nRunning backtest…")
    trades, portfolio_values = run_backtest(df)

    # 4. Compute summary statistics
    metrics = calculate_metrics(portfolio_values, trades, df)

    # 5. Print results
    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)
    print(f"  Starting capital   : ${INITIAL_CAPITAL:>10,.2f}")
    print(f"  Ending value       : ${metrics['final_value']:>10,.2f}")
    print(f"  Strategy return    : {metrics['total_return']:>+9.2f}%")
    print(f"  Buy-and-hold return: {metrics['bh_return']:>+9.2f}%")
    print(f"  Number of trades   : {metrics['num_trades']:>10}")
    print(f"  Win rate           : {metrics['win_rate']:>9.1f}%")
    print(f"  Max drawdown       : {metrics['max_drawdown']:>9.2f}%")
    print("=" * 55)

    # Show every individual trade
    if trades:
        print("\n  Individual trades:")
        print(f"  {'Sell Date':<12}  {'Buy $':>8}  {'Sell $':>8}  {'P/L':>7}  Result")
        print("  " + "-" * 50)
        for t in trades:
            result = "WIN " if t["winner"] else "LOSS"
            print(f"  {str(t['sell_date'].date()):<12}  "
                  f"{t['buy_price']:>8.2f}  "
                  f"{t['sell_price']:>8.2f}  "
                  f"{t['profit_pct']:>+6.2f}%  {result}")

    # 6. Save chart
    plot_results(df, portfolio_values)


if __name__ == "__main__":
    main()

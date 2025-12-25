"""
Real-market multi-asset backtest harness for the trading bot.

What it does:
- Fetches OHLCV for all 15 supported assets (crypto, gold, futures, 11 forex).
- Runs a volatility/MA strategy per asset using the shared BacktestEngine
  (includes slippage + fees).
- Produces JSON + Markdown summaries with per-asset and portfolio metrics.

How to run (example):
    python real_market_backtest.py --bars 1500 --interval 60 --capital 500 --risk 0.01

Notes:
- Uses TradingViewDataClient (yfinance fallback). Provide your network/API access.
- Adjust slippage/fees per asset in ASSETS if your broker differs.
- Results are saved under backtests/ by default.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from backtest_engine import BacktestEngine
from performance_metrics import PerformanceMetrics
from tradingview_data_client import TradingViewDataClient

# Asset universe (15 assets) with realistic cost assumptions (bps = 0.01%)
ASSETS: List[Dict] = [
    {"name": "BTC", "tv_symbol": "BTC", "interval": "60", "bars": 1500, "slippage_bps": 8, "fee_bps": 7},
    {"name": "GOLD", "tv_symbol": "XAUUSD", "interval": "60", "bars": 1500, "slippage_bps": 3, "fee_bps": 4},
    {"name": "ES", "tv_symbol": "CME:ES1!", "interval": "60", "bars": 1500, "slippage_bps": 2, "fee_bps": 2},
    {"name": "NQ", "tv_symbol": "CME:NQ1!", "interval": "60", "bars": 1500, "slippage_bps": 2, "fee_bps": 2},
    {"name": "EURUSD", "tv_symbol": "EURUSD", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "GBPUSD", "tv_symbol": "GBPUSD", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "USDJPY", "tv_symbol": "USDJPY", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "AUDUSD", "tv_symbol": "AUDUSD", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "USDCAD", "tv_symbol": "USDCAD", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "EURJPY", "tv_symbol": "EURJPY", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "NZDUSD", "tv_symbol": "NZDUSD", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "EURGBP", "tv_symbol": "EURGBP", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "GBPJPY", "tv_symbol": "GBPJPY", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "AUDJPY", "tv_symbol": "AUDJPY", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
    {"name": "USDCHF", "tv_symbol": "USDCHF", "interval": "60", "bars": 1500, "slippage_bps": 1, "fee_bps": 1},
]


def compute_atr(data: pd.DataFrame, length: int = 14) -> float:
    """Lightweight ATR calculation (no TA-lib dependency)."""
    if len(data) < length + 1:
        return 0.0
    highs = data["high"]
    lows = data["low"]
    closes = data["close"]
    prev_close = closes.shift(1)
    tr = pd.concat(
        [
            highs - lows,
            (highs - prev_close).abs(),
            (lows - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return float(tr.tail(length).mean())


def make_strategy(asset: Dict):
    """
    Simple, robust strategy for backtesting harness:
    - Trend filter: 20/50 SMA crossover
    - Volatility-based stop using ATR
    - Two take-profit targets (1.8R, 3.0R)
    """

    def strategy(data: pd.DataFrame) -> Dict:
        window_fast, window_slow = 20, 50
        if len(data) < window_slow + 5:
            return {"direction": "HOLD"}

        recent = data.tail(window_slow + 5)
        closes = recent["close"]
        fast = closes.rolling(window_fast).mean().iloc[-1]
        slow = closes.rolling(window_slow).mean().iloc[-1]
        atr = compute_atr(recent, length=14)

        if atr <= 0:
            return {"direction": "HOLD"}

        entry = closes.iloc[-1]
        stop_distance = atr * asset.get("atr_mult", 1.2)

        if fast > slow and entry > fast:
            direction = "BUY"
            stop_loss = entry - stop_distance
            tp1 = entry + stop_distance * 1.8
            tp2 = entry + stop_distance * 3.0
        elif fast < slow and entry < fast:
            direction = "SELL"
            stop_loss = entry + stop_distance
            tp1 = entry - stop_distance * 1.8
            tp2 = entry - stop_distance * 3.0
        else:
            return {"direction": "HOLD"}

        return {
            "direction": direction,
            "entry_price": entry,
            "stop_loss": stop_loss,
            "take_profit_1": tp1,
            "take_profit_2": tp2,
        }

    return strategy


def load_ohlcv(
    client: TradingViewDataClient,
    asset: Dict,
    bars_override: Optional[int],
    interval_override: Optional[str],
) -> Optional[pd.DataFrame]:
    """Fetch OHLCV with optional CLI overrides."""
    bars = bars_override or asset.get("bars", 800)
    interval = interval_override or asset.get("interval", "60")

    df = client.get_data(asset["tv_symbol"], interval=str(interval), n_bars=bars)
    if df is None or len(df) == 0:
        return None

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")

    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df.sort_index(inplace=True)
    return df


def run_asset_backtest(
    asset: Dict,
    args: argparse.Namespace,
    client: TradingViewDataClient,
) -> Optional[Dict]:
    """Run backtest for a single asset."""
    df = load_ohlcv(client, asset, args.bars, args.interval)
    if df is None or len(df) < 80:
        print(f"⚠️  Skipping {asset['name']} (insufficient data)")
        return None

    engine = BacktestEngine(
        initial_capital=args.capital,
        risk_per_trade=args.risk,
        slippage=asset.get("slippage_bps", 0) / 10000,
        fee=asset.get("fee_bps", 0) / 10000,
    )

    engine.run_backtest(df, make_strategy(asset), verbose=args.verbose)

    trades_df = engine.get_trades_df()
    equity_df = engine.get_equity_curve_df()

    metrics_calc = PerformanceMetrics(trades_df, equity_df, engine.initial_capital)
    metrics = metrics_calc.calculate_all_metrics()
    metrics["final_capital"] = float(metrics_calc.final_capital)
    metrics["slippage_bps"] = asset.get("slippage_bps", 0)
    metrics["fee_bps"] = asset.get("fee_bps", 0)

    return {
        "asset": asset["name"],
        "symbol": asset["tv_symbol"],
        "trades": int(metrics.get("total_trades", 0)),
        "metrics": metrics,
    }


def build_portfolio_summary(results: List[Dict], per_asset_capital: float) -> Dict:
    """Aggregate basic portfolio-level stats from per-asset runs."""
    if not results:
        return {"message": "No assets produced results"}

    total_trades = sum(r["metrics"].get("total_trades", 0) for r in results)
    weighted_win = 0.0
    pf_values = []
    total_final_capital = 0.0

    for r in results:
        m = r["metrics"]
        trades = m.get("total_trades", 0)
        total_final_capital += m.get("final_capital", per_asset_capital)
        if trades > 0:
            weighted_win += m.get("win_rate", 0) * trades
            pf_values.append(m.get("profit_factor", 0))

    avg_win_rate = weighted_win / total_trades if total_trades > 0 else 0
    avg_profit_factor = sum(pf_values) / len(pf_values) if pf_values else 0

    return {
        "assets_tested": len(results),
        "starting_capital_total": per_asset_capital * len(results),
        "ending_capital_total": total_final_capital,
        "total_pnl": total_final_capital - per_asset_capital * len(results),
        "avg_win_rate": avg_win_rate,
        "avg_profit_factor": avg_profit_factor,
        "total_trades": total_trades,
    }


def render_markdown(payload: Dict) -> str:
    """Create a concise Markdown report."""
    portfolio = payload["portfolio"]
    lines = [
        "# Real-Market Backtest Results",
        f"Generated (UTC): {payload['generated_at_utc']}",
        "",
        "## Portfolio",
        f"- Assets tested: {portfolio.get('assets_tested', 0)}",
        f"- Total trades: {portfolio.get('total_trades', 0)}",
        f"- Starting capital (total): ${portfolio.get('starting_capital_total', 0):,.2f}",
        f"- Ending capital (total):   ${portfolio.get('ending_capital_total', 0):,.2f}",
        f"- Total P&L:                ${portfolio.get('total_pnl', 0):+,.2f}",
        f"- Avg win rate (weighted):  {portfolio.get('avg_win_rate', 0):.2f}%",
        f"- Avg profit factor:        {portfolio.get('avg_profit_factor', 0):.2f}",
        "",
        "## Per-Asset Metrics",
        "| Asset | Trades | Win% | PF | Final Cap | Max DD% |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for r in payload["assets"]:
        m = r["metrics"]
        lines.append(
            f"| {r['asset']} | {m.get('total_trades', 0)} | "
            f"{m.get('win_rate', 0):.1f}% | {m.get('profit_factor', 0):.2f} | "
            f"${m.get('final_capital', 0):,.2f} | {m.get('max_drawdown_pct', 0):.2f}% |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Real-market multi-asset backtest harness")
    parser.add_argument("--bars", type=int, default=None, help="Override bars per asset (default: asset config)")
    parser.add_argument("--interval", type=str, default=None, help="Override interval per asset (default: asset config)")
    parser.add_argument("--capital", type=float, default=500, help="Starting capital per asset")
    parser.add_argument("--risk", type=float, default=0.01, help="Risk per trade (e.g., 0.01 = 1%%)")
    parser.add_argument(
        "--output-json",
        type=str,
        default=os.path.join("backtests", "real_market_backtest_results.json"),
        help="Path to save JSON results",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default=os.path.join("backtests", "real_market_backtest_results.md"),
        help="Path to save Markdown summary",
    )
    parser.add_argument("--verbose", action="store_true", help="Print per-asset engine output")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)

    client = TradingViewDataClient()
    results: List[Dict] = []

    print("🚀 Starting real-market backtests...")
    for asset in ASSETS:
        res = run_asset_backtest(asset, args, client)
        if res:
            results.append(res)

    portfolio = build_portfolio_summary(results, args.capital)

    payload = {
        "generated_at_utc": datetime.utcnow().isoformat(),
        "settings": {
            "bars_override": args.bars,
            "interval_override": args.interval,
            "capital_per_asset": args.capital,
            "risk_per_trade": args.risk,
        },
        "portfolio": portfolio,
        "assets": results,
    }

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(render_markdown(payload))

    print(f"✅ Saved JSON results to {args.output_json}")
    print(f"✅ Saved Markdown summary to {args.output_md}")
    print(f"Assets tested: {portfolio.get('assets_tested', 0)}")
    print(f"Total trades:  {portfolio.get('total_trades', 0)}")
    print(f"Total P&L:     ${portfolio.get('total_pnl', 0):+,.2f}")


if __name__ == "__main__":
    main()


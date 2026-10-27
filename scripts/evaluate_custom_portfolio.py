#!/usr/bin/env python3
"""Evaluate a custom agent-generated ETF strategy on `data/market_sandbox/`.

Automatically appends every test run to `logs/sandbox_trial_ledger.jsonl` so that
multiple-testing deflation (Deflated Sharpe Ratio, DSR) is tracked honestly as your
agent iterates on strategies for the $1,000 Post-Cutoff Live Duel.

Usage:
    # Evaluate a time-series weights CSV (dates x tickers) or a static portfolio JSON:
    python scripts/evaluate_custom_portfolio.py --portfolio submission/portfolio_submission_template.json
    python scripts/evaluate_custom_portfolio.py --weights-csv cases/case_06_clean_sector_momentum/target_weights.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from quantit_audit import (
    cost_sensitivity_curve,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    matched_null_benchmark,
    run_weights_backtest,
)

SANDBOX_DIR = REPO_ROOT / "data" / "market_sandbox"
LEDGER_PATH = REPO_ROOT / "logs" / "sandbox_trial_ledger.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate custom portfolio weights on the US ETF Market Sandbox.")
    parser.add_argument("--portfolio", type=Path, help="Path to a static portfolio_submission.json file.")
    parser.add_argument("--weights-csv", type=Path, help="Path to a dynamic target_weights.csv (dates x tickers).")
    parser.add_argument("--label", default="agent_sandbox_candidate", help="Label recorded in the trial ledger.")
    parser.add_argument("--start-date", default="2018-01-02", help="Evaluation start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", default="2026-06-30", help="Evaluation end date (YYYY-MM-DD).")
    args = parser.parse_args()

    if not args.portfolio and not args.weights_csv:
        parser.error("Provide either --portfolio <json> or --weights-csv <csv>")

    ret_df = pd.read_csv(
        SANDBOX_DIR / "liquid_etf_daily_returns_2018_2026.csv",
        index_col=0,
        parse_dates=True,
    ).loc[args.start_date : args.end_date]
    macro_df = pd.read_csv(
        SANDBOX_DIR / "macro_and_regime_signals_2018_2026.csv",
        index_col=0,
        parse_dates=True,
    ).loc[ret_df.index]

    if args.portfolio:
        payload = json.loads(args.portfolio.read_text())
        w_dict = payload.get("weights", {})
        w_df = pd.DataFrame(0.0, index=ret_df.index, columns=ret_df.columns)
        for tkr, val in w_dict.items():
            if tkr in w_df.columns:
                w_df[tkr] = float(val)
        n_held = max(1, len(w_dict))
        rebal_days = 21
    else:
        raw_w = pd.read_csv(args.weights_csv, index_col=0, parse_dates=True)
        # Map sector names if needed or align directly to ETF tickers
        sector_map_path = REPO_ROOT / "cases" / "case_06_clean_sector_momentum" / "sector_etf_mapping.json"
        if sector_map_path.is_file():
            smap = json.loads(sector_map_path.read_text())
            rename_cols = {k: v["etf"] for k, v in smap.items() if k in raw_w.columns}
            raw_w = raw_w.rename(columns=rename_cols)
        w_df = pd.DataFrame(0.0, index=ret_df.index, columns=ret_df.columns)
        for col in raw_w.columns:
            if col in w_df.columns:
                w_df[col] = raw_w[col].reindex(ret_df.index).ffill().fillna(0.0)
        n_held = max(1, int(round((w_df > 0.001).sum(axis=1).median())))
        rebal_days = 5

    res_10 = run_weights_backtest(w_df, ret_df, cost_bps=10.0, lag=1)
    curve = cost_sensitivity_curve(w_df, ret_df, bps_grid=(0.0, 5.0, 10.0, 15.0, 20.0))

    # Append to sandbox trial ledger so multiplicity is tracked automatically
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing_trials = 0
    if LEDGER_PATH.is_file():
        existing_trials = len([ln for ln in LEDGER_PATH.read_text().splitlines() if ln.strip()])
    n_trials = existing_trials + 1

    entry = {
        "trial_id": n_trials,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "label": args.label,
        "n_obs": res_10.n_obs,
        "net_sharpe_10bps": round(res_10.sharpe, 4),
        "ann_return": round(res_10.ann_return, 4),
        "max_drawdown": round(res_10.max_drawdown, 4),
        "ann_turnover": round(res_10.ann_turnover, 2),
    }
    with LEDGER_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    dsr = deflated_sharpe_ratio(
        res_10.sharpe,
        n_trials=n_trials,
        n_obs=res_10.n_obs,
        skew=res_10.skew,
        kurtosis=res_10.kurtosis,
    )
    exp_null_sr = expected_max_sharpe(max(1, n_trials), res_10.n_obs)

    # Slice performance by CALM vs STRESS market regime
    pos = w_df.shift(1).fillna(0.0)
    to = pos.diff().abs().sum(axis=1).fillna(0.0)
    net_series = (pos * ret_df).sum(axis=1) - (10.0 / 10000.0) * to
    stress_mask = macro_df["regime_state"] == "STRESS"
    stress_ret = net_series.loc[stress_mask]
    spy_stress = ret_df["SPY"].loc[stress_mask]

    null_bench = matched_null_benchmark(
        ret_df.drop(columns=["SHY", "IEF", "TLT", "GLD", "LQD"], errors="ignore"),
        n_held=min(n_held, 8),
        rebalance_every_n_days=rebal_days,
        cost_bps=10.0,
    )

    report = {
        "label": args.label,
        "sandbox_window": f"{ret_df.index[0].date()} to {ret_df.index[-1].date()}",
        "net_10bps_summary": res_10.summary_dict(),
        "multiplicity_audit": {
            "cumulative_sandbox_trials_logged": n_trials,
            "expected_max_null_sharpe": round(exp_null_sr, 4),
            "deflated_sharpe_ratio": round(dsr, 4),
        },
        "stress_regime_audit": {
            "n_stress_days": int(stress_mask.sum()),
            "strategy_mean_daily_stress_return": round(float(stress_ret.mean()), 5),
            "spy_mean_daily_stress_return": round(float(spy_stress.mean()), 5),
            "worst_stress_day_return": round(float(stress_ret.min()), 4),
        },
        "cost_sensitivity_table": curve.to_dict(orient="records"),
        "matched_null_random_basket_benchmark": null_bench,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

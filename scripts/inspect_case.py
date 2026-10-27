#!/usr/bin/env python3
"""CLI diagnostic runner for the 6 candidate cases in the Quantit x NYU Stern Hackathon.

Students and Pi agents can call this directly from the terminal or wrap it inside
`.pi/extensions/` to inspect backtest assumptions, transaction-cost curves,
multiple-testing logs, regime correlation spikes, and survivorship gaps.

Usage:
    python scripts/inspect_case.py --case case_02_the_cost_cliff
    python scripts/inspect_case.py --all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from quantit_audit import (
    benjamini_hochberg,
    cost_sensitivity_curve,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    matched_null_benchmark,
    regime_correlation_audit,
    run_weights_backtest,
    sharpe_pvalue,
    signals_to_weights,
)

CASES_DIR = REPO_ROOT / "cases"


def inspect_case_01(cdir: Path) -> dict:
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    sig_prop = pd.read_csv(cdir / "proposer_signal_panel.csv", index_col=0, parse_dates=True)
    sig_pit = pd.read_csv(cdir / "pit_aligned_signal_panel.csv", index_col=0, parse_dates=True)
    filings = json.loads((cdir / "filings_and_quotes.json").read_text())

    w_prop = signals_to_weights(sig_prop, long_only=False)
    w_pit = signals_to_weights(sig_pit, long_only=False)

    res_prop = run_weights_backtest(w_prop, ret, cost_bps=10.0, lag=1)
    res_pit = run_weights_backtest(w_pit, ret, cost_bps=10.0, lag=1)

    lags = [f["filing_lag_calendar_days"] for f in filings]
    return {
        "case_id": cdir.name,
        "n_filing_excerpts": len(filings),
        "median_filing_lag_calendar_days": float(pd.Series(lags).median()),
        "proposer_claimed_backtest": res_prop.summary_dict(),
        "pit_and_entity_masked_control": res_pit.summary_dict(),
    }


def inspect_case_02(cdir: Path) -> dict:
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    sig = pd.read_csv(cdir / "signal_panel.csv", index_col=0, parse_dates=True)
    w = signals_to_weights(sig, long_only=False)
    curve = cost_sensitivity_curve(w, ret, bps_grid=(0.0, 2.0, 5.0, 10.0, 15.0, 20.0))
    return {
        "case_id": cdir.name,
        "cost_sensitivity_table": curve.to_dict(orient="records"),
    }


def inspect_case_03(cdir: Path) -> dict:
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    sig = pd.read_csv(cdir / "winning_signal.csv", index_col=0, parse_dates=True)
    w = signals_to_weights(sig, long_only=False)
    res = run_weights_backtest(w, ret, cost_bps=10.0, lag=1)

    ledger_path = cdir / "logs" / "experiment_ledger.jsonl"
    trials = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
    n_trials = len(trials)
    pvals = pd.Series({t["candidate_name"]: t["naive_pvalue"] for t in trials})
    bh_passed = int(benjamini_hochberg(pvals, alpha=0.05).sum())

    exp_max_null = expected_max_sharpe(n_trials, res.n_obs)
    dsr = deflated_sharpe_ratio(
        res.sharpe,
        n_trials=n_trials,
        n_obs=res.n_obs,
        skew=res.skew,
        kurtosis=res.kurtosis,
    )
    return {
        "case_id": cdir.name,
        "winner_single_trial_backtest": res.summary_dict(),
        "naive_single_test_pvalue": round(sharpe_pvalue(res.sharpe, res.n_obs), 5),
        "n_trials_in_ledger": n_trials,
        "expected_max_null_sharpe": round(exp_max_null, 3),
        "deflated_sharpe_ratio": round(dsr, 4),
        "bh_fdr_05_rejections": bh_passed,
    }


def inspect_case_04(cdir: Path) -> dict:
    sleeves = pd.read_csv(cdir / "sleeve_returns.csv", index_col=0, parse_dates=True)
    reg = pd.read_csv(cdir / "market_regime.csv", index_col=0, parse_dates=True)
    audit = regime_correlation_audit(sleeves, reg["regime_label"])
    return {
        "case_id": cdir.name,
        "regime_audit": audit,
    }


def inspect_case_05(cdir: Path) -> dict:
    surv_ret = pd.read_csv(cdir / "survivor_panel_returns.csv", index_col=0, parse_dates=True)
    sig_surv = pd.read_csv(cdir / "signal_panel.csv", index_col=0, parse_dates=True)
    w_surv = signals_to_weights(sig_surv, long_only=True)
    res_surv = run_weights_backtest(w_surv, surv_ret, cost_bps=10.0, lag=1)

    full_ret = pd.read_csv(cdir / "point_in_time_full_returns.csv", index_col=0, parse_dates=True)
    roll_20 = (1.0 + full_ret.fillna(0.0)).rolling(20).apply(lambda x: x.prod(), raw=True) - 1.0
    sig_full = ((-roll_20).clip(lower=0.0)).where(full_ret.notna(), 0.0)
    w_full = signals_to_weights(sig_full, long_only=True)
    res_full = run_weights_backtest(w_full, full_ret.fillna(0.0), cost_bps=10.0, lag=1)

    delist_df = pd.read_csv(cdir / "delisting_cohort_audit.csv")
    return {
        "case_id": cdir.name,
        "n_survivors_in_proposer_panel": surv_ret.shape[1],
        "n_delisted_omitted": len(delist_df),
        "survivor_only_backtest": res_surv.summary_dict(),
        "point_in_time_full_cohort_backtest": res_full.summary_dict(),
    }


def inspect_case_06(cdir: Path) -> dict:
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    w = pd.read_csv(cdir / "target_weights.csv", index_col=0, parse_dates=True)
    curve = cost_sensitivity_curve(w, ret, bps_grid=(0.0, 5.0, 10.0, 15.0, 20.0))
    res_10 = run_weights_backtest(w, ret, cost_bps=10.0, lag=1)

    ledger_path = cdir / "logs" / "experiment_ledger.jsonl"
    trials = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
    dsr = deflated_sharpe_ratio(
        res_10.sharpe,
        n_trials=len(trials),
        n_obs=res_10.n_obs,
        skew=res_10.skew,
        kurtosis=res_10.kurtosis,
    )
    null_bench = matched_null_benchmark(ret, n_held=4, rebalance_every_n_days=5, cost_bps=10.0)
    return {
        "case_id": cdir.name,
        "net_10bps_backtest": res_10.summary_dict(),
        "n_trials_in_ledger": len(trials),
        "deflated_sharpe_ratio": round(dsr, 4),
        "cost_sensitivity_table": curve.to_dict(orient="records"),
        "matched_null_random_basket_benchmark": null_bench,
    }


DISPATCH = {
    "case_01_filing_lag_mirage": inspect_case_01,
    "case_02_the_cost_cliff": inspect_case_02,
    "case_03_twenty_tries": inspect_case_03,
    "case_04_regime_correlation_spike": inspect_case_04,
    "case_05_survivorship_trap": inspect_case_05,
    "case_06_clean_sector_momentum": inspect_case_06,
}


def main():
    parser = argparse.ArgumentParser(description="Run quantitative diagnostics on Hackathon candidate cases.")
    parser.add_argument("--case", choices=sorted(DISPATCH.keys()), help="Specific case folder to inspect.")
    parser.add_argument("--all", action="store_true", help="Inspect all 6 candidate cases.")
    args = parser.parse_args()

    if not args.case and not args.all:
        parser.error("Provide --case <case_id> or --all")

    targets = sorted(DISPATCH.keys()) if args.all else [args.case]
    output = {}
    for cid in targets:
        output[cid] = DISPATCH[cid](CASES_DIR / cid)

    print(json.dumps(output if args.all else output[targets[0]], indent=2))


if __name__ == "__main__":
    main()

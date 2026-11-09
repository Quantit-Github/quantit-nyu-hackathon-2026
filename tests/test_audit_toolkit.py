"""Unit and integration tests for the Quantit Audit Toolkit, Guided Cases, Blind Challenges, and Market Sandbox."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from quantit_audit import (
    ALLOWED_LIQUID_TICKERS,
    BLIND_CHALLENGE_CASES,
    REQUIRED_CASES,
    cost_sensitivity_curve,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    run_weights_backtest,
    signals_to_weights,
    validate_audit_verdicts,
    validate_portfolio_submission,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"
CHALLENGES_DIR = REPO_ROOT / "challenges"
SANDBOX_DIR = REPO_ROOT / "data" / "market_sandbox"


def test_lag_guard_rejects_zero_lag():
    dates = pd.bdate_range("2024-01-01", periods=20)
    w = pd.DataFrame({"A": 0.5, "B": 0.5}, index=dates)
    r = pd.DataFrame({"A": 0.01, "B": -0.005}, index=dates)
    with pytest.raises(ValueError, match="lag must be >= 1"):
        run_weights_backtest(w, r, lag=0)


def test_multiple_testing_deflation_monotone():
    sr_obs = 1.60
    n_obs = 504
    e1 = expected_max_sharpe(1, n_obs)
    e10 = expected_max_sharpe(10, n_obs)
    e80 = expected_max_sharpe(80, n_obs)
    assert 0.0 == e1 < e10 < e80

    dsr_3 = deflated_sharpe_ratio(sr_obs, n_trials=3, n_obs=n_obs)
    dsr_80 = deflated_sharpe_ratio(sr_obs, n_trials=80, n_obs=n_obs)
    assert dsr_3 > 0.90
    assert dsr_80 < 0.50


def test_all_guided_and_blind_cases_and_sandbox_exist():
    for cid in REQUIRED_CASES:
        cdir = CASES_DIR / cid
        assert cdir.is_dir(), f"Missing guided case {cid}"
        assert (cdir / "proposal.md").is_file()
        assert (cdir / "metadata.json").is_file()

    for bid in BLIND_CHALLENGE_CASES:
        bdir = CHALLENGES_DIR / bid
        assert bdir.is_dir(), f"Missing blind challenge {bid}"
        assert (bdir / "proposal.md").is_file()

    assert (SANDBOX_DIR / "liquid_etf_daily_returns_2018_2026.csv").is_file()
    assert (SANDBOX_DIR / "macro_and_regime_signals_2018_2026.csv").is_file()


def test_case_02_cost_cliff_flips_sign():
    cdir = CASES_DIR / "case_02_the_cost_cliff"
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    sig = pd.read_csv(cdir / "signal_panel.csv", index_col=0, parse_dates=True)
    w = signals_to_weights(sig, long_only=False)
    curve = cost_sensitivity_curve(w, ret, bps_grid=(0.0, 10.0, 15.0))
    sr_0 = float(curve.loc[curve["cost_bps"] == 0.0, "sharpe"].iloc[0])
    sr_10 = float(curve.loc[curve["cost_bps"] == 10.0, "sharpe"].iloc[0])
    assert sr_0 > 2.0
    assert sr_10 < -1.0


def test_case_06_clean_control_passes_gates():
    cdir = CASES_DIR / "case_06_clean_sector_momentum"
    ret = pd.read_csv(cdir / "returns_panel.csv", index_col=0, parse_dates=True)
    w = pd.read_csv(cdir / "target_weights.csv", index_col=0, parse_dates=True)
    res = run_weights_backtest(w, ret, cost_bps=10.0, lag=1)
    assert res.sharpe > 1.0
    assert res.ann_turnover < 25.0
    dsr = deflated_sharpe_ratio(res.sharpe, n_trials=3, n_obs=res.n_obs, skew=res.skew, kurtosis=res.kurtosis)
    assert dsr > 0.95


def test_validators_catch_templates_and_pass_valid():
    v_tmpl = REPO_ROOT / "submission" / "audit_verdicts_template.json"
    v_errs = validate_audit_verdicts(v_tmpl)
    assert any("team_name" in e for e in v_errs)
    assert any("All 6 cases were marked `PASS`" in e for e in v_errs)
    assert any("blind_01_earnings_tone_drift.decision" in e for e in v_errs)

    valid_verdicts = json.loads(v_tmpl.read_text())
    valid_verdicts["team_name"] = "Stern Alpha Critics"
    for cid in REQUIRED_CASES:
        valid_verdicts["case_verdicts"][cid]["decision"] = (
            "FUND" if cid == "case_06_clean_sector_momentum" else "PASS"
        )
        valid_verdicts["case_verdicts"][cid]["primary_finding"] = (
            f"Audited {cid} with quantitative falsification checks and verified lag, cost, and multiplicity."
        )
    for bid in BLIND_CHALLENGE_CASES:
        valid_verdicts["blind_challenge_verdicts"][bid]["decision"] = (
            "FUND" if bid == "blind_04_defensive_sector_shield" else "PASS"
        )
        valid_verdicts["blind_challenge_verdicts"][bid]["primary_finding"] = (
            f"Audited {bid} and verified lag alignment, cost curve, and trial multiplicity."
        )
    assert validate_audit_verdicts(valid_verdicts) == []

    tmpl_path = REPO_ROOT / "submission" / "portfolio_submission_template.json"
    errs = validate_portfolio_submission(tmpl_path)
    assert any("team_name" in e for e in errs)

    valid_payload = json.loads(tmpl_path.read_text())
    valid_payload["team_name"] = "Stern Alpha Critics"
    valid_payload["thesis_and_edge_summary"] = (
        "Weekly top-4 sector rotation passed N=3 DSR (0.996), 15 bps cost stress, and 99th percentile matched-null check."
    )
    assert validate_portfolio_submission(valid_payload) == []


def test_zero_turnover_breakeven_is_null_and_valid_json():
    dates = pd.bdate_range("2024-01-01", periods=30)
    w = pd.DataFrame({"SPY": 0.6, "TLT": 0.4}, index=dates)
    r = pd.DataFrame(
        {
            "SPY": [0.002 if i % 2 == 0 else -0.001 for i in range(30)],
            "TLT": [-0.0005 if i % 3 == 0 else 0.001 for i in range(30)],
        },
        index=dates,
    )
    res = run_weights_backtest(w, r, cost_bps=10.0, lag=1)
    assert res.breakeven_bps is None
    assert res.summary_dict()["breakeven_bps"] is None
    curve = cost_sensitivity_curve(w, r, bps_grid=(0.0, 10.0))
    records = curve.where(pd.notna(curve), None).to_dict(orient="records")
    # Strict JSON check (disallows Infinity / NaN)
    serialized = json.dumps({"summary": res.summary_dict(), "curve": records}, allow_nan=False)
    parsed = json.loads(serialized)
    assert parsed["summary"]["breakeven_bps"] is None
    assert all(row["breakeven_bps"] is None for row in parsed["curve"])


def test_allowed_liquid_tickers_all_exist_in_sandbox():
    sandbox_csv = SANDBOX_DIR / "multi_asset_universe_130_returns_2018_2026.csv"
    cols = set(pd.read_csv(sandbox_csv, nrows=2, index_col=0).columns)
    missing = ALLOWED_LIQUID_TICKERS - cols
    assert missing == set(), f"Allowed tickers missing from sandbox data: {sorted(missing)}"

    meta = json.loads((SANDBOX_DIR / "sandbox_universe_metadata.json").read_text())
    meta_tickers = {c["ticker"] for c in meta["constituents"]}
    eligible_tickers = {c["ticker"] for c in meta["constituents"] if c["eligible_for_live_1000_duel"]}
    assert meta_tickers == cols
    assert eligible_tickers == ALLOWED_LIQUID_TICKERS


def test_case_and_challenge_backtest_scripts_run_from_repo_root():
    scripts = [
        CASES_DIR / "case_02_the_cost_cliff" / "proposer_backtest.py",
        CHALLENGES_DIR / "blind_01_earnings_tone_drift" / "strategy_backtest.py",
        CHALLENGES_DIR / "blind_02_sector_momentum_noisy" / "strategy_backtest.py",
    ]
    for script in scripts:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, f"{script} failed from REPO_ROOT: {proc.stderr}"


def test_evaluate_custom_portfolio_matches_case_06_and_blind_04():
    ledger_path = REPO_ROOT / "logs" / "sandbox_trial_ledger.jsonl"
    prior_ledger = ledger_path.read_text() if ledger_path.is_file() else None
    try:
        for rel_csv, min_sr in [
            ("cases/case_06_clean_sector_momentum/target_weights.csv", 1.20),
            ("challenges/blind_04_defensive_sector_shield/target_weights.csv", 1.20),
        ]:
            proc = subprocess.run(
                [sys.executable, "scripts/evaluate_custom_portfolio.py", "--weights-csv", rel_csv],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            assert proc.returncode == 0, f"evaluate_custom_portfolio failed on {rel_csv}: {proc.stderr}"
            assert proc.stderr == "", f"Unexpected warning on {rel_csv}: {proc.stderr}"
            payload = json.loads(proc.stdout)
            assert payload["net_10bps_summary"]["sharpe"] >= min_sr
            assert payload["multiplicity_audit"]["deflated_sharpe_ratio"] > 0.99
    finally:
        if prior_ledger is None:
            if ledger_path.is_file():
                ledger_path.unlink()
            if ledger_path.parent.is_dir() and not any(ledger_path.parent.iterdir()):
                ledger_path.parent.rmdir()
        else:
            ledger_path.write_text(prior_ledger)




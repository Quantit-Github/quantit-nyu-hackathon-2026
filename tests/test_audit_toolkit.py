"""Unit and integration tests for the Quantit Audit Toolkit, Guided Cases, Blind Challenges, and Market Sandbox."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from quantit_audit import (
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

    tmpl_path = REPO_ROOT / "submission" / "portfolio_submission_template.json"
    errs = validate_portfolio_submission(tmpl_path)
    assert any("team_name" in e for e in errs)

    valid_payload = json.loads(tmpl_path.read_text())
    valid_payload["team_name"] = "Stern Alpha Critics"
    valid_payload["thesis_and_edge_summary"] = (
        "Weekly top-4 sector rotation passed N=3 DSR (0.996), 15 bps cost stress, and 99th percentile matched-null check."
    )
    assert validate_portfolio_submission(valid_payload) == []

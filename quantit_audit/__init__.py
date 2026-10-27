"""Quantit Audit Toolkit — Falsification & Verification Primitives for Finance Agents.

Used in the Quantit x NYU Stern Finance Agent Hackathon (TECH-UB 41, Nov 2026).
"""

from quantit_audit.backtest import (
    BacktestResult,
    cost_sensitivity_curve,
    matched_null_benchmark,
    regime_correlation_audit,
    run_weights_backtest,
    signals_to_weights,
)
from quantit_audit.statistics import (
    benjamini_hochberg,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    sharpe_pvalue,
)
from quantit_audit.validator import (
    ALLOWED_LIQUID_TICKERS,
    validate_ic_verdicts,
    validate_portfolio_submission,
)

__all__ = [
    "ALLOWED_LIQUID_TICKERS",
    "BacktestResult",
    "benjamini_hochberg",
    "cost_sensitivity_curve",
    "deflated_sharpe_ratio",
    "expected_max_sharpe",
    "matched_null_benchmark",
    "regime_correlation_audit",
    "run_weights_backtest",
    "sharpe_pvalue",
    "signals_to_weights",
    "validate_ic_verdicts",
    "validate_portfolio_submission",
]

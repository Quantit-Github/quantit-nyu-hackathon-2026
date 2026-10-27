"""Validators for Strategy Audit verdicts and the $1,000 Post-Cutoff Live Duel portfolio."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_CASES = (
    "case_01_filing_lag_mirage",
    "case_02_the_cost_cliff",
    "case_03_twenty_tries",
    "case_04_regime_correlation_spike",
    "case_05_survivorship_trap",
    "case_06_clean_sector_momentum",
)

BLIND_CHALLENGE_CASES = (
    "blind_01_earnings_tone_drift",
    "blind_02_sector_momentum_noisy",
    "blind_03_factor_grid_winner",
    "blind_04_defensive_sector_shield",
)

VALID_CALLS = ("FUND", "PILOT", "PASS")

ALLOWED_LIQUID_TICKERS = {
    # SPDR & iShares US Sector / Factor / Broad ETFs
    "SPY", "QQQ", "IWM", "DIA", "VTI",
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB", "XLC", "XLRE",
    "IYC", "IYR", "SMH", "IBB", "XBI", "KRE", "XOP", "GDX",
    "MTUM", "QUAL", "VLUE", "USMV", "SIZE",
    "TLT", "IEF", "SHY", "SGOV", "BIL", "LQD", "HYG", "GLD", "SLV", "DBC",
    # Liquid Large-Cap US Equities (from Case 01 / S&P 100 core)
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "ORCL", "CRM", "AMD",
    "NFLX", "INTC", "TXN", "JPM", "BAC", "WFC", "GS", "MS", "BLK", "AXP", "XOM",
    "CVX", "COP", "SLB", "EOG", "JNJ", "UNH", "LLY", "PFE", "ABBV", "TMO", "PG",
    "KO", "PEP", "WMT", "COST", "MCD", "NKE", "DIS", "PYPL", "CAT", "HON", "UNP",
    "GE", "BA", "NEE", "DUK",
}


def validate_audit_verdicts(payload: dict | Path) -> list[str]:
    """Validate `submission/audit_verdicts.json` structure and evidence fields.

    Returns a list of error strings (empty list == VALID).
    """
    if isinstance(payload, Path):
        payload = json.loads(payload.read_text())

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Root JSON must be an object."]

    if not payload.get("team_name") or payload.get("team_name") == "REPLACE_WITH_TEAM_NAME":
        errors.append("`team_name` must be set to your actual team name.")

    verdicts = payload.get("case_verdicts")
    if not isinstance(verdicts, dict):
        errors.append("`case_verdicts` must be a dictionary mapping case_id -> verdict object.")
        return errors

    for cid in REQUIRED_CASES:
        if cid not in verdicts:
            errors.append(f"Missing verdict entry for `{cid}`.")
            continue
        entry = verdicts[cid]
        call = entry.get("decision")
        if call not in VALID_CALLS:
            errors.append(f"`{cid}.decision` must be one of {VALID_CALLS}, got {call!r}.")
        defect = str(entry.get("primary_finding", "")).strip()
        if len(defect) < 15 or "TODO" in defect.upper():
            errors.append(f"`{cid}.primary_finding` must provide a concrete finding (>=15 chars, no TODO).")
        metric = entry.get("key_metric_evidence")
        if not isinstance(metric, dict) or len(metric) == 0:
            errors.append(f"`{cid}.key_metric_evidence` must be a non-empty dict of quantitative evidence.")

    # Epistemic sanity check: if all 6 cases have the exact same decision, warn that at least 1 control differs
    decisions = [verdicts.get(c, {}).get("decision") for c in REQUIRED_CASES if c in verdicts]
    if len(decisions) == 6 and len(set(decisions)) == 1:
        errors.append(
            f"All 6 cases were marked `{decisions[0]}` — remember the pack contains both planted traps AND at least one sound control."
        )

    # Validate blind_challenge_verdicts if provided and populated
    blind_verdicts = payload.get("blind_challenge_verdicts")
    if isinstance(blind_verdicts, dict):
        for bid, bentry in blind_verdicts.items():
            if bid not in BLIND_CHALLENGE_CASES:
                errors.append(f"Unknown blind challenge id `{bid}` (expected one of {BLIND_CHALLENGE_CASES}).")
                continue
            bcall = bentry.get("decision")
            if bcall not in VALID_CALLS:
                errors.append(f"`{bid}.decision` must be one of {VALID_CALLS}, got {bcall!r}.")

    return errors


def validate_portfolio_submission(payload: dict | Path) -> list[str]:
    """Validate `submission/portfolio_submission.json` for the $1,000 Post-Cutoff Live Duel.

    Rules for the Nov 18 – Dec 18, 2026 live $1,000 run:
    - Long-only weights in [0.0, 0.40] per ticker.
    - Total weights must sum to 1.00 (within +/- 0.005).
    - Minimum 3 distinct tickers, maximum 12 tickers.
    - All tickers must be liquid US-listed ETFs or large-cap equities (`ALLOWED_LIQUID_TICKERS`).
    - Must specify `benchmark_ticker` (default `SPY`) and `kill_switch_max_drawdown` in `[-0.25, -0.03]`.
    """
    if isinstance(payload, Path):
        payload = json.loads(payload.read_text())

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["Root JSON must be an object."]

    if not payload.get("team_name") or payload.get("team_name") == "REPLACE_WITH_TEAM_NAME":
        errors.append("`team_name` must be set to your actual team name.")

    weights = payload.get("weights")
    if not isinstance(weights, dict) or len(weights) == 0:
        errors.append("`weights` must be a non-empty dictionary mapping ticker -> weight.")
        return errors

    if not 3 <= len(weights) <= 12:
        errors.append(f"Portfolio must hold between 3 and 12 tickers (got {len(weights)}).")

    total_w = 0.0
    for tkr, w in weights.items():
        if tkr not in ALLOWED_LIQUID_TICKERS:
            errors.append(
                f"Ticker `{tkr}` is not in ALLOWED_LIQUID_TICKERS (use liquid US ETFs or S&P 100 equities)."
            )
        if not isinstance(w, (int, float)) or w <= 0.0:
            errors.append(f"Weight for `{tkr}` must be strictly positive (long-only), got {w!r}.")
            continue
        if w > 0.4001:
            errors.append(f"Weight for `{tkr}` ({w:.2%}) exceeds the 40% single-asset concentration cap.")
        total_w += float(w)

    if abs(total_w - 1.0) > 0.005:
        errors.append(f"Weights must sum to 1.000 (got {total_w:.4f}).")

    kill_dd = payload.get("kill_switch_max_drawdown")
    if not isinstance(kill_dd, (int, float)) or not (-0.25 <= float(kill_dd) <= -0.03):
        errors.append(
            f"`kill_switch_max_drawdown` must be a negative decimal between -0.25 and -0.03 (got {kill_dd!r})."
        )

    rationale = str(payload.get("thesis_and_edge_summary", "")).strip()
    if len(rationale) < 20 or "TODO" in rationale.upper():
        errors.append("`thesis_and_edge_summary` must state why this portfolio should be funded (>=20 chars).")

    return errors

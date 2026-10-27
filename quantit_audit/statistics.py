"""Statistical falsification & multiple-testing corrections (Bailey & Lopez de Prado 2014; BH 1995)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def sharpe_pvalue(sharpe: float, n_obs: int, periods_per_year: int = 252) -> float:
    """Two-sided naive p-value for an annualized Sharpe ratio under H0: SR = 0 (single trial)."""
    if n_obs < 2:
        raise ValueError("n_obs must be at least 2")
    if not np.isfinite(sharpe):
        return float("nan")
    per_period = sharpe / np.sqrt(periods_per_year)
    t_stat = per_period * np.sqrt(n_obs)
    return float(2.0 * stats.norm.sf(abs(t_stat)))


def expected_max_sharpe(n_trials: int, n_obs: int, periods_per_year: int = 252) -> float:
    """Expected maximum annualized Sharpe ratio across `n_trials` independent pure-null strategies."""
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if n_obs < 2:
        raise ValueError("n_obs must be >= 2")
    if n_trials == 1:
        return 0.0

    euler_mascheroni = 0.5772156649015329
    q = (1.0 - euler_mascheroni) * stats.norm.ppf(1.0 - 1.0 / n_trials) + (
        euler_mascheroni * stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e))
    )
    return float((q / np.sqrt(n_obs)) * np.sqrt(periods_per_year))


def deflated_sharpe_ratio(
    sharpe: float,
    n_trials: int,
    n_obs: int,
    *,
    skew: float = 0.0,
    kurtosis: float = 3.0,
    periods_per_year: int = 252,
) -> float:
    """Probability that an observed Sharpe ratio exceeds the multiple-testing null benchmark.

    Conventionally a candidate passes multiple-testing scrutiny only if DSR >= 0.95.
    """
    if not np.isfinite(sharpe):
        return float("nan")
    if n_obs < 2:
        raise ValueError("n_obs must be >= 2")

    sr0_ann = expected_max_sharpe(n_trials, n_obs, periods_per_year)
    sr = sharpe / np.sqrt(periods_per_year)
    sr0 = sr0_ann / np.sqrt(periods_per_year)

    var = (1.0 - skew * sr + ((kurtosis - 1.0) / 4.0) * (sr**2)) / (n_obs - 1)
    if var <= 0:
        return float("nan")
    return float(stats.norm.cdf((sr - sr0) / np.sqrt(var)))


def benjamini_hochberg(pvalues: pd.Series, alpha: float = 0.05) -> pd.Series:
    """Benjamini-Hochberg step-up false-discovery-rate (FDR) control at level `alpha`."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    rejected = pd.Series(False, index=pvalues.index)
    usable = pvalues.dropna()
    if usable.empty:
        return rejected

    ordered = usable.sort_values()
    m = len(ordered)
    thresholds = alpha * np.arange(1, m + 1) / m
    passing = ordered.to_numpy() <= thresholds
    if not passing.any():
        return rejected

    cutoff = int(np.max(np.flatnonzero(passing)))
    rejected.loc[ordered.index[: cutoff + 1]] = True
    return rejected

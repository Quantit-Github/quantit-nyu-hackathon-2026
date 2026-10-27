"""Backtest, cost-cliff, regime-correlation, and matched-null verification primitives.

Core invariants:
1. A signal or target weight observed at date `t` can only earn returns at `t + lag`
   (default `lag = 1`). Setting `lag = 0` introduces look-ahead bias.
2. Two-sided portfolio turnover on day `t` is `sum_i |pos_{t,i} - pos_{t-1,i}|`
   (never `|sum_i pos_{t,i} - sum_i pos_{t-1,i}|`, which is identically zero for
   constant-leverage or dollar-neutral books).
3. Every strategy claim should be compared against both a transaction-cost curve
   and a same-count random basket control (`matched_null_benchmark`).
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class BacktestResult:
    n_obs: int
    ann_return: float
    ann_vol: float
    sharpe: float
    max_drawdown: float
    ann_turnover: float
    breakeven_bps: float
    skew: float
    kurtosis: float
    daily_returns: pd.Series
    daily_turnover: pd.Series

    def summary_dict(self) -> dict:
        return {
            "n_obs": self.n_obs,
            "ann_return": round(self.ann_return, 4),
            "ann_vol": round(self.ann_vol, 4),
            "sharpe": round(self.sharpe, 3),
            "max_drawdown": round(self.max_drawdown, 4),
            "ann_turnover": round(self.ann_turnover, 2),
            "breakeven_bps": round(self.breakeven_bps, 2),
            "skew": round(self.skew, 3),
            "kurtosis": round(self.kurtosis, 3),
        }


def signals_to_weights(
    signal: pd.DataFrame,
    *,
    long_only: bool = False,
    top_k: int | None = None,
    gross_leverage: float = 1.0,
) -> pd.DataFrame:
    """Convert raw cross-sectional signals into portfolio target weights."""
    if top_k is not None:
        ranks = signal.rank(axis=1, ascending=False)
        selected = (ranks <= top_k).astype(float).where(signal.notna(), 0.0)
        denom = selected.sum(axis=1).replace(0.0, np.nan)
        return selected.div(denom, axis=0).fillna(0.0) * gross_leverage

    if long_only:
        pos_sig = signal.clip(lower=0.0).fillna(0.0)
        denom = pos_sig.sum(axis=1).replace(0.0, np.nan)
        return pos_sig.div(denom, axis=0).fillna(0.0) * gross_leverage

    demeaned = signal.sub(signal.mean(axis=1), axis=0).fillna(0.0)
    denom = demeaned.abs().sum(axis=1).replace(0.0, np.nan)
    return demeaned.div(denom, axis=0).fillna(0.0) * gross_leverage


def run_weights_backtest(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    *,
    cost_bps: float = 0.0,
    lag: int = 1,
    periods_per_year: int = 252,
) -> BacktestResult:
    """Evaluate target weights against asset returns with explicit lag and turnover cost."""
    if lag < 1:
        raise ValueError("lag must be >= 1 to prevent look-ahead bias.")

    common_dates = weights.index.intersection(returns.index)
    common_cols = weights.columns.intersection(returns.columns)
    w = weights.loc[common_dates, common_cols].fillna(0.0)
    r = returns.loc[common_dates, common_cols].fillna(0.0)

    positions = w.shift(lag)
    valid_mask = positions.notna().any(axis=1)
    positions = positions.loc[valid_mask]
    r = r.loc[positions.index]

    turnover = positions.diff().abs().sum(axis=1).fillna(0.0)
    gross_ret = (positions * r).sum(axis=1)
    net_ret = gross_ret - (cost_bps / 10000.0) * turnover

    n_obs = len(net_ret)
    ann_ret = float(net_ret.mean() * periods_per_year)
    ann_vol = float(net_ret.std() * np.sqrt(periods_per_year))
    sharpe = ann_ret / ann_vol if ann_vol > 0 else float("nan")

    cum = (1.0 + net_ret).cumprod()
    mdd = float((cum / cum.cummax() - 1.0).min())
    ann_to = float(turnover.mean() * periods_per_year)

    mean_to = float(turnover.mean())
    breakeven = float((gross_ret.mean() / mean_to) * 10000.0) if mean_to > 1e-9 else float("inf")

    return BacktestResult(
        n_obs=n_obs,
        ann_return=ann_ret,
        ann_vol=ann_vol,
        sharpe=sharpe,
        max_drawdown=mdd,
        ann_turnover=ann_to,
        breakeven_bps=breakeven,
        skew=float(stats.skew(net_ret)),
        kurtosis=float(stats.kurtosis(net_ret, fisher=False)),
        daily_returns=net_ret,
        daily_turnover=turnover,
    )


def cost_sensitivity_curve(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    *,
    bps_grid: tuple[float, ...] = (0.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
    lag: int = 1,
) -> pd.DataFrame:
    """Tabulate Net Sharpe and Annualized Return across transaction-cost assumptions."""
    rows = []
    for bps in bps_grid:
        res = run_weights_backtest(weights, returns, cost_bps=bps, lag=lag)
        rows.append(
            {
                "cost_bps": bps,
                "sharpe": round(res.sharpe, 3),
                "ann_return": round(res.ann_return, 4),
                "ann_vol": round(res.ann_vol, 4),
                "max_drawdown": round(res.max_drawdown, 4),
                "ann_turnover": round(res.ann_turnover, 2),
                "breakeven_bps": round(res.breakeven_bps, 2),
            }
        )
    return pd.DataFrame(rows)


def matched_null_benchmark(
    returns: pd.DataFrame,
    *,
    n_held: int = 4,
    rebalance_every_n_days: int = 5,
    cost_bps: float = 10.0,
    n_simulations: int = 250,
    seed: int = 42,
) -> dict:
    """Monte Carlo distribution of Same-Count Random Baskets with identical rebalance cadence."""
    rng = np.random.default_rng(seed)
    dates = returns.index
    n_assets = returns.shape[1]
    if not 1 <= n_held <= n_assets:
        raise ValueError(f"n_held must be in [1, {n_assets}]")

    rebal_dates = dates[::rebalance_every_n_days]
    sim_sharpes = []

    for _ in range(n_simulations):
        w_rebal = np.zeros((len(rebal_dates), n_assets))
        for i in range(len(rebal_dates)):
            chosen = rng.choice(n_assets, size=n_held, replace=False)
            w_rebal[i, chosen] = 1.0 / n_held
        w_df = pd.DataFrame(w_rebal, index=rebal_dates, columns=returns.columns).reindex(dates).ffill().fillna(0.0)
        res = run_weights_backtest(w_df, returns, cost_bps=cost_bps, lag=1)
        sim_sharpes.append(res.sharpe)

    arr = np.array(sim_sharpes)
    return {
        "n_simulations": n_simulations,
        "n_held": n_held,
        "rebalance_every_n_days": rebalance_every_n_days,
        "cost_bps": cost_bps,
        "null_sharpe_mean": round(float(np.mean(arr)), 3),
        "null_sharpe_std": round(float(np.std(arr)), 3),
        "null_sharpe_p50": round(float(np.percentile(arr, 50)), 3),
        "null_sharpe_p95": round(float(np.percentile(arr, 95)), 3),
        "null_sharpe_p99": round(float(np.percentile(arr, 99)), 3),
    }


def regime_correlation_audit(
    sleeve_returns: pd.DataFrame,
    regime_series: pd.Series,
    *,
    calm_label: str = "CALM",
    stress_label: str = "STRESS",
) -> dict:
    """Compare average off-diagonal pairwise correlation and tail metrics across regimes."""
    common = sleeve_returns.index.intersection(regime_series.index)
    s_ret = sleeve_returns.loc[common]
    reg = regime_series.loc[common]

    n_cols = s_ret.shape[1]
    off_diag = ~np.eye(n_cols, dtype=bool)

    calm_sub = s_ret.loc[reg == calm_label]
    stress_sub = s_ret.loc[reg == stress_label]

    calm_corr = float(calm_sub.corr().to_numpy()[off_diag].mean()) if len(calm_sub) > 5 else float("nan")
    stress_corr = float(stress_sub.corr().to_numpy()[off_diag].mean()) if len(stress_sub) > 5 else float("nan")

    ew_port = s_ret.mean(axis=1)
    calm_port = ew_port.loc[reg == calm_label]
    stress_port = ew_port.loc[reg == stress_label]

    sr_calm = float(calm_port.mean() / calm_port.std() * np.sqrt(252)) if len(calm_port) > 5 else float("nan")
    sr_full = float(ew_port.mean() / ew_port.std() * np.sqrt(252))
    cum = (1.0 + ew_port).cumprod()
    mdd = float((cum / cum.cummax() - 1.0).min())

    return {
        "n_calm_days": int(len(calm_sub)),
        "n_stress_days": int(len(stress_sub)),
        "avg_pairwise_corr_calm": round(calm_corr, 3),
        "avg_pairwise_corr_stress": round(stress_corr, 3),
        "correlation_spike_delta": round(stress_corr - calm_corr, 3),
        "equal_weight_sharpe_calm": round(sr_calm, 3),
        "equal_weight_sharpe_full": round(sr_full, 3),
        "equal_weight_max_drawdown": round(mdd, 4),
        "equal_weight_skewness": round(float(stats.skew(ew_port)), 3),
        "worst_stress_day_return": round(float(stress_port.min()), 4) if len(stress_port) else float("nan"),
    }

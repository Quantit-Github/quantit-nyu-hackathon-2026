"""Proposer's original backtest script for Case 02 (Fast Industry Reversal)."""
import numpy as np
import pandas as pd

signals = pd.read_csv("signal_panel.csv", index_col=0, parse_dates=True)
returns = pd.read_csv("returns_panel.csv", index_col=0, parse_dates=True)

# Cross-sectional dollar-neutral weights (Gross leverage = 1.0)
weights = signals.sub(signals.mean(axis=1), axis=0)
weights = weights.div(weights.abs().sum(axis=1), axis=0).fillna(0.0)
positions = weights.shift(1)

# BUG IN PROPOSER SCRIPT: computed net portfolio weight sum change (always 0!) instead of sum(|dw_i|)
wrong_turnover = positions.sum(axis=1).diff().abs().fillna(0.0)
gross_returns = (positions * returns).sum(axis=1).dropna()
claimed_net_returns = gross_returns - (10.0 / 10000.0) * wrong_turnover.loc[gross_returns.index]

sharpe = claimed_net_returns.mean() / claimed_net_returns.std() * np.sqrt(252)
print(f"Claimed Net Sharpe (at 10 bps): {sharpe:.2f}")

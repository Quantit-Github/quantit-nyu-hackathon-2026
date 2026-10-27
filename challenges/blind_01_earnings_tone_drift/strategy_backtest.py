"""Proposer backtest for Blind Challenge 01 (Earnings Tone Drift)."""
import numpy as np
import pandas as pd

signals = pd.read_csv("signal_panel.csv", index_col=0, parse_dates=True)
returns = pd.read_csv("returns_panel.csv", index_col=0, parse_dates=True)

weights = signals.sub(signals.mean(axis=1), axis=0)
weights = weights.div(weights.abs().sum(axis=1), axis=0).fillna(0.0)

# Proposer computed portfolio returns directly from close-of-day weights:
positions = weights
turnover = positions.diff().abs().sum(axis=1).fillna(0.0)
net_returns = (positions * returns).sum(axis=1) - (10.0 / 10000.0) * turnover
sharpe = net_returns.mean() / net_returns.std() * np.sqrt(252)
print(f"Reported Net Sharpe: {sharpe:.2f}")

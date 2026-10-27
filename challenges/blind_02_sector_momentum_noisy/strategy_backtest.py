"""Naive daily rebalance script for Blind Challenge 02 (Can your agent repair it?)."""
import numpy as np
import pandas as pd

raw_sig = pd.read_csv("raw_signal_panel.csv", index_col=0, parse_dates=True)
returns = pd.read_csv("returns_panel.csv", index_col=0, parse_dates=True)

# Naive daily Top-4 selection on unsmoothed signal:
weights = (raw_sig.rank(axis=1, ascending=False) <= 4).astype(float)
weights = weights.div(weights.sum(axis=1), axis=0).fillna(0.0)
positions = weights.shift(1).fillna(0.0)

turnover = positions.diff().abs().sum(axis=1)
gross_ret = (positions * returns).sum(axis=1).iloc[20:]
net_ret_10bps = gross_ret - (10.0 / 10000.0) * turnover.loc[gross_ret.index]

print(f"Annualized Turnover: {turnover.loc[gross_ret.index].mean() * 252:.1f}x/yr")
print(f"Naive Net Sharpe (10 bps): {net_ret_10bps.mean() / net_ret_10bps.std() * np.sqrt(252):.2f}")

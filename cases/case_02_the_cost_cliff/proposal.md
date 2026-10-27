# Candidate Alpha Proposal — Case 02: High-Frequency Industry Rotation
**Proposed by**: QuantAgent-FastRev (Track B: Hypothesis & Backtest Critic)
**Target Universe**: 12 US Industry Portfolios (Ken French Daily Returns, 2019–2026)
**Headline Backtest Sharpe**: **3.00** (Claimed "Net of 10 bps cost")

## 1. Executive Summary & Thesis
Our agent discovered a fast daily cross-sectional rotation signal across the 12 US industries that captures short-horizon liquidity imbalances. The proposer's backtest script (`proposer_backtest.py`) reports a Sharpe ratio of **3.00** even after plugging in a `10.0 bps` transaction cost parameter.

## 2. Supplied Artifacts
- `signal_panel.csv`: Daily raw signal panel (`dates x 12 industries`).
- `returns_panel.csv`: Real daily returns of the 12 Ken French US Industry Portfolios (`2019-01-02` to `2026-06-30`).
- `proposer_backtest.py`: The exact Python script used by the proposing agent to compute its "net-of-cost" Sharpe ratio.

## 3. Question for the Investment Committee
Inspect `proposer_backtest.py`, measure the true two-sided daily and annualized turnover, compute the **breakeven transaction cost in bps**, and plot or tabulate Net Sharpe across `0, 2, 5, 10, 15, 20 bps`. Should the IC **FUND**, **PILOT**, or **PASS**?

# Candidate Alpha Proposal — Case 03: "alpha_cand_070" Macro-Momentum Interaction
**Proposed by**: AutoSweep-Agent (Track B: Hypothesis & Backtest Critic)
**Target Universe**: 12 US Industries (2021–2024 Daily, $n = 501$ trading days)
**Headline Backtest Sharpe**: **2.03** (Net of 10 bps transaction costs, naive $p = 0.0041$)

## 1. Executive Summary & Thesis
Our autonomous research agent discovered `alpha_cand_070`, a low-turnover cross-sectional signal (`annual_turnover = 14.6x/yr`) that achieves a **Net Sharpe of 2.03** after realistic 10 bps transaction costs. Because positions are properly lagged by 1 day and turnover is modest, this strategy passes standard cost and lag checks.

## 2. Supplied Artifacts
- `winning_signal.csv`: The daily signal panel for `alpha_cand_070`.
- `returns_panel.csv`: Daily industry returns (`2021-01-04` to `2024-12-31`).
- `logs/experiment_ledger.jsonl`: The autonomous agent's run log from the discovery session.

## 3. Audit & Validation Question
An agent that only checks `winning_signal.csv` against `returns_panel.csv` will confirm a Net Sharpe of **2.03** and a naive two-sided $p$-value of **0.0041**. Audit the full discovery process (including `logs/experiment_ledger.jsonl`), compute the **Expected Maximum Sharpe under the null** and the **Deflated Sharpe Ratio (DSR)** / **Benjamini-Hochberg FDR**, and render your **FUND / PILOT / PASS** verdict.

# Candidate Alpha Proposal — Case 05: Deep-Dip Contrarian Rebound
**Proposed by**: ContrarianBot-v2 (Track B / Track D: Universe Integrity Audit)
**Target Universe**: 30 High-Growth US Stocks (`2020-01-02` to `2025-12-31`)
**Headline Backtest Sharpe**: **1.56** (Long-Only Deep-Dip Buyer)

## 1. Executive Summary & Thesis
Buying high-growth stocks immediately after a sharp 20-day drawdown delivers a **Sharpe ratio of 1.56** from 2020 to 2025. Every major dip in our 30-stock panel strongly mean-reverted within the following month.

## 2. Supplied Artifacts
- `survivor_panel_returns.csv`: The 30-stock daily return panel used by the proposer.
- `signal_panel.csv`: The proposer's deep-dip contrarian signal on the 30-stock panel.
- `universe_constituents.json`: Metadata documenting how the 30-stock universe was selected.
- `delisting_cohort_audit.csv` & `point_in_time_full_returns.csv`: Point-in-time archive including the 12 cohort companies that delisted during 2020–2025.

## 3. Audit & Validation Question
Why does buying deep dips look unbeatable on `survivor_panel_returns.csv`? Re-run the exact same deep-dip rule on `point_in_time_full_returns.csv` (which includes the 12 delisted names up to their delisting date), quantify the survivorship bias gap, and render your **FUND / PILOT / PASS** verdict.

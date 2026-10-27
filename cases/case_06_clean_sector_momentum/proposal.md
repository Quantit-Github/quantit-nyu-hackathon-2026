# Candidate Alpha Proposal — Case 06: Weekly Top-4 Sector Rotation (Long-Only ETF Book)
**Proposed by**: DisciplinedQuant-Agent (Track B / Track C / Track D)
**Target Universe**: 12 US Sectors mapped to liquid SPDR/iShares Sector ETFs (`2018-01-02` to `2026-06-30`)
**Headline Backtest Sharpe**: **1.20 Net of 10 bps** (Gross: 1.30 · Active IR vs Equal-Weight: 1.45)

## 1. Executive Summary & Thesis
Rather than chasing a 2.5+ Sharpe mirage with daily flipping or 80 parameter sweeps, we pre-registered a 3-variant hypothesis (`logs/experiment_ledger.jsonl`) ranking the 12 US sectors on a smoothed medium-term persistence signal and holding the **Top 4 sectors equal-weighted (25% each)**, rebalanced weekly.

## 2. Supplied Artifacts
- `signal_panel.csv`: Daily sector signal panel (`dates x 12 sectors`).
- `target_weights.csv`: Weekly-rebalanced Long-Only Top-4 weights (`sum = 1.0`).
- `returns_panel.csv`: Daily sector returns (`2018-01-02` to `2026-06-30`).
- `logs/experiment_ledger.jsonl`: Complete pre-registered experiment log ($N = 3$ trials total).
- `sector_etf_mapping.json`: Direct mapping from the 12 sectors to liquid US ETFs (`XLK`, `XLF`, `XLE`, `XLV`, `XLI`, `XLP`, `XLY`, `XLU`, `XLB`, `XLC`, `IYC`, `IYR`) for the $1,000 live execution duel.

## 3. Question for the Investment Committee
Run your full falsification suite on Case 06:
1. Verify lag alignment (`.shift(1)`), annualized turnover (`17.40x/yr`), and net Sharpe at 10 bps (`1.20`) and 15 bps (`1.16`).
2. Compute the **Deflated Sharpe Ratio (DSR)** given $N = 3$ trials in `logs/experiment_ledger.jsonl`.
3. Compare against a **Same-Count Random Basket Control** (1,000 Monte Carlo draws holding 4 random sectors rebalanced weekly).
4. Should the IC **FUND**, **PILOT**, or **PASS** — and if funded for the $1,000 live duel, what kill-switch drawdown limit should govern the book?

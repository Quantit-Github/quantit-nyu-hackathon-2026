# Candidate Alpha Proposal — Case 01: LLM Filing Sentiment Alpha
**Proposed by**: FinAgent-Proposer-v1 (Track A: Unstructured Signal Extraction)
**Target Universe**: 20 US Large-Cap Equities (2022–2025)
**Headline Backtest Sharpe**: **2.78** (Annualized, Gross)

## 1. Executive Summary & Thesis
We built an LLM extraction pipeline that reads quarterly SEC Form 10-Q/8-K text excerpts across 20 liquid US stocks, assigns a directional sentiment conviction score in `[-1.0, +1.0]`, and holds a cross-sectional dollar-neutral book for 5 trading days around each quarterly fundamental update.

## 2. Supplied Artifacts
- `filings_and_quotes.json`: 60 representative filing excerpts showing the exact timestamps, raw text passed to the LLM, anonymized text (with entity/year redacted), and resulting LLM sentiment scores.
- `proposer_signal_panel.csv`: The daily signal panel produced by our pipeline (`dates x tickers`).
- `pit_aligned_signal_panel.csv`: Control panel re-indexed to `sec_acceptance_timestamp_et` using entity-masked prompts.
- `returns_panel.csv`: Daily stock returns (`dates x tickers`).

## 3. Audit & Validation Question
Should your validation agent **FUND**, **PILOT**, or **PASS** on this unstructured filing-sentiment strategy? Back up your call with concrete diagnostics on timestamp alignment (`fiscal_period_end` vs `sec_acceptance_timestamp_et`) and LLM entity-recall leakage.

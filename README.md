# Quantit × NYU Stern: Finance Agent Hackathon Starter Kit (Fall 2026)

**Course**: Generative AI in Business Lab (`TECH-UB 41`) · NYU Stern  
**Instructor**: Prof. Christian Grewell (`christian@nyu.edu`)  
**Industry Partner**: Quantit (`arkraft.ai` / `quantit.io`)  
**Dates**: Kickoff **Tue, Nov 10, 2026 (5:00–7:00 PM ET)** · Final Pitch Night **Tue, Nov 17, 2026 (6:30–8:00 PM ET)**

---

## 1. Why This Hackathon Is Different: The "Mirage Benchmark"

In 2026, any coding agent (`Pi` + OpenRouter) can write a Python backtest and produce a chart showing a **2.5+ Sharpe ratio** in three minutes. When generation cost drops to zero, **generating plausible-looking backtests is no longer the bottleneck—falsification and disciplined portfolio construction are.**

In real quantitative asset management, 95%+ of AI-generated strategies fail out-of-sample because of subtle structural traps:
1. **Point-in-Time & Entity Recall Leakage**: The LLM remembers which stocks won in 2023–2024, or trades on quarterly financials at `period_end` before the SEC filing actually became public.
2. **The Transaction Cost Cliff**: A daily reversal signal looks unbeatable at `0 bps` (or when turnover is miscoded), but evaporates at `10 bps` per trade.
3. **Multiple-Testing Selection Bias ("The 80 Tries")**: Sweeping 80 random features and presenting only the single best winner manufactures a $p < 0.01$ mirage out of pure noise.
4. **Regime Correlation Spikes**: Five sleeves with `0.00` correlation on calm days suddenly jump to `0.89` correlation during market sell-offs.
5. **Universe Survivorship Bias**: Buying "-20% deep dips" on a panel of companies selected from *today's* survivors guarantees every dip recovers—because the 12 companies that went bankrupt were quietly omitted.

---

## 2. Three Graduated Challenges for Your `Pi` Agent

This repository is structured into **three graduated levels** so your team can both learn the core falsification mechanics and push your agent on genuinely unsolved challenges:

### Level 1 — The 6 Guided Cases (`cases/case_01` … `cases/case_06`)
- Six reference candidate packets (5 planted traps + 1 Clean Control) walked through during the Nov 10 kickoff lecture.
- Use `python scripts/inspect_case.py --all` to see how deterministic verification functions catch each defect and confirm the clean control (`case_06_clean_sector_momentum`).

### Level 2 — 4 Unsolved Blind Challenges (`challenges/blind_01` … `challenges/blind_04`)
- Four **unlabeled strategy packets** with **no spoilers in the folder names** and **no pre-written solver in `inspect_case.py`**:
  - `challenges/blind_01_earnings_tone_drift/`
  - `challenges/blind_02_sector_momentum_noisy/` *(Agent Repair Challenge: can your agent diagnose why the naive script loses money after costs and patch the signal smoothing/rebalance cadence to recover the underlying alpha?)*
  - `challenges/blind_03_factor_grid_winner/`
  - `challenges/blind_04_defensive_sector_shield/`
- Task your `Pi` agent (via custom tools in `.pi/extensions/` or `scripts/`) to autonomously audit all 4 blind folders, repair `blind_02`, and record your findings in `submission/audit_verdicts.json`.

### Level 3 — The $1,000 Post-Cutoff Live Duel (`data/market_sandbox/` · Nov 18 – Dec 18, 2026)
- Prof. Christian Grewell is funding the winning team's recommendation with **$1,000 in real cash** for one month starting **Wednesday, Nov 18, 2026**.
- **Nov 18 – Dec 18, 2026 lies strictly after every frontier LLM's training cutoff**—making it a true test of out-of-sample generalization.
- Inside `data/market_sandbox/`, you have daily returns (`2018-01-02` to `2026-06-30`, 2,134 trading days) across **130 Assets (`multi_asset_universe_130_returns_2018_2026.csv`)**:
  - **42 Liquid Multi-Asset & Thematic ETFs** (`liquid_etf_daily_returns_2018_2026.csv`: Broad US, 13 Sectors, 10 Industry/Thematic like `SMH`, `IGV`, `IBB`, `XBI`, `KRE`, `XOP`, `ITA`, `GDX`, `XHB`, `XRT`, 5 Factor ETFs `MTUM`, `QUAL`, `VLUE`, `USMV`, `SIZE`, 5 Treasury/Credit ETFs `SHY`, `IEF`, `TLT`, `LQD`, `HYG`, and 3 Commodity ETFs `GLD`, `SLV`, `DBC`).
  - **80 Active US Large-Cap Equities** (`us_equity_daily_returns_2018_2026.csv`: S&P 100 / Nasdaq-100 leaders across all 11 sectors) **+ 8 Delisted Historical Trap Stocks (`DELIST_01` … `DELIST_08`)** to test whether your agent's stock screen checks universe survivorship (`sandbox_universe_metadata.json`).
  - **Macro & Regime Indicators** (`macro_and_regime_signals_2018_2026.csv`).
- Have your agent synthesize, repair, or ensemble a long-only portfolio (3 to 25 liquid ETFs and/or large-cap equities) and evaluate it with `python scripts/evaluate_custom_portfolio.py` (which logs every trial to `logs/sandbox_trial_ledger.jsonl` so your Deflated Sharpe Ratio is tracked honestly), then output your final weights in `submission/portfolio_submission.json`.

---

## 3. Quickstart Inside Icecube (`~/work`)

Everything in this repository is **100% self-contained** (requires only `numpy`, `pandas`, `scipy`, `pytest`—no external market-data API keys needed inside your Icecube container).

```bash
# 1. Clone the repository into your Icecube workspace
git clone https://github.com/Quantit-Github/quantit-nyu-hackathon-2026.git
cd quantit-nyu-hackathon-2026

# 2. Install in editable mode (or run directly with system/venv Python)
pip install -e ".[dev]"

# 3. Verify all audit primitives and case files pass unit tests
pytest -q

# 4. Run diagnostics on Guided Case 02 (The Cost Cliff)
python scripts/inspect_case.py --case case_02_the_cost_cliff

# 5. Evaluate a portfolio on the 20-ETF Market Sandbox (auto-logs trial N for DSR)
python scripts/evaluate_custom_portfolio.py --portfolio submission/portfolio_submission_template.json
```

---

## 4. Mapping to Course Starter Cards (A, B, C, D)

| Starter Card | Matching Guided & Blind Packets | Core Verification Primitives in `quantit_audit/` |
|---|---|---|
| **Card A: Unstructured Signal Extraction** | `case_01_filing_lag_mirage` · `blind_01_earnings_tone_drift` | Compare LLM sentiment scores with company/year visible vs anonymized (`COMPANY_REDACTED`), and audit `fiscal_period_end` vs `sec_acceptance_timestamp_et` / lag alignment |
| **Card B: Hypothesis & Backtest Critic** | `case_02_the_cost_cliff` · `case_03_twenty_tries` · `case_05_survivorship_trap` · `blind_02_sector_momentum_noisy` · `blind_03_factor_grid_winner` | `cost_sensitivity_curve()`, `expected_max_sharpe()`, `deflated_sharpe_ratio()`, `benjamini_hochberg()`, survivorship cohort comparison, agent code repair |
| **Card C: Regime & Risk Monitor** | `case_04_regime_correlation_spike` · `case_06_clean_sector_momentum` · `blind_04_defensive_sector_shield` | `regime_correlation_audit()` (`CALM` vs `STRESS` pairwise correlation spike, tail skewness) & `matched_null_benchmark()` |
| **Card D: Open Quantit Challenge** | All 6 Guided Cases + 4 Blind Challenges + `data/market_sandbox/` | Build an end-to-end Falsification & Portfolio Construction Agent that audits all packets and builds a winning `$1,000` live portfolio |

---

## 5. Repository Structure

```text
quantit-nyu-hackathon-2026/
├── AGENTS.md                        # Starter instructions for your Pi coding agent
├── INTENT_TEMPLATE.md               # Template for Deliverable #1 (INTENT.md)
├── README.md                        # This guide
├── pyproject.toml                   # Minimal dependencies (numpy, pandas, scipy, pytest)
├── quantit_audit/                   # Deterministic verification & falsification library
│   ├── backtest.py                  # Lagged backtester, cost curve, matched-null Monte Carlo, regime audit
│   ├── statistics.py                # Deflated Sharpe Ratio (DSR), Expected Max Null SR, BH-FDR
│   └── validator.py                 # Schema & risk-limit validator for audit verdicts and $1,000 live portfolio
├── cases/                           # Level 1: 6 Guided Candidate Packets (5 traps + 1 clean control)
│   ├── case_01_filing_lag_mirage/
│   ├── case_02_the_cost_cliff/
│   ├── case_03_twenty_tries/
│   ├── case_04_regime_correlation_spike/
│   ├── case_05_survivorship_trap/
│   └── case_06_clean_sector_momentum/
├── challenges/                      # Level 2: 4 Unsolved Blind Challenges (audit + repair)
│   ├── blind_01_earnings_tone_drift/
│   ├── blind_02_sector_momentum_noisy/
│   ├── blind_03_factor_grid_winner/
│   └── blind_04_defensive_sector_shield/
├── data/
│   ├── public_benchmarks/           # Ken French Daily 12 Industries & Fama-French Factors (2018–2026)
│   └── market_sandbox/              # Level 3: 20-ETF Daily Return & Macro/Regime Sandbox for $1,000 Live Duel
├── scripts/
│   ├── inspect_case.py              # CLI diagnostic runner for the 6 guided cases
│   ├── evaluate_custom_portfolio.py # Sandbox evaluator with automatic trial-ledger DSR tracking
│   └── validate_submission.py       # Pre-flight check for your final JSON deliverables
├── submission/
│   ├── audit_verdicts_template.json         # Structured Fund / Pilot / Pass table across cases & blind challenges
│   └── portfolio_submission_template.json   # Executable spec for the $1,000 Nov 18 – Dec 18 Live Duel
└── tests/
    └── test_audit_toolkit.py        # Unit tests verifying the math and case integrity
```

---

## 6. Deliverables Checklist for Tuesday, Nov 17 (6:30 PM ET)

1. **`INTENT.md`** (copied from `INTENT_TEMPLATE.md` and posted to the class Agent Board).
2. **Working Agent Prototype**: Your refined `AGENTS.md` + at least one custom verification tool/script in `.pi/extensions/` or `scripts/`.
3. **Evaluation & Failure Log**:
   - Baseline comparison (e.g., naive unguarded LLM prompt or equal-weight / random-basket baseline).
   - 5 structured test cases across `cases/`, `challenges/`, or `data/market_sandbox/`.
   - 1 real mistake your AI agent made during development and how your guardrail caught/fixed it.
   - Validated `submission/audit_verdicts.json` and `submission/portfolio_submission.json` (check with `python scripts/validate_submission.py`).
4. **90-Second Demo Video**: Submitted before class on Nov 17.
5. **5-Minute Live Pitch**: Delivered live on Nov 17, closing with an evidence-backed **`FUND`**, **`PILOT`**, or **`PASS`** recommendation and your $1,000 live portfolio spec.

---

## 7. Data Provenance & Academic License Note

- **Ken French Data Library (`data/public_benchmarks/`)**: Real daily US factor and 12-industry portfolio returns (`2018-01-02` to `2026-06-30`), publicly redistributable for academic and educational use.
- **Calibrated Evaluation Panels (`cases/`, `challenges/`, `data/market_sandbox/`)**: Candidate signals, filing excerpts, and survivorship/regime stress panels are deterministically calibrated around real market factor structures so that each case carries an exact, verifiable ground truth. Ticker symbols in single-stock examples are public identifiers; calibrated evaluation series must not be mistaken for vendor-licensed exchange feeds.

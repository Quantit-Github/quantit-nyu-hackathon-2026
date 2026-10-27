# Quantit × NYU Stern: Finance Agent Hackathon Starter Kit (Fall 2026)

**Course**: Generative AI in Business Lab (`TECH-UB 41`) · NYU Stern  
**Instructor**: Prof. Christian Grewell (`christian@nyu.edu`)  
**Industry Anchor & Investment Committee**: Quantit (`arkraft.ai` / `quantit.io`)  
**Dates**: Kickoff **Tue, Nov 10, 2026 (5:00–7:00 PM ET)** · Presentations & IC Judging **Tue, Nov 17, 2026 (6:30–8:00 PM ET)**

---

## 1. Why This Hackathon Is Different: The "Mirage Benchmark"

In 2026, any coding agent (`Pi` + OpenRouter) can write a Python backtest and produce a chart showing a **2.5+ Sharpe ratio** in three minutes. When generation cost drops to zero, **generating plausible-looking backtests is no longer the bottleneck—falsification is.**

In real quantitative asset management, 95%+ of AI-generated strategies fail out-of-sample because of subtle structural traps:
1. **Point-in-Time & Entity Recall Leakage**: The LLM remembers which stocks won in 2023–2024, or trades on quarterly financials at `period_end` before the SEC filing actually became public.
2. **The Transaction Cost Cliff**: A daily reversal signal looks unbeatable at `0 bps` (or when turnover is miscoded), but evaporates at `10 bps` per trade.
3. **Multiple-Testing Selection Bias ("The 80 Tries")**: Sweeping 80 random features and presenting only the single best winner (`alpha_cand_061`) manufactures a $p < 0.01$ mirage out of pure noise.
4. **Regime Correlation Spikes**: Five sleeves with `0.00` correlation on calm days suddenly jump to `0.89` correlation during market sell-offs.
5. **Universe Survivorship Bias**: Buying "-20% deep dips" on a panel of companies selected from *today's* survivors guarantees every dip recovers—because the 12 companies that went bankrupt were quietly omitted.

### Your Two-Part Mission
1. **Audit the 6 Seeded Candidate Packets (`cases/case_01` … `cases/case_06`)**:
   - Inside `cases/`, six autonomous research agents have submitted investment proposals (`proposal.md` + signal/return CSVs + logs) to the Quantit Investment Committee.
   - **Five of them contain fatal real-world traps. At least one is genuinely sound (the Clean Control).**
   - Build and wire your own agent workflow (`AGENTS.md` + `.pi/extensions/` or Python verification scripts) to audit the packets, catch the traps with hard quantitative evidence, and render an honest **`FUND` / `PILOT` / `PASS`** call on your chosen track (or across all six!).
2. **Compete in the $1,000 Post-Cutoff Live Duel (Nov 18 – Dec 18, 2026)**:
   - Prof. Christian Grewell is funding the winning team's recommendation with **$1,000 in real cash** for one month starting **Wednesday, Nov 18, 2026**.
   - Notice the calendar: **Nov 18 – Dec 18, 2026 lies strictly after every frontier LLM's training cutoff.** No model can memorize next month's market returns.
   - To qualify for the $1,000 allocation, your agent must output a validated `submission/portfolio_submission.json` (either endorsing our Clean Control ETF book or proposing your own verified liquid US ETF / large-cap basket) that will be tracked against `SPY` and a `Same-Count Random Basket Control`.

---

## 2. Quickstart Inside Icecube (`~/work`)

Everything in this repository is **100% self-contained** (requires only `numpy`, `pandas`, `scipy`, `pytest`—no external market-data API keys needed inside your Icecube container).

```bash
# 1. Clone the repository into your Icecube workspace
git clone https://github.com/Quantit-Github/quantit-nyu-hackathon-2026.git
cd quantit-nyu-hackathon-2026

# 2. Install in editable mode (or run directly with system/venv Python)
pip install -e ".[dev]"

# 3. Verify all audit primitives and case files pass unit tests
pytest -q

# 4. Run your first diagnostic on Case 02 (The Cost Cliff)
python scripts/inspect_case.py --case case_02_the_cost_cliff
```

---

## 3. Mapping to Course Starter Cards (A, B, C, D)

You may focus deeply on one Starter Card (and run 5 structured test cases around it) or build a full **Investment Committee Gatekeeper Agent** that audits all 6 cases:

| Starter Card | Matching Seeded Cases in `cases/` | Core Verification Primitives in `quantit_audit/` |
|---|---|---|
| **Card A: Unstructured Signal Extraction** | `case_01_filing_lag_mirage` (`filings_and_quotes.json` + `proposer_signal_panel.csv` vs `pit_aligned_signal_panel.csv`) | Compare LLM sentiment scores with company/year visible vs anonymized (`COMPANY_REDACTED`), and audit `fiscal_period_end` vs `sec_acceptance_timestamp_et` |
| **Card B: Hypothesis & Backtest Critic** | `case_02_the_cost_cliff` · `case_03_twenty_tries` · `case_05_survivorship_trap` · `case_06_clean_sector_momentum` | `cost_sensitivity_curve()`, `expected_max_sharpe()`, `deflated_sharpe_ratio()`, `benjamini_hochberg()`, survivorship cohort comparison |
| **Card C: Regime & Risk Monitor** | `case_04_regime_correlation_spike` · `case_06_clean_sector_momentum` | `regime_correlation_audit()` (`CALM` vs `STRESS` pairwise correlation spike, tail skewness) & `matched_null_benchmark()` |
| **Card D: Open Quantit Challenge** | All 6 Cases (`cases/case_01` … `case_06`) + `data/public_benchmarks/` | Build an end-to-end IC Falsification Agent that scores all 6 packets automatically and emits a battle-tested `$1,000` live portfolio |

---

## 4. Repository Structure

```text
quantit-nyu-hackathon-2026/
├── AGENTS.md                        # Starter instructions for your Pi coding agent
├── INTENT_TEMPLATE.md               # Template for Deliverable #1 (INTENT.md)
├── README.md                        # This guide
├── pyproject.toml                   # Minimal dependencies (numpy, pandas, scipy, pytest)
├── quantit_audit/                   # Deterministic verification & falsification library
│   ├── backtest.py                  # Lagged backtester, cost curve, matched-null Monte Carlo, regime audit
│   ├── statistics.py                # Deflated Sharpe Ratio (DSR), Expected Max Null SR, BH-FDR
│   └── validator.py                 # Schema & risk-limit validator for IC verdicts and $1,000 live portfolio
├── cases/                           # The 6 Candidate Alpha Packets (5 traps + 1 clean control)
│   ├── case_01_filing_lag_mirage/
│   ├── case_02_the_cost_cliff/
│   ├── case_03_twenty_tries/
│   ├── case_04_regime_correlation_spike/
│   ├── case_05_survivorship_trap/
│   └── case_06_clean_sector_momentum/
├── data/public_benchmarks/          # Ken French Daily 12 Industries & Fama-French Factors (2018–2026)
├── scripts/
│   ├── inspect_case.py              # CLI diagnostic runner (can be wired into .pi/extensions/)
│   └── validate_submission.py       # Pre-flight check for your final JSON deliverables
├── submission/
│   ├── ic_verdicts_template.json    # Structured Fund / Pilot / Pass table across the cases
│   └── portfolio_submission_template.json  # Executable spec for the $1,000 Nov 18 – Dec 18 Live Duel
└── tests/
    └── test_audit_toolkit.py        # Unit tests verifying the math and case integrity
```

---

## 5. Deliverables Checklist for Tuesday, Nov 17 (6:30 PM ET)

1. **`INTENT.md`** (copied from `INTENT_TEMPLATE.md` and posted to the class Agent Board).
2. **Working Agent Prototype**: Your refined `AGENTS.md` + at least one custom verification tool/script in `.pi/extensions/` or `scripts/`.
3. **Evaluation & Failure Log**:
   - Baseline comparison (e.g., naive unguarded LLM prompt or equal-weight / random-basket baseline).
   - 5 structured test cases (including at least 1 adversarial/failure case from `cases/`).
   - 1 real mistake your AI agent made during development and how your guardrail caught/fixed it.
   - Validated `submission/ic_verdicts.json` and `submission/portfolio_submission.json` (check with `python scripts/validate_submission.py`).
4. **90-Second Demo Video**: Submitted before class on Nov 17.
5. **5-Minute Live Investment Committee Pitch**: Delivered live on Nov 17, closing with an evidence-backed **`FUND`**, **`PILOT`**, or **`PASS`** recommendation.

---

## 6. Data Provenance & Academic License Note

- **Ken French Data Library (`data/public_benchmarks/`)**: Real daily US factor and 12-industry portfolio returns (`2018-01-02` to `2026-06-30`), publicly redistributable for academic and educational use.
- **Calibrated Evaluation Panels (`cases/`)**: Candidate signals, filing excerpts, and survivorship/regime stress panels are deterministically calibrated around real market factor structures so that each case carries an exact, verifiable ground truth. Ticker symbols in single-stock examples are public identifiers; calibrated evaluation series must not be mistaken for vendor-licensed exchange feeds.

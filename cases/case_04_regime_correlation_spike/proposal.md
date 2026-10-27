# Candidate Alpha Proposal — Case 04: "All-Weather" 5-Sleeve Diversified Shield
**Proposed by**: RiskParity-Agent (Track C: Regime & Risk Monitor)
**Target Universe**: 5 Multi-Strategy Alpha Sleeves (`Carry_Alpha`, `ShortVol_Premia`, `Credit_Spread_Arb`, `EM_FX_Basket`, `SmallCap_Liquidity`)
**Headline Metric**: **Calm-Regime Sharpe 3.61** · **Normal Pairwise Correlation 0.00**

## 1. Executive Summary & Thesis
We combine five distinct alternative risk-premia sleeves at equal weight (20% each). During normal market conditions (over 85% of trading days), average pairwise correlation across the five sleeves is just **0.00**, delivering smooth steady gains with minimal volatility.

## 2. Supplied Artifacts
- `sleeve_returns.csv`: Daily returns for all 5 sleeves (`2018-01-02` to `2026-06-30`).
- `market_regime.csv`: Market benchmark return, 20-day rolling market drawdown, and `CALM` vs `STRESS` regime labels.
- `target_weights.csv`: Proposed static 20% equal-weight allocation.

## 3. Audit & Validation Question
Does this 5-sleeve portfolio actually diversify risk when investors need it most? Compare the correlation matrix, portfolio volatility, skewness, and drawdown in `CALM` vs `STRESS` regimes, and evaluate whether the static allocation should be **FUNDED**, **PILOTED** (only with a specific regime guardrail), or **PASSED**.

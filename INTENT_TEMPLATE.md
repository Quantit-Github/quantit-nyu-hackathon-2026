# INTENT.md — Problem & Value Brief Template

> Copy this file to `INTENT.md` and post it to the class **Agent Board** for `@Grader` feedback.

## 1. Team & Track
- **Team Name**:
- **Members**:
- **Selected Starter Card**: (Card A: Unstructured Signal Extraction / Card B: Hypothesis & Backtest Critic / Card C: Regime & Risk Monitor / Card D: Open Quantit Challenge)

## 2. Target User & Decision Bottleneck
- **Who is the user?** (e.g., Portfolio Manager, Quantitative Researcher, Investment Committee Risk Officer)
- **What specific decision fails today when using naive AI agents?**
- **Why does this matter before deploying real capital?**

## 3. Agent Architecture & Custom Verification Tool
- **Model(s) used on OpenRouter**:
- **Core workflow in `AGENTS.md`**:
- **Custom tool / script wired into `.pi/extensions/` or `scripts/`**:
- **What deterministic check does your tool enforce that an LLM cannot reliably do in its head?**

## 4. Evaluation Plan (5 Test Cases + Baseline + 1 Failure Case)
1. **Baseline**: What naive heuristic or unguarded prompt are you comparing against?
2. **Test Case 1**:
3. **Test Case 2**:
4. **Test Case 3**:
5. **Test Case 4**:
6. **Test Case 5 (Adversarial / Failure Case)**:

## 5. Out of Scope
- State clearly what your agent intentionally does **not** attempt to do in a 1-week build.

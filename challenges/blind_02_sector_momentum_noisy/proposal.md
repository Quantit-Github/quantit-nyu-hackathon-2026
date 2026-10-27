# Blind Challenge 02: Fast Sector Signal (Agent Repair Challenge)
**Current Status**: Fails 10 bps transaction cost gate (`Net Sharpe = -0.71`, `Turnover = 317.2x/yr`)
**Universe**: 12 US Sectors (`2019-01-02` to `2026-06-30`)

## Challenge Task (Diagnose & Repair)
1. Audit `strategy_backtest.py` and `raw_signal_panel.csv` to explain why the naive implementation loses money after 10 bps costs.
2. **Agent Repair Task**: Is there a genuine slow-moving alpha buried underneath high-frequency noise in `raw_signal_panel.csv`? Have your agent test a minimal, principled signal-smoothing + weekly rebalance patch (logging every trial) and determine whether the repaired strategy passes the 10 bps cost gate and Matched-Null Random Basket benchmark.

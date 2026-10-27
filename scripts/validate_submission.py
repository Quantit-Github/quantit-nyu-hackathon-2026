#!/usr/bin/env python3
"""Pre-flight validator for Strategy Audit verdicts and the $1,000 Live Portfolio.

Run before submitting to the Agent Board / @Grader:
    python scripts/validate_submission.py \
        --verdicts submission/audit_verdicts.json \
        --portfolio submission/portfolio_submission.json
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from quantit_audit.validator import validate_audit_verdicts, validate_portfolio_submission


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate hackathon submission JSON files.")
    parser.add_argument(
        "--verdicts",
        type=Path,
        default=REPO_ROOT / "submission" / "audit_verdicts_template.json",
        help="Path to audit_verdicts.json",
    )
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=REPO_ROOT / "submission" / "portfolio_submission_template.json",
        help="Path to portfolio_submission.json",
    )
    args = parser.parse_args()

    v_errors = validate_audit_verdicts(args.verdicts)
    p_errors = validate_portfolio_submission(args.portfolio)

    print(f"=== Checking {args.verdicts.name} ===")
    if v_errors:
        for err in v_errors:
            print(f"  [FAIL] {err}")
    else:
        print("  [PASS] All Strategy Audit case verdicts are structurally valid.")

    print(f"\n=== Checking {args.portfolio.name} ===")
    if p_errors:
        for err in p_errors:
            print(f"  [FAIL] {err}")
    else:
        print("  [PASS] $1,000 Live Duel portfolio submission is valid and executable.")

    return 1 if (v_errors or p_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())

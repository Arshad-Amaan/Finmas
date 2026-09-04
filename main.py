"""
main.py — Run the multi-agent financial analysis from the command line.

Usage:
    python main.py AAPL
    python main.py TSLA MSFT INFY        # multiple tickers
    python main.py AAPL --real           # try real data via yfinance
"""

import sys

from orchestrator import Orchestrator
from tools import llm

DISCLAIMER = (
    "NOTE: Educational demo only — uses simulated data by default. "
    "Not financial advice."
)


def print_report(report: dict) -> None:
    d = report["decision"]
    line = "=" * 62
    print(f"\n{line}\n  MULTI-AGENT ANALYSIS: {d['ticker']}\n{line}")

    print(f"\n  FINAL DECISION : {d['decision']}  "
          f"(confidence {d['confidence_pct']}%)")
    print(f"  POSITION SIZE  : up to {d['position_size_pct']}% of portfolio")
    if d["risk_override_applied"]:
        print("  ⚠ Risk override: BUY downgraded to HOLD due to HIGH risk")

    votes = d["specialist_votes"]
    print(f"\n  Specialist votes -> Technical: {votes['technical']} | "
          f"Fundamental: {votes['fundamental']} | Sentiment: {votes['sentiment']} | "
          f"Risk: {votes['risk_level']}")

    print("\n  -- Technical Analyst --")
    for n in report["technical"]["notes"]:
        print(f"     • {n}")

    print("\n  -- Fundamental Analyst --")
    for n in report["fundamental"]["notes"]:
        print(f"     • {n}")

    print("\n  -- Sentiment Analyst --")
    for h in report["sentiment"]["headlines"]:
        tag = "+" if h["score"] > 0 else "-" if h["score"] < 0 else "·"
        print(f"     {tag} {h['headline']}")
    print(f"     LLM summary: {report['sentiment']['llm_summary']}")

    print("\n  -- Risk Manager --")
    for n in report["risk"]["notes"]:
        print(f"     • {n}")

    print("\n  -- Agent Communication Log --")
    for entry in report["audit_trail"]:
        print(f"     {entry}")
    print(f"\n  {DISCLAIMER}\n{line}\n")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    use_real = "--real" in sys.argv
    tickers = args or ["AAPL"]

    print(f"LLM backend: {llm.active_backend()}")
    for ticker in tickers:
        orch = Orchestrator(use_real_data=use_real)
        report = orch.full_report(ticker)
        print_report(report)


if __name__ == "__main__":
    main()

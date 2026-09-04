"""
orchestrator.py — Coordinates the multi-agent workflow.

Pipeline:
  1. Fetch market data onto the Blackboard.
  2. Run specialists in sequence (Technical, Fundamental, Sentiment, Risk).
     (They're independent, so you could parallelize them with threads.)
  3. PortfolioManager reads everything and issues the final call.
"""

from typing import Dict

from core import Blackboard, Message
from tools import market_data as md
from agents.specialists import (
    TechnicalAnalystAgent,
    FundamentalAnalystAgent,
    SentimentAnalystAgent,
    RiskManagerAgent,
)
from agents.portfolio_manager import PortfolioManagerAgent


class Orchestrator:
    def __init__(self, use_real_data: bool = False) -> None:
        self.bb = Blackboard()
        self.use_real_data = use_real_data
        self.specialists = [
            TechnicalAnalystAgent(self.bb),
            FundamentalAnalystAgent(self.bb),
            SentimentAnalystAgent(self.bb),
            RiskManagerAgent(self.bb),
        ]
        self.manager = PortfolioManagerAgent(self.bb)

    def analyze_ticker(self, ticker: str, days: int = 180) -> Dict:
        # Step 1 — data acquisition
        prices = md.get_prices(ticker, days=days, use_real=self.use_real_data)
        self.bb.write("prices", prices)
        self.bb.log(Message("Orchestrator", "ALL", f"data:{ticker}",
                            f"{len(prices)} days of prices loaded"))

        # Step 2 — specialists
        for agent in self.specialists:
            agent.run(ticker)

        # Step 3 — final decision
        decision = self.manager.run(ticker)
        return decision

    def full_report(self, ticker: str) -> Dict:
        decision = self.analyze_ticker(ticker)
        return {
            "decision": decision,
            "technical": self.bb.read("TechnicalAnalyst"),
            "fundamental": self.bb.read("FundamentalAnalyst"),
            "sentiment": self.bb.read("SentimentAnalyst"),
            "risk": self.bb.read("RiskManager"),
            "audit_trail": self.bb.audit_trail(),
        }

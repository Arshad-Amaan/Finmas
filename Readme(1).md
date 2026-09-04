# FinMAS — a multi-agent system for stock analysis

I built this to understand how agentic AI actually works under the hood — not by wiring together a framework, but by writing the whole thing from scratch in plain Python. FinMAS is a small team of five AI agents that argue about a stock and settle on a recommendation: BUY, HOLD, or SELL.

Run it on a ticker and you get the final call, a confidence score, a suggested position size, and — my favorite part — a log of every message the agents passed around while making the decision.

**Fair warning:** this is a learning project. It uses simulated data by default and the trading logic is deliberately simple. Please don't use it to invest actual money.

## What's going on inside

Instead of one big model doing everything, the work is split across specialists, the way a real investment team might operate:

- The **Technical Analyst** stares at the charts — moving average crossovers, RSI, MACD.
- The **Fundamental Analyst** checks whether the company is actually healthy: P/E ratio, revenue growth, margins, debt.
- The **Sentiment Analyst** reads recent headlines and scores the mood. If you have an LLM available (more on that below), it also writes a short plain-English summary.
- The **Risk Manager** doesn't have an opinion on direction at all. It measures volatility, worst historical drawdown, and value-at-risk, then says how large a position would be sane.
- The **Portfolio Manager** listens to everyone and makes the call.

They don't talk to each other directly. Everything goes through a shared blackboard — a common memory that each agent reads from and writes to. The orchestrator runs them in sequence, and every interaction gets logged with a timestamp, so you can trace exactly how a decision was reached.

```
                        ┌──────────────────┐
                        │   Orchestrator    │
                        └────────┬─────────┘
                                 │ loads price data
                 ┌───────────────▼────────────────┐
                 │           BLACKBOARD           │
                 │  (shared memory + message log) │
                 └──┬───────┬────────┬───────┬────┘
                    │       │        │       │
              Technical  Fundamental  Sentiment  Risk
               Analyst     Analyst     Analyst   Manager
                    │       │        │       │
                 ┌──▼───────▼────────▼───────▼──┐
                 │       Portfolio Manager       │
                 │    → BUY / HOLD / SELL        │
                 └───────────────────────────────┘
```

The final decision is a weighted vote — technical and fundamental opinions count for 35% each, sentiment for 30%. But the Risk Manager holds a veto of sorts: if a stock is rated HIGH risk, a BUY gets downgraded to HOLD and the position size gets cut in half. I added that after noticing the other agents would happily recommend buying something with a 57% drawdown history.

## Running it

You need Python 3.8 or newer. That's it — no dependencies, nothing to install.

```bash
git clone https://github.com/<your-username>/finmas.git
cd finmas
python main.py AAPL
```

You can pass several tickers at once:

```bash
python main.py TSLA MSFT INFY
```

By default, prices are simulated with a random walk that's seeded per ticker, so the same ticker always produces the same analysis. Different tickers get different "personalities" — TSLA is configured to be much more volatile than MSFT, for example. This keeps the demo reproducible and means it works offline.

## Making it smarter (all optional)

**Real market data.** Install yfinance and add the `--real` flag:

```bash
pip install yfinance
python main.py AAPL --real
```

If the fetch fails for any reason, it quietly falls back to simulated data.

**A free local LLM.** No API key, no billing. Install transformers and it just gets picked up:

```bash
pip install transformers torch
python main.py AAPL
```

The first run downloads Qwen2.5-0.5B-Instruct (about 1 GB) from Hugging Face; after that it's cached and runs offline, even on a laptop CPU. Want a different model? Set `HF_MODEL` to any chat model on the Hub:

```bash
export HF_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

**The Claude API**, if you'd rather:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

The backend is auto-detected — an Anthropic key wins if present, otherwise a local Hugging Face model if transformers is installed, otherwise the agents just run rule-based (which works fine). You can force a specific one with `LLM_BACKEND=huggingface`, `anthropic`, or `none`.

## Poking around the code

```
finmas/
├── main.py                     # CLI + report printing
├── orchestrator.py             # runs the pipeline
├── core.py                     # the Message and Blackboard classes
├── agents/
│   ├── base.py                 # BaseAgent — the run loop and LLM hook
│   ├── specialists.py          # the four analyst agents
│   └── portfolio_manager.py    # voting and the risk override
└── tools/
    ├── market_data.py          # prices, fundamentals, headlines
    ├── indicators.py           # SMA, RSI, MACD, volatility, VaR
    └── llm.py                  # pluggable LLM backend
```

Start with `core.py` (it's tiny) and then `orchestrator.py` — those two files are the whole architecture. The agents themselves are mostly straightforward if/else logic wrapped in a common interface.

## Adding your own agent

This is where it gets fun. A new agent is about twenty lines:

```python
from agents.base import BaseAgent

class MacroAnalystAgent(BaseAgent):
    name = "MacroAnalyst"
    role = "Tracks interest rates and macro conditions"

    def analyze(self, ticker: str) -> dict:
        prices = self.bb.read("prices")          # read shared data
        note = self.llm_reasoning("...")          # optional LLM call
        return {"signal": "HOLD", "notes": ["Rates elevated, staying neutral"]}
```

Register it in the `specialists` list in `orchestrator.py`, give it a weight in the Portfolio Manager if you want its vote to count, and it's part of the team.

Some things I'd like to add eventually, or that would make good exercises if you're learning from this:

- Run the specialists in parallel — they're independent, so a thread pool would do it
- A debate step, where one agent has to argue against the majority before the decision is final
- A backtesting agent that replays decisions over historical windows and reports how the system would have done
- Real headlines from a news API instead of the simulated feed
- Persisting the blackboard to SQLite so agents remember previous sessions

## License

MIT. Do whatever you like with it.

And once more, because it matters: this is an educational project about multi-agent architecture, not a trading tool. The signals are toy-simple on purpose. Don't make investment decisions with it.

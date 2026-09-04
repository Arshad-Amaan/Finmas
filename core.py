"""
core.py — Shared primitives for the multi-agent system.

Defines the Message format agents use to talk to each other and the
Blackboard (shared memory) where agents post their findings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Message:
    """A single message passed between agents."""
    sender: str
    recipient: str
    topic: str
    content: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __repr__(self) -> str:
        return f"[{self.timestamp}] {self.sender} -> {self.recipient} | {self.topic}"


class Blackboard:
    """
    Shared memory (blackboard architecture).

    Agents write their analysis here and read what other agents
    have produced. The orchestrator also logs all messages for
    a full audit trail.
    """

    def __init__(self) -> None:
        self.store: Dict[str, Any] = {}
        self.message_log: List[Message] = []

    def write(self, key: str, value: Any) -> None:
        self.store[key] = value

    def read(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def log(self, msg: Message) -> None:
        self.message_log.append(msg)

    def audit_trail(self) -> List[str]:
        return [repr(m) for m in self.message_log]

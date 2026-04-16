from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentConfig:
    name: str
    role: str
    model: str
    temperature: float = 0.7


@dataclass(slots=True)
class CouncilSignal:
    preferred_option: str = "undeclared"
    confidence: int = 50
    consensus_ready: bool = False
    key_risks: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MemberResponse:
    agent_name: str
    role: str
    model: str
    round_number: int
    content: str
    signal: CouncilSignal
    raw_response: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass(slots=True)
class RoundSummary:
    round_number: int
    member_responses: list[MemberResponse]
    majority_option: str
    ready_count: int
    majority_count: int
    consensus_reached: bool


@dataclass(slots=True)
class FinalRunResult:
    task_mode: str
    prompt: str
    context: str
    rounds: list[RoundSummary]
    final_markdown: str
    consensus_reached: bool
    final_majority_option: str
    synthesized_by: str

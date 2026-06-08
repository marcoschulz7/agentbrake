"""
AgentBrake — the emergency brake for multi-agent systems.

Stop runaway LangChain & CrewAI agents in real time, before 50 cents becomes
$47,000.

Quick start (LangChain):

    from agentbrake import LangChainBrake, AgentBrakeError

    brake = LangChainBrake(max_cost_usd=2.0, repeat_tool_limit=5)
    try:
        agent_executor.invoke({"input": "..."}, config={"callbacks": [brake]})
    except AgentBrakeError as e:
        print(f"Stopped safely: {e.reason}")

Quick start (CrewAI):

    from agentbrake import CrewAIBrake, AgentBrakeError

    CrewAIBrake(max_cost_usd=3.0).install()
    try:
        crew.kickoff()
    except AgentBrakeError as e:
        print(f"Crew stopped safely: {e.reason}")

The framework adapters (LangChainBrake, CrewAIBrake) are thin shells over the
framework-agnostic engine in `core`. The adapters depend on their respective
frameworks only at call time, so `import agentbrake` works even when neither
LangChain nor CrewAI is installed.
"""

from __future__ import annotations

from .core import (
    AgentBrakeError,
    BrakeConfig,
    BrakeEngine,
    DEFAULT_PRICING,
    RunStats,
)
from .langchain import LangChainBrake, LangChainBrakeMiddleware
from .crewai import CrewAIBrake

__version__ = "0.2.0"

__all__ = [
    "LangChainBrake",
    "LangChainBrakeMiddleware",
    "CrewAIBrake",
    "AgentBrakeError",
    "BrakeConfig",
    "BrakeEngine",
    "RunStats",
    "DEFAULT_PRICING",
    "__version__",
]

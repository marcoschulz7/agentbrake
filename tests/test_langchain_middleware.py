"""
LangChain 1.x middleware integration tests — run against REAL langchain.

These skip when langchain 1.x isn't installed. When it is, they prove the thing
that callbacks cannot do on LangGraph: actually HALT a running agent. We build a
real create_agent() agent wired to a fake model that loops forever, attach
LangChainBrakeMiddleware, and assert the run stops at the limit instead of
running to LangGraph's recursion ceiling.
"""

from typing import Any, List, Optional

import pytest

pytest.importorskip("langchain")
pytest.importorskip("langchain.agents.middleware")

from langchain.agents import create_agent
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool

from agentbrake import AgentBrakeError, LangChainBrakeMiddleware


@tool
def search(query: str) -> str:
    """search the web"""
    return "no useful result"


class LoopModel(BaseChatModel):
    """Always asks to call search with the same args -> infinite tool loop."""

    @property
    def _llm_type(self) -> str:
        return "agentbrake-test-loop"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "LoopModel":
        return self

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        msg = AIMessage(
            content="",
            tool_calls=[
                {"name": "search", "args": {"query": "x"}, "id": "c1", "type": "tool_call"}
            ],
        )
        return ChatResult(generations=[ChatGeneration(message=msg)])


def test_middleware_halts_a_real_langgraph_loop():
    brake = LangChainBrakeMiddleware(
        repeat_tool_limit=3,
        max_cost_usd=None,
        max_steps=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    agent = create_agent(LoopModel(), tools=[search], middleware=[brake])
    with pytest.raises(AgentBrakeError) as exc:
        agent.invoke(
            {"messages": [("user", "go")]},
            config={"recursion_limit": 100},
        )
    assert "loop detected" in exc.value.reason
    # stopped at the limit, nowhere near the recursion ceiling
    assert brake.engine.stats.tool_calls == 3


def test_middleware_step_limit_halts():
    brake = LangChainBrakeMiddleware(
        max_steps=5,
        repeat_tool_limit=None,
        max_cost_usd=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    agent = create_agent(LoopModel(), tools=[search], middleware=[brake])
    with pytest.raises(AgentBrakeError) as exc:
        agent.invoke(
            {"messages": [("user", "go")]},
            config={"recursion_limit": 100},
        )
    assert "step limit" in exc.value.reason
    assert brake.engine.stats.steps == 5

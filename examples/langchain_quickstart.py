"""
AgentBrake × LangChain — runnable quickstart, NO API KEY NEEDED.

This builds a *real* LangChain 1.x agent (create_agent / LangGraph), but wires
it to a fake model that keeps asking to call the same tool forever — the classic
runaway loop. AgentBrake is attached with the one line you'd use in production,
and it slams the brake after a few identical calls instead of letting the loop
run (and bill) forever.

Run it:

    pip install agentbrake-sdk[langchain] langchain
    python examples/langchain_quickstart.py

You should see a few "[AgentBrake] step N" lines, then a clean
"🛑 STOPPED — loop detected" and the run ending safely — well before LangGraph's
own recursion limit would have tripped.
"""

from typing import Any, List, Optional

from agentbrake import AgentBrakeError, LangChainBrakeMiddleware

try:
    from langchain.agents import create_agent
    from langchain_core.callbacks import CallbackManagerForLLMRun
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, BaseMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from langchain_core.tools import tool
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "This example needs LangChain 1.x:\n"
        "    pip install agentbrake-sdk[langchain] langchain\n"
        f"(import error: {e})"
    )


@tool
def search(query: str) -> str:
    """Search the web. In a real loop this would be a paid API call."""
    return "no useful result"


class LoopModel(BaseChatModel):
    """A fake model that always asks to call `search` with the SAME args.

    Stands in for a real model that never reaches a stopping condition — the
    exact shape of an expensive runaway loop, but free and offline.
    """

    @property
    def _llm_type(self) -> str:
        return "agentbrake-loop-demo"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "LoopModel":
        return self  # accept and ignore — we always emit the same tool call

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
                {
                    "name": "search",
                    "args": {"query": "pancakes"},
                    "id": "call_x",
                    "type": "tool_call",
                }
            ],
        )
        return ChatResult(generations=[ChatGeneration(message=msg)])


def main() -> None:
    # The only line you add in production: attach the brake as middleware.
    # (On LangChain 1.x, middleware can actually halt the run — a callback
    # cannot, because the framework swallows exceptions raised from callbacks.)
    brake = LangChainBrakeMiddleware(repeat_tool_limit=3, max_steps=20, verbose=True)
    agent = create_agent(LoopModel(), tools=[search], middleware=[brake])

    print("Starting agent (it's going to loop on purpose)...\n")
    try:
        agent.invoke(
            {"messages": [("user", "How do I make pancakes?")]},
            config={"recursion_limit": 100},
        )
        print("\nAgent finished on its own (unexpected for this demo).")
    except AgentBrakeError as e:
        print(f"\n✅ AgentBrake caught it: {e.reason}")
        print(f"   final stats:{e.stats.summary()}")


if __name__ == "__main__":
    main()

# AgentBrake examples

Runnable demos of the brake engaging on a real agent loop.

## `langchain_quickstart.py` — runs with NO API key

Builds a real LangChain 1.x agent (`create_agent` / LangGraph) wired to a fake
model that loops forever, and stops it with `LangChainBrakeMiddleware`.

```bash
pip install agentbrake[langchain] langchain
python examples/langchain_quickstart.py
```

Expected: a few `[AgentBrake] step N` lines, then
`🛑 STOPPED — loop detected` — well before LangGraph's own recursion limit.

> **Which LangChain class do I use?**
> - **LangChain 1.x** (`create_agent` / LangGraph): use `LangChainBrakeMiddleware`.
>   Middleware runs inside the agent graph, so it can actually halt the run.
> - **Classic `AgentExecutor`** (LangChain 0.x): use the `LangChainBrake`
>   callback (`config={"callbacks": [brake]}`).
>
> On LangChain 1.x, callbacks are observe-only — the framework swallows
> exceptions raised from them — which is why the middleware exists.

## `crewai_quickstart.py` — needs a real LLM key

A meaningful CrewAI run needs a real model, so this shows the production wiring
and runs a tiny real crew.

```bash
pip install agentbrake crewai
export OPENAI_API_KEY=sk-...
python examples/crewai_quickstart.py
```

Wire-in is two lines — construct your crew, then `CrewAIBrake(...).install()`
right before `crew.kickoff()`. The brake is verified against the real CrewAI
library in `tests/test_crewai.py`.

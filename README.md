# 🛑 AgentBrake

**The emergency brake for multi-agent systems.**
Stop runaway LangChain & CrewAI agents in real time — *before* 50 cents turns into $47,000.

```bash
pip install agentbrake-sdk
```

> The install name is `agentbrake-sdk`; you import it as `agentbrake`.

---

## The problem

In November 2025, four LangChain agents entered an infinite loop. They ran for 11 days. The bill was **$47,000**. Nobody noticed until it was over.

This is not rare. Autonomous agents fail *expensively* rather than loudly:

- An agent calls the same tool **14,000 times** with identical arguments.
- A planner expands one simple task into dozens of high-context subagent calls.
- A reasoning loop never hits its stopping condition and runs all night.

Observability tools **record** this. They don't **stop** it. By the time the alert fires — or someone reads it — the money is gone. The gap between "the alert fired" and "the run stopped" is exactly where the damage compounds.

**AgentBrake closes that gap. It intercepts, not just observes.**

---

## How it works

AgentBrake hooks into your agent's execution and watches every step in real time. When a run crosses a limit you set, it raises a clean exception that **halts the agent before the next expensive call goes out.**

```python
from agentbrake import LangChainBrakeMiddleware
from langchain.agents import create_agent

agent = create_agent(
    model, tools=tools,
    middleware=[LangChainBrakeMiddleware(max_cost_usd=2.00, repeat_tool_limit=5)],
)
```

That's it. One line.

---

## What it catches

| Runaway pattern | How AgentBrake stops it |
|---|---|
| **Identical-tool loops** (same call, same args, over and over) | `repeat_tool_limit` — trips after N identical calls in a row |
| **Cost blowouts** (the $47k overnight run) | `max_cost_usd` — a hard ceiling, enforced live as tokens are spent |
| **Endless reasoning** (no stopping condition) | `max_steps` — caps total reasoning steps |
| **Tool-call storms** | `max_tool_calls` — caps total tool invocations |
| **Hung runs** | `max_duration_s` — wall-clock ceiling |

It warns at 80% of any limit, and stops at 100%.

---

## LangChain

LangChain has two agent stacks, and they intercept differently — AgentBrake
ships the right tool for each.

**LangChain 1.x** (`create_agent` / LangGraph) — use the middleware. It runs
inside the agent graph, so it can actually halt the run:

```python
from agentbrake import LangChainBrakeMiddleware, AgentBrakeError
from langchain.agents import create_agent

agent = create_agent(
    model, tools=tools,
    middleware=[LangChainBrakeMiddleware(max_cost_usd=2.00, repeat_tool_limit=5, max_steps=30)],
)

try:
    agent.invoke({"messages": [("user", "...")]})
except AgentBrakeError as e:
    print(f"Stopped safely: {e.reason}")
```

**Classic `AgentExecutor`** (LangChain 0.x) — use the callback:

```python
from agentbrake import LangChainBrake, AgentBrakeError

brake = LangChainBrake(
    max_cost_usd=2.00,
    repeat_tool_limit=5,
    max_steps=30,
)

try:
    agent_executor.invoke({"input": "..."}, config={"callbacks": [brake]})
except AgentBrakeError as e:
    print(f"Stopped safely: {e.reason}")
```

## CrewAI

```python
from agentbrake import CrewAIBrake, AgentBrakeError

CrewAIBrake(max_cost_usd=3.00, repeat_tool_limit=5).install()

try:
    crew.kickoff()
except AgentBrakeError as e:
    print(f"Crew stopped safely: {e.reason}")
```

---

## Live cost visibility

Every run prints where your money is going, step by step:

```
[AgentBrake] step 1: web_search · running cost $0.0080
[AgentBrake] step 2: web_search · running cost $0.0160
[AgentBrake] ⚠️  approaching cost limit (1.60 of 2.00)
[AgentBrake] 🛑 STOPPED — loop detected: same tool call repeated 5× in a row
  steps=5 tool_calls=5 llm_calls=4 tokens=9,200 cost=$0.032 elapsed=0.4s
```

---

## Pricing built in

AgentBrake ships with current pricing for GPT-4o, GPT-4, Claude (Opus/Sonnet/Haiku), and Gemini, so cost ceilings work out of the box. Override anytime with your own rates.

---

## Why not just set a provider spend cap?

Provider caps are **monthly** and **account-wide** — they fire after the damage, across everything. AgentBrake is **per-run** and **in-process** — it stops *this* agent *now*, before the next call. It's the difference between a smoke alarm and a sprinkler.

---

## License

MIT — free to use, including commercially.

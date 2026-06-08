# 🛑 AgentBrake

**The emergency brake for multi-agent systems.**
Stop runaway LangChain & CrewAI agents in real time — *before* 50 cents turns into $47,000.

```bash
pip install agentbrake-sdk
```

> The install name is `agentbrake-sdk`; you import it as `agentbrake`.

![AgentBrake halting a runaway agent at a cost ceiling](demo/agentbrake.gif)

*A runaway agent racking up cost, stopped the moment it crosses your ceiling, before the bill grows. There's also a [no-API-key example](examples/langchain_quickstart.py) that brakes a real LangGraph loop you can run yourself.*

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
[AgentBrake] step 1: web_search · running cost $0.4000
[AgentBrake] step 2: web_search · running cost $0.8000
[AgentBrake] step 3: web_search · running cost $1.2000
[AgentBrake] step 4: web_search · running cost $1.6000
[AgentBrake] ⚠️  approaching cost limit (1.60 of 2.0)
[AgentBrake] step 5: web_search · running cost $2.0000
[AgentBrake] 🛑 STOPPED — cost ceiling reached ($2.00 ≥ $2.00)
  steps=5 tool_calls=5 llm_calls=5 cost=$2.0000 elapsed=6.2s
```

---

## Pricing built in

AgentBrake ships with current pricing for GPT-4o, GPT-4, Claude (Opus/Sonnet/Haiku), and Gemini, so cost ceilings work out of the box. Override anytime with your own rates.

---

## Why not just set a provider spend cap?

Provider caps are **monthly** and **account-wide** — they fire after the damage, across everything. AgentBrake is **per-run** and **in-process** — it stops *this* agent *now*, before the next call. It's the difference between a smoke alarm and a sprinkler.

---

## License

[FSL-1.1-MIT](LICENSE) (Functional Source License). Free to use, modify and
self-host for any purpose, **except** building a competing commercial product or
service. Each release converts automatically to the MIT license two years after
it ships. (Versions 0.1.0 and 0.1.1 were released under MIT and stay MIT.)

Because AgentBrake runs **in-process** (no proxy, no gateway), your prompts and
data never leave your environment, and the overhead is measured in microseconds.
Privacy by design, near-zero added latency.

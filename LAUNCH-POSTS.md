# AgentBrake — launch posts (copy-paste ready)

Honest hooks, no hype. The strongest, most defensible angle we have is real:
**AgentBrake actually works on the *current* major versions** — LangChain 1.x
(LangGraph) and CrewAI 1.x — where most cost-guard snippets silently don't,
because (a) LangGraph swallows exceptions raised from callbacks, so a callback
can watch a loop but can't stop it, and (b) CrewAI 1.x moved LLM calls behind a
provider factory. Lead with the $47k story; back it with that technical truth.

Status: both paths are verified end-to-end. LangChain — the no-API-key example
brakes a real LangGraph loop. CrewAI — a live run on real OpenAI confirmed the
brake halts crew.kickoff() (and tracks real tokens/cost). Still say plainly that
it's early (v0.1.x); HN/Reddit reward that honesty.

---

## Hacker News — "Show HN"

**Title** (≤80 chars):

```
Show HN: AgentBrake – stop runaway LangChain/CrewAI agents in real time
```

**First comment (post immediately after submitting):**

```
Hi HN, I built AgentBrake after reading about a LangChain agent loop that ran
for 11 days and cost $47,000 before anyone noticed.

Observability tools record runaway agents; they don't stop them. AgentBrake is
an in-process brake: you give it limits (cost ceiling, identical-tool-loop
detection, max steps/tool-calls/duration) and it raises a clean exception that
halts the run before the next expensive call goes out.

    pip install agentbrake-sdk   # imports as `agentbrake`

LangChain 1.x (create_agent / LangGraph):

    from agentbrake import LangChainBrakeMiddleware
    agent = create_agent(model, tools=tools,
                         middleware=[LangChainBrakeMiddleware(max_cost_usd=2.0, repeat_tool_limit=5)])

The thing I didn't expect while building this: on LangChain 1.x you can't brake
from a callback at all — LangGraph runs callbacks as observers and swallows any
exception they raise, so the run just keeps going. You have to hook the agent
graph via middleware. CrewAI 1.x has a related gotcha: LLM calls now go through a
provider factory, so the obvious patch point is dead. A lot of the cost-guard
snippets floating around were written against the old APIs and quietly no-op on
the current versions. AgentBrake is built and tested against langchain 1.3 and
crewai 1.14.

Honest status: both paths are verified end-to-end. There's an example that
brakes a real LangGraph loop with no API key, and a live run on real OpenAI
confirmed the brake halts a CrewAI crew.kickoff() while tracking real
tokens/cost. It's early (v0.1.x) and MIT licensed.

Repo: https://github.com/marcoschulz7/agentbrake
PyPI: https://pypi.org/project/agentbrake-sdk/

Would love feedback — especially on other runaway patterns worth detecting, and
on whether the middleware approach holds up across your LangGraph setups.
```

---

## Reddit — r/LangChain

**Title:**

```
I built a one-line brake that stops runaway agent loops (and actually works on LangChain 1.x / LangGraph)
```

**Body:**

```
A LangChain agent loop once ran for 11 days and cost $47k before anyone caught
it. Observability records that; it doesn't stop it. So I built AgentBrake — an
in-process brake that halts a run when it crosses limits you set: cost ceiling,
identical-tool-loop detection, max steps / tool-calls / duration.

    pip install agentbrake-sdk

    from agentbrake import LangChainBrakeMiddleware
    agent = create_agent(model, tools=tools,
        middleware=[LangChainBrakeMiddleware(max_cost_usd=2.0, repeat_tool_limit=5)])

One thing worth flagging for this sub specifically: on LangChain 1.x you cannot
stop a run from a callback — LangGraph treats callbacks as observers and
swallows exceptions raised from them, so the agent keeps looping. You have to go
through middleware, which runs inside the graph. AgentBrake ships both: the
middleware for 1.x / create_agent, and the classic callback for 0.x
AgentExecutor.

There's a runnable example in the repo that brakes a real LangGraph loop with no
API key, if you want to see it engage before wiring it into your own agent.

MIT, feedback very welcome (especially on loop patterns I should detect):
https://github.com/marcoschulz7/agentbrake
```

---

## Reddit — r/CrewAI and r/AI_Agents

**Title:**

```
Stop CrewAI agents from burning your budget in a loop — one-line in-process brake
```

**Body:**

```
Built this after the $47k LangChain-loop story going around. AgentBrake is a
real-time brake for agent runs: cost ceiling + identical-tool-loop detection +
step/tool/duration limits, enforced in-process so it halts before the next
expensive call.

    pip install agentbrake-sdk

    from agentbrake import CrewAIBrake
    CrewAIBrake(max_cost_usd=3.0, repeat_tool_limit=5).install()   # before kickoff

CrewAI-specific note: 1.x routes LLM calls through a provider factory
(OpenAICompletion, etc.), so the naive "patch LLM.call" guards you'll find don't
fire anymore. AgentBrake patches the actual provider classes + ToolUsage, tested
against crewai 1.14. Loop / step / tool / duration limits are solid; cost
accuracy depends on the provider reporting tokens.

MIT, repo + examples: https://github.com/marcoschulz7/agentbrake
Happy to answer anything / take feature requests.
```

---

## X / Twitter — thread

```
1/ A LangChain agent once cost someone $47,000 overnight.

It entered a loop, ran for 11 days, and nobody noticed until the bill came.

I built the 1-line fix. It's open source. 🧵

2/ The problem isn't that agents fail. It's that they fail *expensively and
quietly*:

- same tool called 14,000× with identical args
- a reasoning loop that never hits its stop condition
- an overnight run that just... keeps going

Your dashboard records it. It doesn't stop it.

3/ AgentBrake is an in-process brake. You set limits, it halts the run before
the next expensive call:

    pip install agentbrake-sdk

cost ceiling · identical-loop detection · max steps / tool-calls / duration.
Warns at 80%, stops at 100%.

4/ The part I didn't expect:

On LangChain 1.x (LangGraph), you CAN'T stop a run from a callback — the
framework swallows the exception and keeps looping.

Most cost-guard snippets out there were written for the old API and quietly
no-op now. AgentBrake uses middleware, so it actually brakes.

5/ Same story on CrewAI 1.x: LLM calls moved behind a provider factory, so the
obvious patch point is dead. AgentBrake patches the real provider classes.

Built + tested against langchain 1.3 and crewai 1.14.

6/ It's MIT. There's a demo you can run with no API key that brakes a real
LangGraph loop at step 3.

Repo: github.com/marcoschulz7/agentbrake

If you run agents in prod, I'd love your runaway-loop war stories 👇
```

---

## Discord one-liner (LangChain / CrewAI #show-and-tell)

```
Made a small MIT tool — AgentBrake — that halts a run when it loops or blows a
cost ceiling. The bit that mattered: on LangChain 1.x a callback can't stop the
run (LangGraph swallows the exception), so it hooks the graph via middleware
instead. `pip install agentbrake-sdk` · github.com/marcoschulz7/agentbrake —
feedback welcome.
```

---

## Posting checklist

- [ ] Record the demo (see DEMO.md) and attach the GIF to HN/Reddit/X — the
      "step 1, 2, 3 → 🛑 STOPPED" moment is the whole pitch in 5 seconds.
- [ ] HN: post Tue–Thu, ~8am US Pacific (≈17:00 CET). Stay online all day,
      reply to every comment.
- [ ] Don't cross-post everything in one hour — space it out, lead with HN.
- [ ] When anyone says "this would've saved me $X", ask for a one-line quote.
```

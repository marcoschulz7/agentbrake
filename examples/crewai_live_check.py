"""
CrewAI LIVE end-to-end check — proves the brake fires against the real CrewAI
runtime and a real LLM provider, for a fraction of a cent.

It runs a tiny real crew on gpt-4o-mini with a deliberately tiny cost ceiling, so
AgentBrake trips right after the first real LLM call. That exercises the full
path: real CrewAI kickoff -> real OpenAI call -> tokens tracked from the
provider -> brake raises and halts the crew.

Run:
    export OPENAI_API_KEY=sk-...
    python examples/crewai_live_check.py

Expected: a "[AgentBrake] installed" line, then a clean
"🛑 STOPPED — cost ceiling reached", with real token/cost numbers in the stats.
"""

import os

from agentbrake import AgentBrakeError, CrewAIBrake

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Set OPENAI_API_KEY first:  export OPENAI_API_KEY=sk-...")

try:
    from crewai import Agent, Crew, Task
except Exception as e:  # pragma: no cover
    raise SystemExit(f"Needs crewai installed (pip install crewai). {e}")


def build_crew() -> "Crew":
    analyst = Agent(
        role="Analyst",
        goal="Answer in exactly one short sentence.",
        backstory="You are terse and precise.",
        llm="gpt-4o-mini",          # cheap model: keeps this check near-free
        verbose=False,
    )
    task = Task(
        description="What is a runaway agent loop? One sentence.",
        expected_output="One sentence.",
        agent=analyst,
    )
    return Crew(agents=[analyst], tasks=[task], verbose=False)


def main() -> None:
    crew = build_crew()

    # Tiny ceiling on purpose: the first real LLM call already exceeds it, so the
    # brake engages end-to-end. (In production you'd set a real dollar amount.)
    CrewAIBrake(max_cost_usd=0.000001, repeat_tool_limit=5).install()

    try:
        result = crew.kickoff()
        print("\nCrew finished (ceiling not hit — raise it to see a real answer):")
        print(result)
    except AgentBrakeError as e:
        print(f"\n✅ END-TO-END VERIFIED — brake fired on a real crew: {e.reason}")
        print(f"   real provider stats:{e.stats.summary()}")


if __name__ == "__main__":
    main()

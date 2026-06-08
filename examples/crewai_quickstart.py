"""
AgentBrake × CrewAI — quickstart.

Unlike the LangChain example, a meaningful CrewAI demo runs a real crew, which
needs a real LLM (and an API key). So this file shows the exact production
wiring. The brake itself is verified against the real CrewAI library in
tests/test_crewai.py — including the loop detector and the cost ceiling.

Run it (costs a few cents of real tokens):

    pip install agentbrake-sdk crewai
    export OPENAI_API_KEY=sk-...
    python examples/crewai_quickstart.py

What to wire in your own code is just two lines:

    from agentbrake import CrewAIBrake
    CrewAIBrake(max_cost_usd=3.0, repeat_tool_limit=5).install()   # before kickoff

Important: call .install() AFTER your agents/LLMs are constructed (CrewAI lazy-
loads provider classes), i.e. right before crew.kickoff().
"""

from agentbrake import AgentBrakeError, CrewAIBrake

try:
    from crewai import Agent, Crew, Task
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "This example needs CrewAI:\n"
        "    pip install agentbrake-sdk crewai\n"
        f"(import error: {e})"
    )


def build_crew() -> "Crew":
    researcher = Agent(
        role="Researcher",
        goal="Answer the question concisely.",
        backstory="You are a focused analyst who avoids busywork.",
        verbose=False,
    )
    task = Task(
        description="In two sentences, explain what a runaway agent loop is.",
        expected_output="A two-sentence explanation.",
        agent=researcher,
    )
    return Crew(agents=[researcher], tasks=[task], verbose=False)


def main() -> None:
    crew = build_crew()

    # The brake: a hard per-run ceiling and a loop detector. Installed right
    # before kickoff so every provider class in use is already imported.
    CrewAIBrake(max_cost_usd=3.0, repeat_tool_limit=5, max_steps=30).install()

    try:
        result = crew.kickoff()
        print("\nCrew finished within limits:\n", result)
    except AgentBrakeError as e:
        print(f"\n✅ Crew stopped safely by AgentBrake: {e.reason}")
        print(f"   final stats:{e.stats.summary()}")


if __name__ == "__main__":
    main()

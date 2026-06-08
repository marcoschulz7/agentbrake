# Changelog

All notable changes to AgentBrake are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — unreleased

First public release.

### Added
- **Framework-agnostic engine** (`core`): live loop detection (identical
  tool+args repeated N times), cost ceiling, step / tool-call / duration limits,
  warn-at-80%, built-in pricing for GPT-4o, GPT-4, Claude, and Gemini.
- **LangChain 1.x support** via `LangChainBrakeMiddleware` — runs inside the
  `create_agent` / LangGraph execution graph, so it can actually halt a run.
- **Classic LangChain (0.x) support** via the `LangChainBrake` callback for
  `AgentExecutor`.
- **CrewAI 1.x support** via `CrewAIBrake` — patches every provider completion
  class plus `ToolUsage._use`, with per-instance token-delta cost accounting.
- Runnable examples for both frameworks (LangChain demo needs no API key).
- Test suite covering the engine and both framework integrations against the
  real `langchain` 1.3 and `crewai` 1.14 libraries.

### Notes
- On LangChain 1.x, callbacks are observe-only (the framework swallows
  exceptions raised from them) — use `LangChainBrakeMiddleware` to brake, not the
  callback. See the README for the 1.x-vs-0.x guidance.
- CrewAI cost accuracy depends on the provider reporting token usage; without it
  the brake falls back to a rough length-based estimate while all other limits
  (loop, steps, tool-calls, duration) remain exact.

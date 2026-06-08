"""
CrewAI adapter for AgentBrake.

CrewAI doesn't expose the same clean callback surface as LangChain, so we do
what NVIDIA's own toolkit does: monkey-patch the two methods that matter —
the LLM call and the tool-usage call — to route through our engine first.

Usage (one line):

    from agentbrake import CrewAIBrake

    CrewAIBrake(max_cost_usd=3.0).install()
    # ... build and run your crew as normal ...

When a threshold trips, AgentBrakeError is raised from inside the patched
method, which unwinds the crew's execution loop and stops further LLM spend.
"""

from __future__ import annotations

from typing import Any, Optional

from .core import BrakeConfig, BrakeEngine, RunStats


def _default_warn(msg: str, stats: RunStats) -> None:
    print(f"\033[33m[AgentBrake] ⚠️  {msg}\033[0m")


def _default_stop(reason: str, stats: RunStats) -> None:
    print(f"\033[31m[AgentBrake] 🛑 STOPPED — {reason}\033[0m")
    print(f"\033[31m{stats.summary()}\033[0m")


class CrewAIBrake:
    def __init__(
        self,
        max_cost_usd: Optional[float] = 5.0,
        max_steps: Optional[int] = 50,
        max_tool_calls: Optional[int] = 100,
        max_duration_s: Optional[float] = 600.0,
        repeat_tool_limit: Optional[int] = 5,
        verbose: bool = True,
        pricing: Optional[dict] = None,
    ):
        config = BrakeConfig(
            max_cost_usd=max_cost_usd,
            max_steps=max_steps,
            max_tool_calls=max_tool_calls,
            max_duration_s=max_duration_s,
            repeat_tool_limit=repeat_tool_limit,
        )
        self.engine = BrakeEngine(
            config=config,
            pricing=pricing,
            on_warn=_default_warn if verbose else None,
            on_stop=_default_stop if verbose else None,
        )
        self.verbose = verbose
        self._installed = False
        self._orig_tool_use = None
        # CrewAI 1.x routes LLM calls through provider-specific subclasses
        # (OpenAICompletion, AnthropicCompletion, ...), each overriding call().
        # We patch every class that owns a synchronous call(), keyed class->orig.
        self._orig_llm_calls: dict = {}
        # CrewAI keeps a *cumulative* token tally per LLM instance, so we record
        # the last-seen totals per instance and feed the engine only the delta
        # of each call. Keyed by id(llm) because a crew can run several LLMs.
        self._usage_seen: dict = {}

    def install(self) -> "CrewAIBrake":
        """Patch CrewAI's tool-usage and LLM-call paths. Idempotent.

        Call this *after* your agents/LLMs are constructed (e.g. right before
        crew.kickoff()). CrewAI lazy-imports provider classes, so installing
        after construction guarantees the provider you actually use is patched.
        """
        if self._installed:
            return self
        try:
            from crewai.tools.tool_usage import ToolUsage
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "CrewAIBrake.install() needs `crewai` installed. "
                "Run: pip install crewai"
            ) from e

        engine = self.engine
        verbose = self.verbose

        # --- patch tool usage ---
        self._orig_tool_use = ToolUsage._use

        def _patched_use(self_tu, *args, **kwargs):
            # Signature-agnostic: CrewAI 1.x calls _use(tool_string=, tool=,
            # calling=) by keyword, but argument order has shifted between
            # versions. Pull what we need from either kwargs or positional args
            # and pass everything through untouched.
            tool_string = kwargs.get("tool_string")
            tool = kwargs.get("tool")
            if tool_string is None and len(args) >= 1:
                tool_string = args[0]
            if tool is None and len(args) >= 2:
                tool = args[1]
            name = getattr(tool, "name", "") or str(tool_string or "")[:40]
            tool_input = str(tool_string or "")
            engine.record_step()
            engine.record_tool(name, tool_input)
            if verbose:
                print(f"\033[36m[AgentBrake] tool '{name}' · "
                      f"step {engine.stats.steps} · "
                      f"${engine.stats.cost_usd:.4f}\033[0m")
            engine.check()
            return CrewAIBrake._call_original(
                self._orig_tool_use, self_tu, *args, **kwargs
            )

        ToolUsage._use = _patched_use

        # --- patch every LLM class that owns a synchronous call() ---
        # We wrap the *original* of each class. Because some classes share the
        # same inherited call(), we dedupe by the underlying function so a call
        # is never recorded twice.
        def _make_llm_wrapper(orig):
            def _patched_call(self_llm, *args, **kwargs):
                result = CrewAIBrake._call_original(orig, self_llm, *args, **kwargs)
                model = getattr(self_llm, "model", "") or ""
                in_tok, out_tok = self._extract_call_tokens(self_llm)
                # fallback: rough estimate from length if no usage was reported
                if not (in_tok or out_tok):
                    out_tok = max(1, len(str(result)) // 4)
                engine.record_llm(model, in_tok, out_tok)
                engine.check()
                return result
            return _patched_call

        for klass in self._llm_call_owners():
            orig = klass.__dict__["call"]
            self._orig_llm_calls[klass] = orig
            klass.call = _make_llm_wrapper(orig)

        self._installed = True
        if verbose:
            n = len(self._orig_llm_calls)
            print(f"\033[32m[AgentBrake] installed — watching this crew "
                  f"({n} LLM provider(s) + tools).\033[0m")
        return self

    @staticmethod
    def _llm_call_owners() -> list:
        """All currently-imported CrewAI LLM classes that define their own
        call(): the provider completions (OpenAI/Anthropic/Gemini/...) plus the
        base classes as a fallback. Patching each is what makes the brake fire
        regardless of provider, since CrewAI's LLM(...) is a factory that hands
        back a provider subclass rather than a base LLM."""
        owners: list = []
        seen = set()

        def _add(klass):
            if klass is not None and "call" in klass.__dict__ and klass not in seen:
                seen.add(klass)
                owners.append(klass)

        bases = []
        try:
            from crewai.llms.base_llm import BaseLLM
            bases.append(BaseLLM)
        except Exception:  # pragma: no cover - older crewai layout
            pass
        try:
            from crewai.llm import LLM
            bases.append(LLM)
        except Exception:  # pragma: no cover
            pass

        def _walk(klass):
            _add(klass)
            for sub in klass.__subclasses__():
                _walk(sub)

        for b in bases:
            _walk(b)
        return owners

    def uninstall(self) -> None:
        """Restore original CrewAI methods. Useful in tests."""
        if not self._installed:
            return
        from crewai.tools.tool_usage import ToolUsage
        if self._orig_tool_use:
            ToolUsage._use = self._orig_tool_use
        for klass, orig in self._orig_llm_calls.items():
            klass.call = orig
        self._orig_llm_calls = {}
        self._installed = False

    def _extract_call_tokens(self, llm: Any) -> tuple:
        """Return (input_tokens, output_tokens) for the most recent LLM call.

        CrewAI 1.x stores a *cumulative* per-instance tally in `_token_usage`
        ({'prompt_tokens', 'completion_tokens', ...}), so we diff against the
        last total we saw for this instance. Older CrewAI exposed a per-call
        `_last_usage` dict — we fall back to that, then to (0, 0) so the caller
        can length-estimate. Never raises; usage tracking must not break a run.
        """
        try:
            cumulative = getattr(llm, "_token_usage", None)
            if isinstance(cumulative, dict):
                cur_in = int(cumulative.get("prompt_tokens", 0) or 0)
                cur_out = int(cumulative.get("completion_tokens", 0) or 0)
                key = id(llm)
                prev_in, prev_out = self._usage_seen.get(key, (0, 0))
                self._usage_seen[key] = (cur_in, cur_out)
                in_tok = max(0, cur_in - prev_in)
                out_tok = max(0, cur_out - prev_out)
                if in_tok or out_tok:
                    return in_tok, out_tok

            # Backward-compat: older CrewAI per-call usage shape.
            last = getattr(llm, "_last_usage", None)
            if isinstance(last, dict):
                in_tok = int(last.get("prompt_tokens", 0) or last.get("input_tokens", 0) or 0)
                out_tok = int(last.get("completion_tokens", 0) or last.get("output_tokens", 0) or 0)
                return in_tok, out_tok
        except Exception:
            pass
        return 0, 0

    @staticmethod
    def _call_original(fn, *args, **kwargs):
        # bound vs unbound safety wrapper
        return fn(*args, **kwargs)

    def __enter__(self):
        return self.install()

    def __exit__(self, *exc):
        self.uninstall()
        return False

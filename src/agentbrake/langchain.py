"""
LangChain adapter for AgentBrake.

Usage (one line to wire in):

    from agentbrake import LangChainBrake

    brake = LangChainBrake(max_cost_usd=2.0)
    agent_executor.invoke({"input": "..."}, config={"callbacks": [brake]})

LangChain's callback system gives us hooks on every meaningful event. We map:
  on_tool_start  -> a reasoning step + a tool invocation (count + loop fingerprint)
  on_llm_end     -> token usage (cost tracking)
After each, we call engine.check(), which raises AgentBrakeError to halt the run.
Because the exception propagates out of the callback, LangChain stops calling
the model — the brake engages *before* the next expensive request.

Why on_tool_start and not on_agent_action? The classic AgentExecutor emitted
on_agent_action, but LangChain 1.x agents (create_agent / LangGraph) do not —
they only emit on_tool_start / on_llm_end. on_tool_start fires in BOTH the
classic and the 1.x agent stacks, so recording there keeps loop, step and
tool-count limits working across versions. (Verified against langchain 1.3.)
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from langchain_core.callbacks.base import BaseCallbackHandler
except Exception:  # pragma: no cover - allows import without langchain installed
    class BaseCallbackHandler:  # type: ignore
        """Fallback stub so `import agentbrake` works without LangChain present."""
        pass

try:
    # LangChain 1.x: the middleware API runs *inside* the agent's execution
    # graph, so raising from it actually halts the run (callbacks do not).
    from langchain.agents.middleware import AgentMiddleware
except Exception:  # pragma: no cover - langchain<1.0 or not installed
    class AgentMiddleware:  # type: ignore
        """Fallback stub so `import agentbrake` works without LangChain 1.x."""
        def __init__(self, *args, **kwargs):
            pass

from .core import BrakeConfig, BrakeEngine, RunStats


def _default_warn(msg: str, stats: RunStats) -> None:
    print(f"\033[33m[AgentBrake] ⚠️  {msg}\033[0m")


def _default_stop(reason: str, stats: RunStats) -> None:
    print(f"\033[31m[AgentBrake] 🛑 STOPPED — {reason}\033[0m")
    print(f"\033[31m{stats.summary()}\033[0m")


class LangChainBrake(BaseCallbackHandler):
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

    # --- LangChain hooks ----------------------------------------------------

    def on_tool_start(self, serialized: Any, input_str: str, **kwargs: Any) -> None:
        # The single source of truth for tool/step recording. Fires in both the
        # classic AgentExecutor and the LangChain 1.x (LangGraph) agent stacks.
        name = ""
        if isinstance(serialized, dict):
            name = serialized.get("name") or serialized.get("id") or ""
        elif serialized:
            name = str(serialized)
        name = name or "tool"
        self.engine.record_step()
        self.engine.record_tool(str(name), str(input_str or ""))
        if self.verbose:
            print(f"\033[36m[AgentBrake] step {self.engine.stats.steps}: "
                  f"{name} · running cost ${self.engine.stats.cost_usd:.4f}\033[0m")
        self.engine.check()

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        model, in_tok, out_tok = self._extract_usage(response)
        self.engine.record_llm(model, in_tok, out_tok)
        self.engine.check()

    # --- usage extraction (LangChain's shape varies by provider) ------------

    @staticmethod
    def _extract_usage(response: Any) -> tuple[str, int, int]:
        model = ""
        in_tok = out_tok = 0
        try:
            llm_output = getattr(response, "llm_output", None) or {}
            model = llm_output.get("model_name") or llm_output.get("model") or ""
            usage = (
                llm_output.get("token_usage")
                or llm_output.get("usage")
                or {}
            )
            in_tok = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
            out_tok = usage.get("completion_tokens") or usage.get("output_tokens") or 0

            # newer LangChain puts usage on the message itself
            if not (in_tok or out_tok):
                gens = getattr(response, "generations", []) or []
                for batch in gens:
                    for gen in batch:
                        msg = getattr(gen, "message", None)
                        meta = getattr(msg, "usage_metadata", None) if msg else None
                        if meta:
                            in_tok += meta.get("input_tokens", 0)
                            out_tok += meta.get("output_tokens", 0)
        except Exception:
            pass
        return model, int(in_tok or 0), int(out_tok or 0)


class LangChainBrakeMiddleware(AgentMiddleware):
    """AgentBrake for LangChain 1.x agents (create_agent / LangGraph).

    Why a second class? LangChain 1.x runs callbacks as fire-and-forget
    observers: an exception raised from a callback is logged and *swallowed*, so
    the classic ``LangChainBrake`` callback can watch a run but cannot stop one.
    Middleware, by contrast, runs *inside* the agent's execution graph — raising
    from it unwinds the run. So this is the class that actually brakes on 1.x.

    Usage:

        from agentbrake import LangChainBrakeMiddleware, AgentBrakeError
        from langchain.agents import create_agent

        agent = create_agent(
            model, tools=tools,
            middleware=[LangChainBrakeMiddleware(max_cost_usd=2.0)],
        )
        try:
            agent.invoke({"messages": [("user", "...")]})
        except AgentBrakeError as e:
            print(f"Stopped safely: {e.reason}")

    Use the callback ``LangChainBrake`` for the classic AgentExecutor (0.x).
    """

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
        super().__init__()
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

    # --- middleware hooks (run synchronously inside the agent graph) ---------

    def wrap_tool_call(self, request: Any, handler: Any) -> Any:
        """Runs before each tool executes. We check *first*, so the brake stops
        the run before the next (possibly expensive) tool call goes out."""
        self.engine.check()  # re-raise immediately if already stopped
        name, args = self._tool_call_fields(request)
        self.engine.record_step()
        self.engine.record_tool(name, args)
        if self.verbose:
            print(f"\033[36m[AgentBrake] step {self.engine.stats.steps}: "
                  f"{name} · running cost ${self.engine.stats.cost_usd:.4f}\033[0m")
        self.engine.check()  # raises AgentBrakeError -> unwinds the agent
        return handler(request)

    def wrap_model_call(self, request: Any, handler: Any) -> Any:
        """Wraps each model call. Enforce ceilings before spending again, then
        record this call's tokens and re-check."""
        self.engine.check()  # stop before another paid model call if over budget
        response = handler(request)
        model, in_tok, out_tok = self._usage_from_response(response)
        self.engine.record_llm(model, in_tok, out_tok)
        self.engine.check()
        return response

    # --- extraction helpers --------------------------------------------------

    @staticmethod
    def _tool_call_fields(request: Any) -> tuple[str, str]:
        tc = getattr(request, "tool_call", None)
        if isinstance(tc, dict):
            name = tc.get("name") or tc.get("id") or "tool"
            args = tc.get("args", "")
        else:
            name = getattr(tc, "name", "") or "tool"
            args = getattr(tc, "args", "")
        return str(name), str(args)

    @staticmethod
    def _usage_from_response(response: Any) -> tuple[str, int, int]:
        """Pull (model, input_tokens, output_tokens) from a middleware model
        response. LangChain 1.x returns messages carrying usage_metadata."""
        model = ""
        in_tok = out_tok = 0
        try:
            msgs = getattr(response, "result", None)
            if msgs is None:
                msgs = response if isinstance(response, (list, tuple)) else []
            for m in msgs or []:
                meta = getattr(m, "usage_metadata", None)
                if meta:
                    in_tok += meta.get("input_tokens", 0) or 0
                    out_tok += meta.get("output_tokens", 0) or 0
                if not model:
                    rmeta = getattr(m, "response_metadata", None) or {}
                    model = rmeta.get("model_name") or rmeta.get("model") or ""
        except Exception:
            pass
        return model, int(in_tok or 0), int(out_tok or 0)

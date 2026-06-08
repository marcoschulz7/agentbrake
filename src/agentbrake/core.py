"""
AgentBrake core — the framework-agnostic engine.

This module contains the actual logic: tracking agent activity and deciding
when to slam the brakes. It knows nothing about LangChain or CrewAI — the
framework adapters (langchain.py, crewai.py) feed events into this engine.

That separation is deliberate: when the next framework shows up, we only write
a thin adapter; the brain stays the same.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Callable, Optional


class AgentBrakeError(BaseException):
    """Raised when AgentBrake stops an agent. Catch this to handle a stop gracefully.

    Deliberately a *BaseException*, not Exception — like KeyboardInterrupt and
    SystemExit. Agent frameworks (CrewAI's task executor, LangChain's tool
    nodes) wrap execution in broad ``except Exception`` retry loops; if the brake
    were a normal Exception, those loops would swallow it and the run would keep
    going (and keep spending). As a BaseException it sails straight past
    ``except Exception`` and actually halts the run. User code still catches it
    explicitly with ``except AgentBrakeError``.
    """

    def __init__(self, reason: str, stats: "RunStats"):
        self.reason = reason
        self.stats = stats
        super().__init__(f"AgentBrake engaged: {reason}\n{stats.summary()}")


# --- Pricing -----------------------------------------------------------------
# Approximate USD per 1M tokens. Used for live cost estimation. These are
# deliberately editable — the user can override with set_pricing(). The point
# isn't accounting-grade billing, it's a real-time "are we about to torch money"
# signal, which only needs to be roughly right.
DEFAULT_PRICING = {
    # model substring (lowercased) : (input_per_mtok, output_per_mtok)
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4": (30.00, 60.00),
    "claude-opus": (15.00, 75.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-haiku": (0.80, 4.00),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    # fallback when the model is unknown
    "_default": (5.00, 15.00),
}


def _price_for(model: str, pricing: dict) -> tuple[float, float]:
    if not model:
        return pricing["_default"]
    m = model.lower()
    for key, price in pricing.items():
        if key != "_default" and key in m:
            return price
    return pricing["_default"]


@dataclass
class RunStats:
    """Live tally for a single agent run."""

    steps: int = 0
    tool_calls: int = 0
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    started_at: float = field(default_factory=time.time)
    stopped: bool = False
    stop_reason: Optional[str] = None

    @property
    def elapsed_s(self) -> float:
        return time.time() - self.started_at

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def summary(self) -> str:
        return (
            f"  steps={self.steps} tool_calls={self.tool_calls} "
            f"llm_calls={self.llm_calls} tokens={self.total_tokens:,} "
            f"cost=${self.cost_usd:.4f} elapsed={self.elapsed_s:.1f}s"
        )


@dataclass
class BrakeConfig:
    """The thresholds. Sensible defaults so it works out of the box,
    but every one is tunable."""

    max_cost_usd: Optional[float] = 5.0          # hard ceiling per run
    max_steps: Optional[int] = 50                 # max agent reasoning steps
    max_tool_calls: Optional[int] = 100           # max total tool invocations
    max_duration_s: Optional[float] = 600.0       # wall-clock ceiling (10 min)
    repeat_tool_limit: Optional[int] = 5          # identical tool call N times = loop
    warn_at_fraction: float = 0.8                 # warn when 80% of any limit hit


class BrakeEngine:
    """The decision core. Framework adapters call record_* and then check().

    on_warn / on_stop are callbacks so the adapters (and tests) can surface
    events however they like (print, log, push to a dashboard later).
    """

    def __init__(
        self,
        config: Optional[BrakeConfig] = None,
        pricing: Optional[dict] = None,
        on_warn: Optional[Callable[[str, RunStats], None]] = None,
        on_stop: Optional[Callable[[str, RunStats], None]] = None,
    ):
        self.config = config or BrakeConfig()
        self.pricing = pricing or dict(DEFAULT_PRICING)
        self.stats = RunStats()
        self.on_warn = on_warn
        self.on_stop = on_stop
        # fingerprint -> consecutive repeat count, for loop detection
        self._last_fingerprint: Optional[str] = None
        self._repeat_count: int = 0
        self._warned: set[str] = set()

    # --- recording -----------------------------------------------------------

    def record_step(self) -> None:
        self.stats.steps += 1

    def record_llm(self, model: str, input_tokens: int, output_tokens: int) -> None:
        self.stats.llm_calls += 1
        self.stats.input_tokens += max(0, input_tokens)
        self.stats.output_tokens += max(0, output_tokens)
        in_price, out_price = _price_for(model, self.pricing)
        self.stats.cost_usd += (
            input_tokens / 1_000_000 * in_price
            + output_tokens / 1_000_000 * out_price
        )

    def record_tool(self, tool_name: str, tool_input: str) -> None:
        self.stats.tool_calls += 1
        # loop detection: same tool + same input back-to-back
        fingerprint = hashlib.sha1(
            f"{tool_name}::{tool_input}".encode("utf-8", "ignore")
        ).hexdigest()
        if fingerprint == self._last_fingerprint:
            self._repeat_count += 1
        else:
            self._last_fingerprint = fingerprint
            self._repeat_count = 1

    # --- the brake ------------------------------------------------------------

    def check(self) -> None:
        """Evaluate all thresholds. Warn near limits, raise at limits.

        Once the brake has engaged, *every* subsequent check re-raises. This is
        what makes it a real kill-switch: if a framework swallowed the first
        AgentBrakeError and retried (CrewAI and others do exactly this), the next
        check stops it again — before any further work or spend."""
        if self.stats.stopped:
            raise AgentBrakeError(self.stats.stop_reason or "stopped", self.stats)

        c = self.config
        self._maybe_warn("cost", self.stats.cost_usd, c.max_cost_usd)
        self._maybe_warn("steps", self.stats.steps, c.max_steps)
        self._maybe_warn("tool_calls", self.stats.tool_calls, c.max_tool_calls)
        self._maybe_warn("duration", self.stats.elapsed_s, c.max_duration_s)

        if c.max_cost_usd is not None and self.stats.cost_usd >= c.max_cost_usd:
            self._stop(f"cost ceiling reached (${self.stats.cost_usd:.2f} ≥ ${c.max_cost_usd:.2f})")
        if c.max_steps is not None and self.stats.steps >= c.max_steps:
            self._stop(f"step limit reached ({self.stats.steps} ≥ {c.max_steps})")
        if c.max_tool_calls is not None and self.stats.tool_calls >= c.max_tool_calls:
            self._stop(f"tool-call limit reached ({self.stats.tool_calls} ≥ {c.max_tool_calls})")
        if c.max_duration_s is not None and self.stats.elapsed_s >= c.max_duration_s:
            self._stop(f"time limit reached ({self.stats.elapsed_s:.0f}s ≥ {c.max_duration_s:.0f}s)")
        if c.repeat_tool_limit is not None and self._repeat_count >= c.repeat_tool_limit:
            self._stop(
                f"loop detected: same tool call repeated {self._repeat_count}× in a row"
            )

    def _maybe_warn(self, name: str, value: float, limit: Optional[float]) -> None:
        if limit is None or name in self._warned:
            return
        if value >= limit * self.config.warn_at_fraction:
            self._warned.add(name)
            msg = f"approaching {name} limit ({value:.2f} of {limit})"
            if self.on_warn:
                self.on_warn(msg, self.stats)

    def _stop(self, reason: str) -> None:
        self.stats.stopped = True
        self.stats.stop_reason = reason
        if self.on_stop:
            self.on_stop(reason, self.stats)
        raise AgentBrakeError(reason, self.stats)

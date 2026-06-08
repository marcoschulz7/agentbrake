"""
Engine tests — the framework-agnostic brain.

These exercise BrakeEngine directly by feeding it record_* events and asserting
that check() warns near limits and raises AgentBrakeError at limits. No
LangChain or CrewAI involved here; that's the whole point of the core/adapter
split.
"""

import time

import pytest

from agentbrake import (
    AgentBrakeError,
    BrakeConfig,
    BrakeEngine,
    DEFAULT_PRICING,
)
from agentbrake.core import _price_for


def _only(**overrides):
    """A config with every limit disabled except the ones passed in.

    Keeps each test focused on a single threshold instead of accidentally
    tripping a different one.
    """
    base = dict(
        max_cost_usd=None,
        max_steps=None,
        max_tool_calls=None,
        max_duration_s=None,
        repeat_tool_limit=None,
    )
    base.update(overrides)
    return BrakeConfig(**base)


def test_loop_detection_trips_on_repeated_tool():
    eng = BrakeEngine(_only(repeat_tool_limit=3))
    with pytest.raises(AgentBrakeError) as exc:
        for _ in range(5):
            eng.record_tool("search", "same args")
            eng.check()
    assert "loop detected" in exc.value.reason
    assert eng.stats.stopped is True


def test_loop_counter_resets_on_different_input():
    eng = BrakeEngine(_only(repeat_tool_limit=3))
    # Alternating inputs must never trip the loop detector.
    for i in range(20):
        eng.record_tool("search", f"different-{i % 2}")
        eng.check()
    assert eng.stats.stopped is False
    assert eng.stats.tool_calls == 20


def test_cost_ceiling_stops_when_tokens_get_expensive():
    eng = BrakeEngine(_only(max_cost_usd=0.50))
    with pytest.raises(AgentBrakeError) as exc:
        # gpt-4o output is $10/Mtok -> 100k output tokens ~= $1.00 > $0.50
        eng.record_llm("gpt-4o", 0, 100_000)
        eng.check()
    assert "cost ceiling" in exc.value.reason


def test_step_limit_stops():
    eng = BrakeEngine(_only(max_steps=4))
    with pytest.raises(AgentBrakeError) as exc:
        for _ in range(10):
            eng.record_step()
            eng.check()
    assert "step limit" in exc.value.reason
    assert eng.stats.steps == 4


def test_tool_call_limit_stops():
    eng = BrakeEngine(_only(max_tool_calls=3))
    with pytest.raises(AgentBrakeError) as exc:
        for i in range(10):
            # unique inputs so the loop detector doesn't trip first
            eng.record_tool("search", f"q-{i}")
            eng.check()
    assert "tool-call limit" in exc.value.reason
    assert eng.stats.tool_calls == 3


def test_duration_limit_stops():
    eng = BrakeEngine(_only(max_duration_s=1.0))
    # Pretend the run started 10 seconds ago instead of sleeping in the test.
    eng.stats.started_at = time.time() - 10
    with pytest.raises(AgentBrakeError) as exc:
        eng.check()
    assert "time limit" in exc.value.reason


def test_warn_fires_at_80_percent_without_stopping():
    warnings = []
    eng = BrakeEngine(
        _only(max_cost_usd=1.0),
        on_warn=lambda msg, stats: warnings.append(msg),
    )
    # 90k output tokens on gpt-4o = $0.90 -> past 80% of $1.00, below ceiling
    eng.record_llm("gpt-4o", 0, 90_000)
    eng.check()
    assert eng.stats.stopped is False
    assert len(warnings) == 1
    assert "approaching cost limit" in warnings[0]


def test_warn_fires_only_once_per_limit():
    warnings = []
    eng = BrakeEngine(
        _only(max_steps=10),
        on_warn=lambda msg, stats: warnings.append(msg),
    )
    for _ in range(9):  # crosses 80% (8 steps) and stays there, never hits 10
        eng.record_step()
        eng.check()
    assert eng.stats.stopped is False
    assert len(warnings) == 1  # not spammed every step


def test_on_stop_callback_fires_with_reason():
    stops = []
    eng = BrakeEngine(
        _only(max_steps=2),
        on_stop=lambda reason, stats: stops.append(reason),
    )
    with pytest.raises(AgentBrakeError):
        for _ in range(5):
            eng.record_step()
            eng.check()
    assert len(stops) == 1
    assert "step limit" in stops[0]


def test_no_stop_when_comfortably_under_all_limits():
    eng = BrakeEngine(
        BrakeConfig(
            max_cost_usd=100.0,
            max_steps=100,
            max_tool_calls=100,
            max_duration_s=3600.0,
            repeat_tool_limit=50,
        )
    )
    for i in range(5):
        eng.record_step()
        eng.record_tool("search", f"q-{i}")
        eng.record_llm("gpt-4o-mini", 100, 100)
        eng.check()
    assert eng.stats.stopped is False


def test_pricing_lookup_matches_substring_and_falls_back():
    # exact-ish substrings resolve to their entry
    assert _price_for("gpt-4o", DEFAULT_PRICING) == DEFAULT_PRICING["gpt-4o"]
    assert _price_for("claude-opus-4-8", DEFAULT_PRICING) == DEFAULT_PRICING["claude-opus"]
    # unknown model and empty model both hit the default
    assert _price_for("some-unknown-model", DEFAULT_PRICING) == DEFAULT_PRICING["_default"]
    assert _price_for("", DEFAULT_PRICING) == DEFAULT_PRICING["_default"]


def test_cost_is_computed_from_real_pricing():
    eng = BrakeEngine(_only())  # all limits off, just measure cost
    # claude-sonnet: $3 in / $15 out per Mtok
    eng.record_llm("claude-sonnet", 1_000_000, 1_000_000)
    assert eng.stats.cost_usd == pytest.approx(3.0 + 15.0)
    assert eng.stats.input_tokens == 1_000_000
    assert eng.stats.output_tokens == 1_000_000
    assert eng.stats.total_tokens == 2_000_000


def test_stats_summary_is_human_readable():
    eng = BrakeEngine(_only())
    eng.record_step()
    eng.record_tool("search", "x")
    eng.record_llm("gpt-4o", 1000, 2000)
    s = eng.stats.summary()
    assert "steps=1" in s
    assert "tool_calls=1" in s
    assert "llm_calls=1" in s


def test_check_is_a_noop_after_stop():
    eng = BrakeEngine(_only(max_steps=1))
    with pytest.raises(AgentBrakeError):
        eng.record_step()
        eng.check()
    # already stopped -> calling check again must not raise again
    eng.check()
    assert eng.stats.stopped is True

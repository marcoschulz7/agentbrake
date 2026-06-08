"""
CrewAI adapter integration tests — run against the REAL crewai library.

These skip automatically when crewai isn't installed (system Python / CI), but
when it is present they verify the thing that actually breaks between CrewAI
versions: that our monkey-patch points still exist, that install()/uninstall()
work, and that the brake engages when the patched methods are driven.

We don't make live LLM calls. Instead we swap in a fake "original" for each
patched method *before* installing the brake, so the brake wraps our fake. That
exercises the wrapper + engine wiring against crewai's real class objects
without a network call or API key.
"""

import pytest

crewai = pytest.importorskip("crewai")

from crewai.llm import LLM
from crewai.tools.tool_usage import ToolUsage

from agentbrake import AgentBrakeError, CrewAIBrake


def _provider_class():
    """The concrete provider class CrewAI 1.x actually runs (OpenAICompletion),
    obtained via the LLM(...) factory. This is the class that owns call()."""
    return type(LLM(model="gpt-4o"))


def test_patch_points_still_exist_in_installed_crewai():
    # If a future crewai removes/renames these, this fails loudly — which is
    # exactly the early-warning we want.
    assert hasattr(ToolUsage, "_use")
    # the concrete provider class must own a call() we can wrap
    assert "call" in _provider_class().__dict__


def test_install_patches_the_real_provider_class_not_the_factory():
    # Regression guard for the CrewAI 1.x finding: LLM(...) is a factory that
    # returns a provider subclass, so patching the base LLM.call is a no-op.
    Provider = _provider_class()
    orig_provider_call = Provider.__dict__["call"]
    orig_use = ToolUsage._use
    brake = CrewAIBrake(verbose=False)
    brake.install()
    assert Provider.__dict__["call"] is not orig_provider_call  # really patched
    assert ToolUsage._use is not orig_use
    brake.uninstall()
    assert Provider.__dict__["call"] is orig_provider_call
    assert ToolUsage._use is orig_use


def test_install_is_idempotent():
    brake = CrewAIBrake(verbose=False)
    brake.install()
    patched = ToolUsage._use
    brake.install()  # second call must not double-wrap
    assert ToolUsage._use is patched
    brake.uninstall()


def test_repeated_tool_use_trips_loop():
    orig_use = ToolUsage._use
    # fake original: ignores everything, returns a string
    ToolUsage._use = lambda self, *a, **k: "tool result"
    try:
        brake = CrewAIBrake(
            repeat_tool_limit=3,
            max_cost_usd=None,
            max_steps=None,
            max_tool_calls=None,
            max_duration_s=None,
            verbose=False,
        )
        brake.install()
        sentinel = object()  # stand-in for a ToolUsage instance
        with pytest.raises(AgentBrakeError) as exc:
            for _ in range(5):
                # crewai calls _use by keyword; mirror that exactly
                ToolUsage._use(sentinel, tool_string="same", tool=None, calling=None)
        assert "loop detected" in exc.value.reason
        brake.uninstall()
    finally:
        ToolUsage._use = orig_use


def test_token_delta_accounting_and_cost_ceiling():
    llm = LLM(model="gpt-4o")  # factory returns a provider instance
    Provider = type(llm)
    orig_call = Provider.__dict__["call"]

    # fake original: simulate the API bumping the cumulative per-instance tally,
    # exactly as the real provider's call() does synchronously before returning.
    def fake_call(self, *a, **k):
        self._token_usage["prompt_tokens"] += 10_000
        self._token_usage["completion_tokens"] += 10_000
        return "llm output"

    Provider.call = fake_call
    try:
        # gpt-4o = $2.50 in / $10 out per Mtok -> $0.125 per fake call.
        # ceiling $0.50 -> trips on the 4th call.
        brake = CrewAIBrake(
            max_cost_usd=0.50,
            repeat_tool_limit=None,
            max_steps=None,
            max_tool_calls=None,
            max_duration_s=None,
            verbose=False,
        )
        brake.install()
        with pytest.raises(AgentBrakeError) as exc:
            for _ in range(10):
                llm.call("hello")
        assert "cost ceiling" in exc.value.reason
        stats = brake.engine.stats
        # delta accounting: 4 calls * 10k each, NOT the cumulative-of-cumulative
        assert stats.input_tokens == 40_000
        assert stats.output_tokens == 40_000
        assert stats.llm_calls == 4
        brake.uninstall()
    finally:
        Provider.call = orig_call


def test_context_manager_installs_and_restores():
    orig_use = ToolUsage._use
    with CrewAIBrake(verbose=False):
        assert ToolUsage._use is not orig_use
    assert ToolUsage._use is orig_use

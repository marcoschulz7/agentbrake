"""
LangChain adapter tests.

These drive LangChainBrake through the same callback methods LangChain itself
would call (on_tool_start, on_llm_end), using lightweight fakes that mimic the
shapes LangChain produces. on_tool_start is used (not on_agent_action) because
that is the hook that fires across BOTH the classic AgentExecutor and the
LangChain 1.x / LangGraph agent stacks. We don't need LangChain installed: the
adapter falls back to a stub BaseCallbackHandler, and our fakes supply the
attributes the hooks read.
"""

from types import SimpleNamespace

import pytest

from agentbrake import AgentBrakeError, LangChainBrake


def _tool_start(name, input_str):
    """Mimic a LangChain on_tool_start call: serialized dict + input string."""
    return {"name": name}, str(input_str)


def _llm_response_legacy(model, prompt_tokens, completion_tokens):
    """Older LangChain shape: usage under response.llm_output['token_usage']."""
    return SimpleNamespace(
        llm_output={
            "model_name": model,
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
        },
        generations=[],
    )


def _llm_response_usage_metadata(input_tokens, output_tokens):
    """Newer LangChain shape: usage_metadata on the generation's message."""
    msg = SimpleNamespace(
        usage_metadata={"input_tokens": input_tokens, "output_tokens": output_tokens}
    )
    gen = SimpleNamespace(message=msg)
    return SimpleNamespace(llm_output={}, generations=[[gen]])


def test_repeated_tool_start_trips_loop():
    brake = LangChainBrake(
        repeat_tool_limit=3,
        max_cost_usd=None,
        max_steps=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    serialized, input_str = _tool_start("web_search", {"q": "same"})
    with pytest.raises(AgentBrakeError) as exc:
        for _ in range(5):
            brake.on_tool_start(serialized, input_str)
    assert "loop detected" in exc.value.reason


def test_llm_end_accumulates_cost_and_stops_at_ceiling():
    brake = LangChainBrake(
        max_cost_usd=0.50,
        repeat_tool_limit=None,
        max_steps=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    with pytest.raises(AgentBrakeError) as exc:
        # gpt-4o output $10/Mtok -> 100k output tokens ~= $1.00 > $0.50
        brake.on_llm_end(_llm_response_legacy("gpt-4o", 0, 100_000))
    assert "cost ceiling" in exc.value.reason


def test_usage_metadata_shape_is_extracted():
    brake = LangChainBrake(
        max_cost_usd=None,
        repeat_tool_limit=None,
        max_steps=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    brake.on_llm_end(_llm_response_usage_metadata(1234, 5678))
    assert brake.engine.stats.input_tokens == 1234
    assert brake.engine.stats.output_tokens == 5678
    assert brake.engine.stats.llm_calls == 1


def test_step_limit_via_tool_starts():
    brake = LangChainBrake(
        max_steps=4,
        repeat_tool_limit=None,
        max_cost_usd=None,
        max_tool_calls=None,
        max_duration_s=None,
        verbose=False,
    )
    with pytest.raises(AgentBrakeError) as exc:
        for i in range(10):
            serialized, input_str = _tool_start("web_search", {"q": i})  # unique
            brake.on_tool_start(serialized, input_str)
    assert "step limit" in exc.value.reason
    assert brake.engine.stats.steps == 4


def test_no_stop_for_a_short_well_behaved_run():
    brake = LangChainBrake(verbose=False)  # generous defaults
    for i in range(3):
        serialized, input_str = _tool_start("web_search", {"q": i})
        brake.on_tool_start(serialized, input_str)
        brake.on_llm_end(_llm_response_legacy("gpt-4o-mini", 500, 500))
    assert brake.engine.stats.stopped is False
    assert brake.engine.stats.steps == 3
    assert brake.engine.stats.llm_calls == 3


def test_malformed_llm_response_does_not_crash():
    brake = LangChainBrake(verbose=False)
    # response with neither llm_output nor generations -> extraction stays at 0
    brake.on_llm_end(SimpleNamespace())
    assert brake.engine.stats.llm_calls == 1
    assert brake.engine.stats.total_tokens == 0

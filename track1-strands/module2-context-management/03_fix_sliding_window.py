"""
Module 2, FIX (attempt 2).

context_manager="auto" (02) measurably made things WORSE here, not better --
see README correction. Nova Pro reflexively calls the injected retrieve_context
tool right after seeing a truncated preview, paying for the preview AND the
full original content AND an extra tool-call round-trip.

This tries SlidingWindowConversationManager instead: it truncates large tool
results in place (head/tail + marker) with should_truncate_results=True, and
crucially injects NO retrieve tool -- there's no escape hatch for the model to
pull the full content back. Compare this output to both 01 and 02.

IMPORTANT (confirmed by reading the installed 1.56.0 source): truncation only
fires inside reduce_context, which only runs when either (a) message count
exceeds window_size (default 40 -- never hit in this module's 6-turn run), or
(b) proactive_compression is enabled and the token ratio threshold is crossed.
should_truncate_results=True alone, with everything else default, does NOT
trigger truncation for a short conversation like this one -- confirmed live,
it produced almost the same token curve as unmanaged 01. proactive_compression
must be explicitly enabled for the fix to actually engage at this scale.
"""
from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
from _common import make_model, TURNS


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs -- returns full log dump."""
    return f"[ERROR] {service}: NullPointerException at PaymentProcessor:142\n" * 500


@tool
def get_metrics(service: str) -> str:
    """Get detailed metrics report."""
    return "CPU: 89% | Mem: 94% | Errors: 12.3% | Latency: 4200ms\n" * 300


agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="You are SRE-Junior. Investigate incidents thoroughly.",
    conversation_manager=SlidingWindowConversationManager(
        should_truncate_results=True,
        proactive_compression=True,  # compress at 70% of context window -- see module docstring
    ),
)

if __name__ == "__main__":
    print("registered tools:", list(agent.tool_names))  # expect no retrieve_context
    prev = 0
    for turn in TURNS:
        result = agent(turn)
        total = result.metrics.accumulated_usage["inputTokens"]
        print(f"{turn}\n  cumulative input tokens: {total}  (+{total - prev})")
        prev = total

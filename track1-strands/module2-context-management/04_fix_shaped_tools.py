"""
Module 2, FIX (attempt 3).

02 (context_manager="auto") and 03 (SlidingWindowConversationManager, even with
proactive_compression=True) both failed to reduce tokens vs. 01 unmanaged --
confirmed live, see README. Root cause, confirmed by reading the installed
strands-agents 1.56.0 source: proactive_compression triggers at 70% of the
model's context_window_limit (Nova Pro: ~300K), never crossed by a single
request in this 6-turn run. Strands' built-in context managers only help once
you're actually near the model's window -- they don't shrink a moderately
large but not-yet-huge conversation.

This fix instead shapes the TOOLS: get_logs/get_metrics return a short
deduplicated summary instead of 500x/300x repeated lines. No framework-level
context management needed -- the fix is at the source of the bloat, not after
it enters the conversation.
"""
from strands import Agent, tool
from _common import make_model, TURNS


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs -- returns a deduplicated summary."""
    return (
        f"[ERROR] {service}: NullPointerException at PaymentProcessor:142 "
        f"(500 occurrences in the last window)"
    )


@tool
def get_metrics(service: str) -> str:
    """Get current health metrics -- single snapshot, not a repeated report."""
    return "CPU: 89% | Mem: 94% | Errors: 12.3% | Latency: 4200ms"


agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="You are SRE-Junior. Investigate incidents thoroughly.",
)

if __name__ == "__main__":
    print("registered tools:", list(agent.tool_names))
    prev = 0
    for turn in TURNS:
        result = agent(turn)
        total = result.metrics.accumulated_usage["inputTokens"]
        print(f"{turn}\n  cumulative input tokens: {total}  (+{total - prev})")
        prev = total

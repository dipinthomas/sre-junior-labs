"""
Module 2, FIX.

context_manager="auto" is real and confirmed working -- but don't expect
cumulative tokens to shrink turn-over-turn or hold flat. What it actually
does: injects a `retrieve_context` tool and truncates large tool results to
short previews before they enter context. Total context still grows, just
more slowly than unmanaged. Compare this output to 01_unmanaged_context.py's.
"""
from strands import Agent, tool
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
    context_manager="auto",  # <- the entire fix
)

if __name__ == "__main__":
    print("registered tools:", list(agent.tool_names))  # note: retrieve_context gets added
    prev = 0
    for turn in TURNS:
        result = agent(turn)
        total = result.metrics.accumulated_usage["inputTokens"]
        print(f"{turn}\n  cumulative input tokens: {total}  (+{total - prev})")
        prev = total

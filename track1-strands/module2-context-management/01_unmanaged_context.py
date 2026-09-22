"""
Module 2, BUILD + RUN + BREAK.

Tool results large enough (500x / 300x repeats) to reproduce real, measured
compounding growth -- confirmed via result.metrics.accumulated_usage, not a
hand-rolled token counter. Left running long enough this will overflow the
model's context window (the BREAK).
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
    system_prompt="You are SRE-Junior. Investigate incidents thoroughly using all tools.",
)

if __name__ == "__main__":
    prev = 0
    for turn in TURNS:
        result = agent(turn)
        total = result.metrics.accumulated_usage["inputTokens"]
        print(f"{turn}\n  cumulative input tokens: {total}  (+{total - prev})")
        prev = total

"""
Module 1, BREAK.

get_logs always fails. Confirmed: retry behavior is model-dependent, NOT a
guaranteed infinite loop (Nova Pro gave up after 1 call in testing; other
models retried 2-3 times). Nothing stops a model that decides to keep trying,
though -- that's what 03_fix fixes.
"""
import time
from strands import Agent, tool
from _common import make_model

call_count = {"n": 0}


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    call_count["n"] += 1
    print(f"  [get_logs call #{call_count['n']}] raising")
    raise Exception("CloudWatch API timeout – try again")


@tool
def get_metrics(service: str) -> str:
    """Get current health metrics for a service."""
    return "CPU: 89%, Memory: 94%, DB: 50/50 (exhausted)"


agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="You are SRE-Junior. Use get_logs and get_metrics to investigate.",
)

if __name__ == "__main__":
    start = time.time()
    result = agent("ALERT: payment-service is down. Investigate.")
    print(f"\nRan for {time.time() - start:.1f}s")
    print(f"get_logs was called {call_count['n']} time(s)")
    print(f"cycles: {result.metrics.cycle_count}  stop_reason: {result.stop_reason}")

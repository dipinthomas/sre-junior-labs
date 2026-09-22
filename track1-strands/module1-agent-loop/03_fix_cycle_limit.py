"""
Module 1, FIX.

Confirmed bug in the "obvious" approach: `event.agent.tool.stop(reason=...)`
raises `AttributeError: Tool 'stop' not found` -- that method does not exist
in strands-agents 1.56.0.

The real fix: set `event.cancel_tool` on the BeforeToolCallEvent.
"""
from strands import Agent, tool
from strands.hooks.events import BeforeToolCallEvent
from _common import make_model

MAX_CYCLES = 5
call_count = {"n": 0}


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    call_count["n"] += 1
    print(f"  [get_logs call #{call_count['n']}]")
    raise Exception("CloudWatch API timeout – try again")


def enforce_cycle_limit(event: BeforeToolCallEvent):
    cycles = event.agent.event_loop_metrics.cycle_count
    print(f"  hook: cycle_count={cycles}")
    if cycles >= MAX_CYCLES:
        # event.agent.tool.stop(...) does NOT exist -- this is the real API:
        event.cancel_tool = f"Safety limit: {MAX_CYCLES} cycles reached. Escalate to human."


agent = Agent(
    model=make_model(),
    tools=[get_logs],
    system_prompt="You are SRE-Junior. get_logs is flaky: retry with the same args if it fails, up to 12 times.",
)
agent.add_hook(enforce_cycle_limit)

if __name__ == "__main__":
    result = agent("ALERT: payment-service is down. Investigate.")
    print(f"\nexecuted={call_count['n']}  cycles={result.metrics.cycle_count}  stop={result.stop_reason}")
    print(result)

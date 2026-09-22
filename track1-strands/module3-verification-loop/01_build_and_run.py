"""
Module 3, BUILD + RUN.

GoalLoop with a real rubric. This module needed NO correction in validation --
the constructor, retry loop, and warnings all match real behavior exactly.
"""
from strands import Agent, tool
from strands.vended_plugins.goal import GoalLoop
from _common import make_model, RUBRIC


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    return "[ERROR] DB connection pool exhausted. [ERROR] NullPointerException."


@tool
def get_metrics(service: str) -> str:
    """Get health metrics for a service."""
    return "CPU: 89%, Memory: 94%, DB connections: 50/50 (pool exhausted)"


verifier = GoalLoop(goal=RUBRIC, max_attempts=3, timeout=60)

agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="You are SRE-Junior. Investigate and produce a complete remediation.",
    context_manager="auto",
    plugins=[verifier],
)

if __name__ == "__main__":
    result = agent("ALERT: payment-service down. Full investigation required.")
    print("\n--- final output ---")
    print(result)

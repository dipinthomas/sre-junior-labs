"""
Module 3, BREAK.

An impossible rubric with no max_attempts. Confirmed: strands-agents actually
warns you at construction time -- this is not a silent trap.
"""
from strands import Agent, tool
from strands.vended_plugins.goal import GoalLoop
from _common import make_model


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    return "[ERROR] DB connection pool exhausted."


@tool
def get_metrics(service: str) -> str:
    """Get health metrics for a service."""
    return "CPU: 89%, Memory: 94%, DB connections: 50/50"


# No max_attempts -- watch for the UserWarning strands-agents prints at construction.
verifier = GoalLoop(
    goal="Response must be exactly 7 words, contain 'quantum entanglement', "
         "AND provide a full root cause analysis."
)

agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="You are SRE-Junior.",
    plugins=[verifier],
)

if __name__ == "__main__":
    print("(watch stderr above for a UserWarning about unbounded execution)\n")
    result = agent("ALERT: payment-service down.")
    print(result)

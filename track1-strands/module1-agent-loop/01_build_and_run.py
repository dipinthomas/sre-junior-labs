"""
Module 1, BUILD + RUN.

SRE-Junior with two mock tools, investigating a real incident.
Confirmed: 2 cycles, stop_reason="end_turn", produces a root cause + remediation.
"""
from strands import Agent, tool
from _common import make_model


@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    return f"""[ERROR] 14:22:01 NullPointerException in {service} PaymentProcessor.java:142
[ERROR] 14:22:03 Connection pool exhausted – max 50 connections
[WARN]  14:22:09 Circuit breaker OPEN for downstream-db"""


@tool
def get_metrics(service: str) -> str:
    """Get current health metrics for a service."""
    return f"""Service: {service}
  CPU: 89%  Memory: 94%  Error rate: 12.3%  DB connections: 50/50 (exhausted)"""


agent = Agent(
    model=make_model(),
    tools=[get_logs, get_metrics],
    system_prompt="""You are SRE-Junior, an on-call triage assistant.
Use get_logs and get_metrics to investigate, then suggest a remediation with a rollback plan.""",
)

if __name__ == "__main__":
    result = agent("ALERT: payment-service is throwing errors. Investigate.")
    print("\n--- result ---")
    print(result)
    print(f"\ncycles: {result.metrics.cycle_count}  stop_reason: {result.stop_reason}")

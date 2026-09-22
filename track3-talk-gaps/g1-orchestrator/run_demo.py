"""
G1 -- The Orchestrator. Confirmed working end-to-end (3 cycles, correct
delegation trace, real final answer) in validation.

Original doc's model="anthropic.claude-sonnet" is not a real Bedrock model ID
and raises ValidationException -- fixed here via make_model().

A sub-agent called as a tool returns a real strands AgentResult object, not a
str, even though the wrapping @tool function is annotated -> str. It works
because AgentResult stringifies sensibly -- but wrap it in str(...) explicitly,
as done below, rather than relying on that.
"""
from strands import Agent, tool
from _common import make_model


@tool
def get_recent_errors(service: str) -> str:
    """Fetch recent errors for a service."""
    return f"[ERROR] {service}: DB connection pool exhausted (48 events in 10 min)."


@tool
def get_open_tickets(service: str) -> str:
    """List open tickets for a service."""
    return "No open tickets."


@tool
def create_ticket(title: str, body: str, priority: str) -> str:
    """File a new ticket."""
    return f"Created ticket SRE-1902 ({priority}): {title}"


log_agent = Agent(
    model=make_model(),
    system_prompt="You are a log analysis specialist. Diagnose errors from CloudWatch.",
    tools=[get_recent_errors],
)

ticket_agent = Agent(
    model=make_model(),
    system_prompt="You create and update SRE incident tickets.",
    tools=[get_open_tickets, create_ticket],
)


@tool
def analyse_logs(service: str, summary: str) -> str:
    """Delegate log analysis to the log specialist sub-agent."""
    return str(log_agent(f"Analyse errors for {service}. Context: {summary}"))


@tool
def file_ticket(title: str, body: str, priority: str) -> str:
    """Delegate ticket creation to the ticket specialist sub-agent."""
    return str(ticket_agent(f"Create a {priority} ticket: {title}. Body: {body}"))


orchestrator = Agent(
    model=make_model(),
    system_prompt="You are an SRE incident commander. Delegate -- never act directly.",
    tools=[analyse_logs, file_ticket],  # delegation tools only, no domain tools
)

if __name__ == "__main__":
    result = orchestrator("payment-service latency spike -- investigate and file a ticket")
    print(f"\ncycles: {result.metrics.cycle_count}  stop_reason: {result.stop_reason}")
    print(result)

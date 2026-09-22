"""
Reference only -- NOT meant to be run directly.

This is the tool section to paste into the CLI-generated
sreJunior/app/sre_junior/main.py, replacing the placeholder `add_numbers` tool.
Confirmed working against a live deployed AgentCore Runtime.

Also confirmed here: the real invoke payload the CLI sends is a `messages` list,
not the flat {"prompt": "..."} shape you might expect from boto3's
invoke_agent_runtime examples elsewhere. The generated _extract_prompt() already
handles both shapes -- don't replace it with logic that assumes only a string.
"""
from strands import tool

@tool
def get_logs(service: str) -> str:
    """Fetch recent error logs for a service."""
    return f"[ERROR] {service}: DB connection pool exhausted."
tools.append(get_logs)  # noqa: F821 -- `tools` is defined earlier in the generated file

@tool
def get_metrics(service: str) -> str:
    """Get health metrics for a service."""
    return f"{service}: CPU 89%, Memory 94%, DB 50/50."
tools.append(get_metrics)  # noqa: F821

# In model/load.py, the CLI's default model_id is
#   "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
# which does not match the doc's claude-sonnet-4-6 claim, and Anthropic model
# access was unreliable in testing regardless. Reliable alternative:
#
#   from strands.models.bedrock import BedrockModel
#   def load_model() -> BedrockModel:
#       return BedrockModel(model_id="us.amazon.nova-pro-v1:0", region_name="us-east-1")

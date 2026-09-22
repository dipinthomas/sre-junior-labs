# G1 — The Orchestrator

Fully run locally, no AWS deployment needed. Confirmed end-to-end.

## Run

```bash
cd track3-talk-gaps/g1-orchestrator
python run_demo.py
```

You should see 3 cycles and a final answer referencing a real created ticket ID. The
orchestrator's own trace will only show `analyse_logs` and `file_ticket` calls — the
domain tools (`get_recent_errors`, `create_ticket`) only appear inside the sub-agents'
own internal traces. That isolation is the whole point of the pattern, and it's real.

## Confirmed bugs fixed here

1. `model="anthropic.claude-sonnet"` is not a valid Bedrock model ID — confirmed with a
   direct `ValidationException: The provided model identifier is invalid.`
2. A sub-agent called as a tool returns `strands.agent.agent_result.AgentResult`, not
   `str` — wrap it in `str(...)` (see `analyse_logs`/`file_ticket` above).

## Gateway Policy enforcement (not runnable here)

The FIX step in the original talk-gap doc calls
`client.create_policy(gatewayId=..., cedarPolicy=...)` — confirmed those parameter
names don't exist. The real `CreatePolicy` operation needs `name`, `definition`, and
`policyEngineId` (a Policy Engine is a separate resource you create first):

```python
policy_engine = client.create_policy_engine(name="sre-tooling-policy-engine")
client.create_policy(
    name="log-agent-scope",
    policyEngineId=policy_engine["policyEngineId"],
    definition="""
    permit(
        principal == AgentCore::Agent::"log-agent",
        action in [AgentCore::Action::"get_recent_errors"],
        resource == AgentCore::Gateway::"sre-tooling-gateway"
    );""",
)
```

This was checked against the real `bedrock-agentcore-control` service model but not
deployed end-to-end — treat it as corrected-API-shape, not live-confirmed enforcement.

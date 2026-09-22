# G3 — The Crash

`flaky_tool.py` is plain Python and runs anywhere — no setup needed, confirmed fine
as originally written. `recovery.py` needs a deployed Runtime + Memory (Track 2,
Modules 4-5); set `AGENT_RUNTIME_ARN` and `MEMORY_ID` in `.env` first.

```bash
cd track3-talk-gaps/g3-crash-recovery
INJECT_CRASH=true python -c "from flaky_tool import scale_db_pool; scale_db_pool('payment-service', 100)"
python recovery.py
```

## Confirmed bugs fixed here

- Same `invoke_agent` → `invoke_agent_runtime` fix as G2.
- `BedrockAgentCoreMemoryClient` doesn't exist — confirmed by introspection against the
  live `bedrock_agentcore` SDK. Real class: `MemoryClient` from `bedrock_agentcore.memory`.
- `.store()` / `.retrieve()` aren't real methods on `MemoryClient` — real equivalents are
  `create_event()` and `retrieve_memories()`, both requiring `actor_id`.

## What's confirmed vs. not

The cold-restart failure story (re-diagnosing on a changed system state, double-applying
a partially-completed fix) is a real and correct failure mode — no AWS-specific claims to
verify there. The recovery code above uses the real client/method names but wasn't run
against a live crash-and-resume cycle end-to-end in this validation pass.

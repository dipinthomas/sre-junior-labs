# G2 — Two Incidents At Once

Needs a deployed AgentCore Runtime (Track 2, Module 4). Set `AGENT_RUNTIME_ARN` in
your `.env` first, then:

```bash
cd track3-talk-gaps/g2-session-isolation
python concurrent_incidents.py               # BUILD/RUN: separate sessions, no bleed
```

To see the BREAK, edit `concurrent_incidents.py` and hardcode both calls to the same
`session_id` string — confirmed live in an earlier validation pass: no error is thrown,
but the second incident's answer stays anchored on the first incident's context.

```bash
python fix_deterministic_session_ids.py       # FIX: deterministic, unique, long enough
```

## Confirmed bugs fixed here

- `client.invoke_agent(agentId=, sessionId=, inputText=)` doesn't exist on the real
  `bedrock-agentcore` boto3 client at all. Real operation: `invoke_agent_runtime`, with
  `agentRuntimeArn` / `runtimeSessionId` / `payload`.
- `runtimeSessionId` has a real, confirmed hard minimum of **33 characters**.

## One correction to the mechanism claim

In live testing, session contamination came from an in-process, per-session agent
cache inside a warm container — not strictly "different microVM, same ID" reasoning.
Don't rely on microVM boundaries as your mental model of why isolation works; the fix
(never reuse or guess a session ID) is identical either way.

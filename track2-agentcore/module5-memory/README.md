# Module 5 — SRE-Junior Remembers (AgentCore Memory)

Requires Module 4's deployed project as a starting point.

## Create the memory resource — confirmed working, real strategy types

```bash
cd sreJunior   # from Module 4
agentcore add memory --name sreJuniorMemory \
  --strategies SEMANTIC,SUMMARIZATION,EPISODIC --expiry 30
agentcore deploy -y
```

**Confirmed bug (if you've seen an older doc):** `"EXTRACTION"` is not a real strategy
type. The real enum is `SEMANTIC` / `SUMMARIZATION` / `USER_PREFERENCE` / `EPISODIC` —
confirmed both via the CLI's own validation and directly against the live
`bedrock-agentcore-control` boto3 client.

The memory ID is injected as an environment variable on your deployed runtime — you
don't hardcode it:

```bash
aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id <your-runtime-id> --query environmentVariables
# → {"MEMORY_SREJUNIORMEMORY_ID": "sreJunior_sreJuniorMemory-XXXXXXXXXX"}
```

## Real client code

See [`memory_client_example.py`](memory_client_example.py). Confirmed by introspection
against the live `bedrock_agentcore` SDK:

- The real class is `MemoryClient`, imported from `bedrock_agentcore.memory` —
  `BedrockAgentCoreMemoryClient` (seen in some docs) does not exist anywhere in the SDK.
- The real methods are `save_conversation()` and `retrieve_memories()` — not
  `create_event(messages=...)` / `retrieve_memory()`. Both **require** an `actor_id`
  argument; a call missing it raises `TypeError` before it reaches AWS.

## A gotcha we hit ourselves

If you wire memory recall into your entrypoint with a guard like
`if isinstance(prompt, str):`, check what your entrypoint actually receives first — the
real `agentcore invoke` CLI sends payloads as a `messages` list, not a bare string, so a
naive string-typed guard silently never fires. Log the real shape before branching on it.

## What's confirmed vs. not

The class names, method names, and the async-propagation-delay behavior of long-term
memory (query at the start of the *next* session, not right after closing the previous
one) are all real and match the original story directionally. We didn't get a clean,
fully-isolated live demonstration of the delay within the time available for this
validation pass — treat that specific claim as correct-but-not-re-confirmed-here.

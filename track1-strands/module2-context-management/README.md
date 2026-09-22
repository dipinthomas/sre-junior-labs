# Module 2 — SRE-Junior Gets Chatty (context management)

Fully run locally, no AWS deployment needed.

## Run

```bash
cd track1-strands/module2-context-management
python 01_unmanaged_context.py           # watch cumulative tokens compound across 6 turns
python 02_fix_context_manager_auto.py    # same 6 turns, context_manager="auto"
```

## What's confirmed vs. what to expect

Measured live (unmanaged), values will vary by model and account but the *shape* is real:

```
turn 1 → ~29,947 cumulative input tokens
turn 2 → ~50,061   (driven by turn 1's stale results still in context)
turn 3 → ~99,775
turn 4 → ~169,277
```

With `context_manager="auto"`, growth is measurably slower but **does not flatten out** --
this corrects a common misread of the feature. It injects a `retrieve_context` tool
(check `agent.tool_names` after construction) and truncates large tool results to
previews. Don't expect a specific target token count; measure your own workload.

If you keep adding turns with large results, `01` will eventually hit a real context
overflow error from Bedrock -- that's expected and matches the original break scenario.

## Key API surface confirmed here

- `context_manager="auto"` on `Agent(...)`
- `result.metrics.accumulated_usage["inputTokens"]` — the real, non-hand-rolled counter
- Auto-injected `retrieve_context` tool

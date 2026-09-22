# Module 1 — Meet SRE-Junior (agent loop)

Fully run locally, no AWS deployment needed — just Bedrock access.

## Run

```bash
cd track1-strands/module1-agent-loop
python 01_build_and_run.py          # baseline: agent investigates, 2 cycles, end_turn
python 02_break_runaway_retries.py  # get_logs always fails -- watch the retry count
python 03_fix_cycle_limit.py        # hook-based cycle cap, the REAL working fix
```

## What's confirmed vs. what to expect

- **`01`**: confirmed working as-is. You should see 2 cycles and a real remediation.
- **`02`**: the retry behavior is real but **model-dependent** — don't expect it to loop
  forever. In testing, Nova Pro gave up after 1 failed call; other models retried 2-3
  times with slightly different arguments before quitting on their own. If you want to
  force a longer loop to see the effect more dramatically, try a different `MODEL_ID` in
  `.env`, or add `max attempts` language to the system prompt as this file does.
- **`03`**: the original doc's `agent.tool.stop()` is not a real method and raises
  `AttributeError`. The fix here uses `event.cancel_tool`, confirmed working — it
  force-stops cleanly at cycle 5 regardless of model.

## Key API surface confirmed here

- `strands.hooks.events.BeforeToolCallEvent`
- `event.agent.event_loop_metrics.cycle_count`
- `event.cancel_tool = "<message>"` — NOT `agent.tool.stop()`
- `result.metrics.cycle_count`, `result.stop_reason`

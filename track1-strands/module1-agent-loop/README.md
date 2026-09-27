# Module 1 — Meet SRE-Junior (agent loop)

Fully run locally, no AWS deployment needed — just Bedrock access.

## The agent loop concept

A plain LLM call is stateless and single-shot: send text, get text back, done — it can't
*do* anything. The **agent loop** (Strands' core abstraction) is what turns that into
something that acts. Per the [Strands docs](https://strandsagents.com/docs/user-guide/sdk/agents/agent-loop/):

> invoke the model, check if it wants to use a tool, execute the tool if so, then invoke
> the model again with the result.

Each trip through that sequence is one **cycle** (Strands calls it a "turn" in the API —
`limits["turns"]` caps how many are allowed per invocation). Every cycle accumulates
context: the model sees the original request plus every tool call and result so far, so it
can reason across multiple steps. This is exactly what the scripts in this module print as
`result.metrics.cycle_count`.

**Tool call execution**, each cycle: the framework validates the model's tool request
against the tool's schema, locates it in the registry, executes it with error handling, and
formats the result as a tool-result message appended to the conversation. Crucially, **a
tool raising an exception returns an error result to the model — it does not terminate the
loop.** The model sees the failure and gets to decide what to do next (retry, try something
else, give up). That's exactly the behavior `02_break_runaway_retries.py` demonstrates:
nothing in the framework stops a model that decides to keep calling a failing tool.

**The loop terminates** when the model produces a final `stop_reason`. The ones relevant
here:
- `end_turn` — model finished normally, no more tool calls requested. This is what `01` and
  `02` both end with (the model gives up or finishes on its own).
- `tool_use` — model wants to execute more tools; the loop just continues, this isn't a
  terminal state.
- other budget/limit reasons (`limit_turns`, `max_tokens`, `guardrail_intervened`, etc.)
  exist but aren't exercised by this module.

**Hooks** are how you observe or intervene in the loop from your own code, rather than just
letting the model run unchecked — this is the mechanism `03_fix_cycle_limit.py` uses to add
a hard cap the framework doesn't provide by default. See "Key API surface" below for the
specific hook used here.

Sources: [Strands docs — Agent Loop](https://strandsagents.com/docs/user-guide/sdk/agents/agent-loop/),
[Strands docs — Anatomy of an Agent](https://strandsagents.com/docs/user-guide/sdk/agents/)

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

- `strands.hooks.events.BeforeToolCallEvent` — fires immediately before each tool
  execution in the loop. Register it via the `HookProvider` protocol:
  ```python
  class ToolGuard:
      def register_hooks(self, registry: HookRegistry):
          registry.add_callback(BeforeToolCallEvent, self.guard_tool)

      def guard_tool(self, event: BeforeToolCallEvent):
          if some_condition:
              event.cancel_tool = "Tool execution blocked"
  ```
- `event.agent.event_loop_metrics.cycle_count` — read the current cycle count from
  inside a hook, so you can compare it against a limit and decide whether to cancel.
- `event.cancel_tool = "<message>"` — NOT `agent.tool.stop()`. Setting this skips the
  tool invocation and returns an error result containing that message to the model
  instead — the model sees it as a failed tool call and continues from there, it doesn't
  crash the loop.
- `result.metrics.cycle_count`, `result.stop_reason` — read after `agent(...)` returns,
  to see how many cycles the whole invocation took and why it stopped
  (`end_turn`, `tool_use`, etc. — see stop reasons above).

(Source: [Strands docs — Hooks and Lifecycle Events](https://strandsagents.com/docs/user-guide/sdk/agents/hooks/))

# Module 2 — SRE-Junior Gets Chatty (context management)

Fully run locally, no AWS deployment needed.

## `context_manager` vs. `conversation_manager` -- not two competing systems

`context_manager="auto"|"agentic"|False` (set on `Agent(context_manager=...)`) is a
**preset selector** -- per the
[Strands docs](https://strandsagents.com/docs/user-guide/sdk/context-management/built-in-modes/),
"by simply specifying one mode in `context_manager`, the SDK configures a complete context
management setup with tuned defaults." It doesn't do the work itself; it configures a
`conversation_manager` object (plus, for `"auto"`, the injected `retrieve_context` tool)
on your behalf.

`conversation_manager=<object>` (set on `Agent(conversation_manager=...)`) is the actual
mechanism -- `SlidingWindowConversationManager`, `SummarizingConversationManager`, or
`NullConversationManager`. Passing one directly bypasses the preset and exposes every knob
by hand (`window_size`, `should_truncate_results`, `proactive_compression`, `pin_first`,
`per_turn`, `summary_ratio`, ...).

So `context_manager="auto"` and a hand-built `SlidingWindowConversationManager` (`03`,
below) are drawing from the same underlying family of mechanisms, not two rival systems --
which is exactly why both hit the same fundamental limitation in this module (see `03`'s
finding below): the mechanism only engages near the model's actual context ceiling,
regardless of which layer you configure it from.

## Run

```bash
cd track1-strands/module2-context-management
python 01_unmanaged_context.py           # watch cumulative tokens compound across 6 turns
python 02_fix_context_manager_auto.py    # same 6 turns, context_manager="auto" -- WORSE, see below
python 03_fix_sliding_window.py          # SlidingWindowConversationManager -- NO BETTER, see below
python 04_fix_shaped_tools.py            # the fix that actually works: shape tool output, not context
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

**Correction (measured live, Nova Pro, `fernhub` account):** with this module's tools and
system prompt, `auto` did not just grow slower -- it was **worse at every turn**, roughly
1.7x more cumulative tokens than unmanaged by turn 6:

| Turn | `01` unmanaged (cumulative / Δ) | `02` auto (cumulative / Δ) |
|---|---|---|
| 1 | 10,028 / +10,028 | 13,989 / +13,989 |
| 2 | 39,788 / +29,760 | 63,301 / +49,312 |
| 3 | 89,321 / +49,533 | 148,094 / +84,793 |
| 4 | 158,558 / +69,237 | 267,992 / +119,898 |
| 5 | 247,542 / +88,984 | 423,145 / +155,153 |
| 6 | 356,268 / +108,726 | 614,581 / +191,436 |

Why: `auto` shows the model a truncated preview of each tool result, but Nova Pro's
system prompt here ("investigate incidents thoroughly") makes the model treat the preview
as insufficient -- it calls the injected `retrieve_context` tool immediately after almost
every `get_logs`/`get_metrics` call to pull back the full original content anyway. That
means each turn pays for the truncated preview **plus** a whole extra tool-call round-trip
**plus** the full original content regardless -- strictly additive over the unmanaged
baseline, not a saving. `auto` only helps if the model is willing to work from the preview
without retrieving; whether that happens is model- and prompt-dependent, so measure your
own workload rather than assuming `auto` is a free win.

If you keep adding turns with large results, `01` will eventually hit a real context
overflow error from Bedrock -- that's expected and matches the original break scenario.

## `03`: SlidingWindowConversationManager also didn't help (confirmed live)

The obvious next thing to try is `SlidingWindowConversationManager(should_truncate_results=True)`
directly, instead of the higher-level `context_manager="auto"`. Measured live, it landed
within noise of unmanaged `01` -- no improvement:

| Turn | `01` unmanaged | `03` sliding window (`should_truncate_results=True`, `proactive_compression=True`) |
|---|---|---|
| 1 | 10,028 | 10,020 |
| 2 | 39,788 | 39,719 |
| 3 | 89,321 | 89,261 |
| 4 | 158,558 | 158,569 |
| 5 | 247,542 | 247,704 |
| 6 | 356,268 | 356,616 |

Why, confirmed by reading the installed `strands-agents` 1.56.0 source
(`strands/agent/conversation_manager/`): truncation only actually runs inside
`reduce_context`, which only fires when either (a) message count exceeds `window_size`
(default 40 -- this module's 6-turn run never gets close), or (b) `proactive_compression`
is enabled *and* `projected_input_tokens / model.context_window_limit` crosses the
threshold (default 0.7). Nova Pro's context window is large enough (~300K) that even
turn 6's single request never crosses 70% of it. **Both built-in mechanisms are designed
to kick in only when you're actually approaching the model's context limit -- they don't
help a conversation that's merely bloated but nowhere near that ceiling.**

## `04`: the fix that actually works -- shape the tool output

Since the framework-level fixes only trigger near the context ceiling, the fix that works
at this module's scale has to happen at the source: don't let tools return bloated output
in the first place. `04_fix_shaped_tools.py` changes `get_logs`/`get_metrics` to return a
short deduplicated summary instead of 500x/300x repeated lines -- no conversation manager
needed at all. Measured live:

| Turn | `01` unmanaged | `04` shaped tools |
|---|---|---|
| 1 | 10,028 | 1,777 |
| 2 | 39,788 | 2,667 |
| 3 | 89,321 | 4,796 |
| 4 | 158,558 | 7,369 |
| 5 | 247,542 | 12,175 |
| 6 | 356,268 | 14,077 |

A ~25x reduction by turn 6, and the per-turn delta stays small and roughly flat instead of
growing every turn. **Takeaway: tool output shape is a first-class lever for context
management, and often a more effective one than reaching for context-management
middleware.** Reach for a conversation manager when you can't control the tool (e.g. a
third-party API that returns huge payloads) and are actually approaching the model's
context window; reach for output shaping first when you own the tool.

### A second, subtler lever: tool output *wording*, not just size

Deduplicating the data isn't the only thing that matters -- the phrasing of a tool's
result also shapes the model's own decision to re-call that tool, independent of the data
being identical. Measured live: `get_logs` originally returned
`"...PaymentProcessor:142 (500 occurrences in the last window)"`. Removing the
parenthetical (just `"...PaymentProcessor:142 "`, no completeness signal) caused Nova Pro
to re-call `get_metrics`/`get_logs` on turns where it had previously trusted stale context
and skipped the call -- 8 tool calls total instead of 6, and cumulative tokens rose from
14,077 to 19,698 by turn 6, purely from the wording change:

| Turn | `04` with "(500 occurrences...)" | `04` without it |
|---|---|---|
| 1 | 1,777 | 1,761 |
| 2 | 2,667 | 3,700 |
| 3 | 4,796 | 6,286 |
| 4 | 7,369 | 9,346 |
| 5 | 12,175 | 15,064 |
| 6 | 14,077 | 19,698 |

Why: the phrase read as a signal of *completeness* -- "this is a stable summary, nothing
more to check" -- which nudged the model toward trusting cached context instead of
re-verifying. Without it, the tool result reads more like a live status line, and the
model's own judgment about staleness tips toward re-calling. **This is not a Strands or
framework behavior -- it's the underlying model's judgment being sensitive to a small
wording change in tool output, on top of whatever size reduction you've already done.**
Shaping tool output for size and shaping it for implied freshness/completeness are two
separate concerns worth checking independently.

## Key API surface confirmed here

- `context_manager="auto"` on `Agent(...)` — injects `retrieve_context`, see `02`'s
  correction above for why this made things worse in this workload.
- `strands.agent.conversation_manager.SlidingWindowConversationManager` — constructor:
  `window_size=40`, `should_truncate_results=True`, `per_turn=False`, `pin_first=None`,
  `proactive_compression=None`. Pass via `Agent(conversation_manager=...)`.
- `proactive_compression=True` — enables compression at 70% of
  `agent.model.context_window_limit`; pass a dict `{"compression_threshold": float}` to
  customize. Confirmed this never triggers for this module's payload sizes.
- `result.metrics.accumulated_usage["inputTokens"]` — the real, non-hand-rolled counter

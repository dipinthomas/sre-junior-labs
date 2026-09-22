# Module 3 — SRE-Junior Checks Its Work (GoalLoop verification)

Fully run locally, no AWS deployment needed. This is the one module that needed
**zero corrections** — the original code matches real behavior exactly.

## Run

```bash
cd track1-strands/module3-verification-loop
python 01_build_and_run.py             # rubric-checked remediation, passes on retry
python 02_break_impossible_rubric.py   # no max_attempts + impossible rubric
```

## What's confirmed

- `GoalLoop(goal=..., max_attempts=3, timeout=60)` — real constructor, works as documented.
- Omitting `max_attempts`/`timeout` triggers a real `UserWarning: strands:goal-loop has no
  max_attempts or timeout; execution is unbounded` at construction time — the SDK actually
  warns you, it's not a silent trap.
- The retry loop (reject with feedback → retry with feedback in context → pass) is real.

## Key API surface confirmed here

- `strands.vended_plugins.goal.GoalLoop`
- `GoalLoop(goal, max_attempts, timeout)`

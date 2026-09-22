# G4 — The Poison

Needs a deployed Memory resource (Track 2, Module 5). Set `MEMORY_ID` in `.env` first.

```bash
cd track3-talk-gaps/g4-memory-poisoning
python -c "from learning_loop import write_lesson_learned; print(write_lesson_learned('INC-1', 'actor-1', 'DB pool exhausted', 'scaled pool to 100'))"
python -c "from learning_loop import recall_past_incidents; print(recall_past_incidents('payment-service', 'actor-1'))"
```

## Confirmed bugs fixed here

Same two bugs as G3: `BedrockAgentCoreMemoryClient` doesn't exist (real: `MemoryClient`),
and `.store()`/`.retrieve()` aren't real methods (real: `create_event()`/`retrieve_memories()`,
both requiring `actor_id`).

## What's confirmed vs. not — read this before presenting this module as proven

The **threat model itself** — untrusted content reaching episodic summarisation with no
provenance check, becoming a trusted "lesson learned" — is a real, published concern
(see OWASP ASI06 in the top-level docs) and doesn't depend on any AWS-specific API.

What we did **not** do: deploy a real ticketing integration, inject an actual poisoned
comment, and watch it get retrieved weeks later with full agent confidence. That full
demonstration needs infrastructure beyond what this validation pass covered. Only the
memory client and method calls above were corrected and confirmed to exist —
`provenance_fix.py`'s design (reject unverified sources, tag trust level) is sound, but
untested end-to-end.

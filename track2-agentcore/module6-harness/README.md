# Module 6 — Full Production (the Harness)

CLI commands only — there's no Python to write for this module.

## Confirmed bug

There is **no `agentcore.yaml` file** to hand-edit. A harness is a resource inside the
same flat `agentcore.json` model as everything else, configured through CLI flags —
fields like `memory: enabled: true` or `context_management: enabled: true` from an
older doc don't correspond to anything real.

## Real command — confirmed against the live CLI

```bash
cd sreJunior   # from Module 4/5
agentcore add harness --name sreJuniorHarness \
  --model-provider bedrock --model-id us.anthropic.claude-sonnet-4-6 \
  --memory-name sreJuniorMemory
agentcore deploy -y
```

Confirmed real flags on `agentcore add harness`: `--model-provider`, `--model-id`,
`--api-format`, `--temperature`, `--top-p`, `--container`, `--memory-name` /
`--memory-arn`, and a `--no-memory` default. There's no single flag equivalent to
`context_management: enabled` from the older doc.

**Before you build against this**, always check your installed CLI's actual flags —
this schema moves fast enough that a plausible-looking snippet from any doc, including
this one, is a coin flip a version or two later:

```bash
agentcore add harness --help
agentcore validate
```

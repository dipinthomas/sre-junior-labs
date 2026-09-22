# Module 4 — SRE-Junior Goes to Work (AgentCore Runtime)

Unlike Track 1, this can't ship as plain files you `python run.py` — the real
`agentcore create` CLI generates its own project structure with an embedded CDK app,
and it's specific to your AWS account. This README gives you the exact, confirmed-working
sequence instead.

## One-time setup

```bash
npm install -g @aws/agentcore aws-cdk
cdk bootstrap aws://<YOUR_ACCOUNT_ID>/<YOUR_REGION>   # once per account+region
```

## Scaffold and deploy — confirmed working, exact flags

```bash
mkdir sre-junior-agentcore && cd sre-junior-agentcore
agentcore create --name sre_junior --project-name sreJunior \
  --framework Strands --model-provider Bedrock \
  --memory none --protocol HTTP --language Python --build CodeZip
```

**Confirmed:** name flags must be alphanumeric + underscores — a hyphen in `--name` is
rejected outright. This creates `sreJunior/app/sre_junior/main.py` and
`sreJunior/agentcore/agentcore.json` — **not** the flat `agent.py` / `agentcore.yaml`
you might expect from an older doc.

## Replace the generated tools with SRE-Junior's

Open `sreJunior/app/sre_junior/main.py` and replace the placeholder `add_numbers` tool
with `get_logs`/`get_metrics` — see [`main_patch_reference.py`](main_patch_reference.py)
in this folder for the exact tool definitions used in validation. Keep everything else
in the generated file (the `agent_factory`, `strip_trailing_tool_use`, and the async
`@app.entrypoint` generator) — that scaffolding is real and required.

## Test locally, then deploy for real

```bash
cd sreJunior
agentcore dev -l                                    # starts a local server, keep it running
agentcore dev "ALERT: payment-service is throwing errors. Investigate."   # in a second terminal
agentcore deploy -y   # -y is required for non-interactive use, or it hangs on a TTY prompt
```

## Invoke the deployed agent — confirmed working, with a real gotcha

```bash
agentcore invoke --session-id "incident-alice-2026-09-22-payment-svc-001" \
  --prompt "payment-service is down. Investigate."
```

**Confirmed bug:** `sessionId` has a hard AWS validation minimum of **33 characters**.
A short, natural ID like `"incident-alice-2026-09-09"` (26 chars) gets rejected with
`ValidationException: Value at 'runtimeSessionId' failed to satisfy constraint: Member
must have length greater than or equal to 33`. Pad your session IDs, or use
[`make_session_id.py`](make_session_id.py) in this folder.

## Tear down when done

```bash
agentcore remove all -y
agentcore deploy -y     # deploys the now-empty config, which deletes the runtime + role
```
This does **not** remove your CDK bootstrap stack (`CDKToolkit`) — that's shared across
projects in the account/region. Only delete it if you're sure nothing else uses it:
```bash
cdk destroy CDKToolkit    # or via CloudFormation console; remember to empty its S3 bucket first
```

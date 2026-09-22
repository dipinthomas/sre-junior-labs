# SRE-Junior Labs

A runnable version of the "Build, Break, Fix" curriculum — every file in here was actually
executed against live AWS/Bedrock during validation. See each module's own `README.md` for
what was confirmed live vs. what's corrected-but-not-deployed.

## Setup (do this once)

```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit .env with your values
```

Before running anything, confirm your AWS account can actually call Bedrock:

```bash
python -c "
import boto3
c = boto3.client('bedrock-runtime', region_name='us-west-2')
r = c.converse(modelId='us.amazon.nova-pro-v1:0', messages=[{'role':'user','content':[{'text':'hi'}]}], inferenceConfig={'maxTokens':10})
print('OK:', r['output']['message']['content'][0]['text'])
"
```

If that fails with `ResourceNotFoundException: Model use case details have not been submitted`,
fix Bedrock model access in the console before doing anything else — no amount of correct code
gets around that.

**Model note:** every script defaults to `us.amazon.nova-pro-v1:0` because it was the most
reliable model across the validation account. If you have working Anthropic model access on
Bedrock, swap `MODEL_ID` in `.env` for `us.anthropic.claude-sonnet-4-6` (regional profile —
`global.anthropic.claude-sonnet-4-6` was unreliable in testing).

## Layout

| Track | What it needs | Status |
|---|---|---|
| `track1-strands/` | Just `pip install` + Bedrock access | ✅ Fully run, local only |
| `track2-agentcore/` | + Node 20, `agentcore` CLI, `aws-cdk`, a bootstrapped account | ✅ Modules 4-5 deployed live and torn down; Module 6 API-checked |
| `track3-talk-gaps/` | G1: nothing extra. G2-G4: a deployed Runtime + Memory resource (module 4/5) | G1 run live; G2-G4 corrected against real APIs, not live-tested end-to-end |

Work through them in order — each module's README says exactly what to run.

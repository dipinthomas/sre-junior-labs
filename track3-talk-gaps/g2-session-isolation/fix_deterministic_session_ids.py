"""
G2 -- FIX. Deterministic, unique, always >= 33 chars. Needs AGENT_RUNTIME_ARN in .env.
"""
import os, json, hashlib
from pathlib import Path
from dotenv import load_dotenv
import boto3

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REGION = os.environ.get("AWS_REGION", "us-west-2")
RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]

client = boto3.client("bedrock-agentcore", region_name=REGION)


def make_session_id(incident_id: str, service: str) -> str:
    raw = f"{incident_id}:{service}"
    return f"incident-{hashlib.sha256(raw.encode()).hexdigest()[:40]}"  # 49 chars


def handle_incident(service: str, incident_id: str, description: str):
    session_id = make_session_id(incident_id, service)
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": description}).encode(),
    )
    print(f"[{session_id}] {resp['response'].read().decode()[:300]}")


if __name__ == "__main__":
    handle_incident("payment-service", "INC-042", "DB pool exhausted -- investigate.")
    handle_incident("auth-service", "INC-043", "JWT signing key rotation failed -- investigate.")
    # Run both, then re-run the SAME incident_id/service pair and confirm you get the
    # same session_id back -- that's the "deterministic" half of the fix.

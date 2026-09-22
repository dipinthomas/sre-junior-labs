"""
G2 -- Two Incidents At Once. Needs AGENT_RUNTIME_ARN in .env (deploy Module 4 first).

Confirmed bug: client.invoke_agent(agentId=..., sessionId=..., inputText=...) does
NOT exist on the bedrock-agentcore client at all. The real operation is
invoke_agent_runtime, with different parameter names: agentRuntimeArn (not agentId),
runtimeSessionId (not sessionId), payload (not inputText).

Confirmed bug: runtimeSessionId has a hard 33-character minimum. Short IDs like
"incident-a3f2" get rejected with ValidationException before reaching your agent.
The uuid4-based ID below clears the minimum by luck (45 chars) -- see fix.py for
a deliberate, deterministic version.
"""
import os, json, threading, uuid
from pathlib import Path
from dotenv import load_dotenv
import boto3

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REGION = os.environ.get("AWS_REGION", "us-west-2")
RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]  # set this after deploying Module 4

client = boto3.client("bedrock-agentcore", region_name=REGION)


def handle_incident(service: str, description: str):
    session_id = f"incident-{uuid.uuid4()}"  # 45 chars, clears the 33-char minimum
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps({"prompt": f"{service}: {description}"}).encode(),
    )
    print(f"[{session_id}] {service}: {resp['response'].read().decode()[:300]}")


if __name__ == "__main__":
    t1 = threading.Thread(target=handle_incident, args=("payment-service", "DB pool exhausted"))
    t2 = threading.Thread(target=handle_incident, args=("auth-service", "JWT signing key rotation failed"))
    t1.start(); t2.start()
    t1.join(); t2.join()

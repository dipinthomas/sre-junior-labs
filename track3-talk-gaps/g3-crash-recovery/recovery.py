"""
G3 -- FIX. Needs AGENT_RUNTIME_ARN and MEMORY_ID in .env (Track 2, Modules 4-5).

Confirmed bugs fixed here (same as G2 + G3's memory client):
- client.invoke_agent(...) -> invoke_agent_runtime(agentRuntimeArn=, runtimeSessionId=, payload=)
- BedrockAgentCoreMemoryClient does not exist -- real class is MemoryClient,
  imported from bedrock_agentcore.memory.
- memory_client.store()/.retrieve() are not real methods. Real: create_event()
  for a write, retrieve_memories() for a query -- both require actor_id.
"""
import os, json
from pathlib import Path
from dotenv import load_dotenv
import boto3
from bedrock_agentcore.memory import MemoryClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REGION = os.environ.get("AWS_REGION", "us-west-2")
RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]
MEMORY_ID = os.environ["MEMORY_ID"]

client = boto3.client("bedrock-agentcore", region_name=REGION)
mem_client = MemoryClient(region_name=REGION)


def run_with_recovery(session_id: str, actor_id: str, task: str):
    try:
        return client.invoke_agent_runtime(
            agentRuntimeArn=RUNTIME_ARN, runtimeSessionId=session_id,
            payload=json.dumps({"prompt": task}).encode(),
        )
    except Exception:
        mem_client.create_event(
            memory_id=MEMORY_ID, actor_id=actor_id, session_id=session_id,
            messages=[("CRASH during scale_db_pool(payment-service, 100) -- incomplete", "SYSTEM")],
        )
        hits = mem_client.retrieve_memories(
            memory_id=MEMORY_ID, namespace=f"/recovery/{actor_id}",
            query="incomplete crash records", top_k=3,
        )
        resume_prompt = (
            f"A crash occurred. Recovery record: {hits}. "
            "Resume from the failed step only. Do not re-diagnose."
        )
        return client.invoke_agent_runtime(
            agentRuntimeArn=RUNTIME_ARN, runtimeSessionId=session_id,
            payload=json.dumps({"prompt": resume_prompt}).encode(),
        )


if __name__ == "__main__":
    sid = "incident-" + "a" * 40  # 49 chars, clears the 33-char minimum
    run_with_recovery(sid, "sre-junior-actor", "payment-service DB pool exhausted -- fix it")

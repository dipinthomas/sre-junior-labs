"""
Reference client code for AgentCore Memory -- confirmed against the real
bedrock_agentcore SDK (class and method names verified by introspection).

Needs a real MEMORY_ID from a deployed memory resource (see README) to actually
call AWS -- set it in your .env as MEMORY_ID, or pass it directly below.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from bedrock_agentcore.memory import MemoryClient  # NOT "BedrockAgentCoreMemoryClient"

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REGION = os.environ.get("AWS_REGION", "us-west-2")
MEMORY_ID = os.environ.get("MEMORY_ID")

mem_client = MemoryClient(region_name=REGION)


def save_turn(actor_id: str, session_id: str, user_prompt: str, agent_reply: str):
    """Real method is save_conversation() -- NOT store(). actor_id is required."""
    return mem_client.save_conversation(
        memory_id=MEMORY_ID,
        actor_id=actor_id,
        session_id=session_id,
        messages=[(user_prompt, "USER"), (agent_reply, "ASSISTANT")],
    )


def recall(actor_id: str, query: str, top_k: int = 3):
    """Real method is retrieve_memories() -- NOT retrieve(). actor_id is required."""
    return mem_client.retrieve_memories(
        memory_id=MEMORY_ID,
        namespace=f"/episodes/{actor_id}",
        query=query,
        top_k=top_k,
    )


if __name__ == "__main__":
    if not MEMORY_ID:
        print("Set MEMORY_ID in your .env first (see README.md) -- this is a reference, not a demo.")
    else:
        save_turn("sre-junior-actor", "demo-session-" + "x" * 30,
                   "payment-service fixed. Root cause was DB pool exhaustion.",
                   "Acknowledged. Closing incident.")
        print(recall("sre-junior-actor", "payment-service incidents"))

"""
G4 -- The Poison. Needs MEMORY_ID in .env (Track 2, Module 5).

Confirmed bugs fixed here (same client issue as G3):
- BedrockAgentCoreMemoryClient does not exist -- real class is MemoryClient.
- .store()/.retrieve() are not real methods -- real: create_event()/retrieve_memories(),
  both requiring actor_id.

NOTE: full poisoning demonstration (a real ticketing integration feeding untrusted
comment content into episodic summarisation) was NOT deployed/run end-to-end in
validation -- only the client and method names were corrected and confirmed to exist.
Treat write_lesson_learned/recall_past_incidents below as corrected-API-shape,
not a live-tested attack demo.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from strands import tool
from bedrock_agentcore.memory import MemoryClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REGION = os.environ.get("AWS_REGION", "us-west-2")
MEMORY_ID = os.environ.get("MEMORY_ID")

mem_client = MemoryClient(region_name=REGION)


@tool
def write_lesson_learned(incident_id: str, actor_id: str, root_cause: str, fix: str) -> str:
    """Write a lesson learned to episodic memory after an incident is resolved."""
    mem_client.create_event(
        memory_id=MEMORY_ID, actor_id=actor_id, session_id=incident_id,
        messages=[(f"Root cause: {root_cause}. Fix applied: {fix}. source=auto-resolved-incident", "ASSISTANT")],
    )
    return f"Lesson learned stored for {incident_id}"


@tool
def recall_past_incidents(service: str, actor_id: str) -> list:
    """Recall learned patterns for this service. Always call at session start."""
    return mem_client.retrieve_memories(
        memory_id=MEMORY_ID, namespace=f"/episodes/{actor_id}",
        query=f"incidents involving {service}", top_k=5,
    )

"""
G4 -- FIX. Provenance-tagged writes: reject un-verified sources, tag trust level.
Needs MEMORY_ID in .env. Same real client as learning_loop.py.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from strands import tool
from bedrock_agentcore.memory import MemoryClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
mem_client = MemoryClient(region_name=os.environ.get("AWS_REGION", "us-west-2"))
MEMORY_ID = os.environ.get("MEMORY_ID")


@tool
def write_lesson_learned(incident_id: str, actor_id: str, root_cause: str, fix: str,
                          source: str = "system", verified: bool = False) -> str:
    """Write lesson only when source is a verified system event."""
    if not verified:
        return "Lesson not stored -- requires verified=True from a system event."
    trust = "high" if source == "system" else "low"
    mem_client.create_event(
        memory_id=MEMORY_ID, actor_id=actor_id, session_id=incident_id,
        messages=[(f"[trust={trust}, source={source}] Root cause: {root_cause}. Fix: {fix}", "ASSISTANT")],
    )
    return f"Lesson learned stored for {incident_id} (trust={trust})"

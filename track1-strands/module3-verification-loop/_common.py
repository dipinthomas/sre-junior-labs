"""Shared setup for Module 3. Loads .env from the project root."""
import os
from pathlib import Path
from dotenv import load_dotenv
from strands.models import BedrockModel

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-pro-v1:0")
REGION = os.environ.get("AWS_REGION", "us-west-2")


def make_model() -> BedrockModel:
    return BedrockModel(model_id=MODEL_ID, region_name=REGION)


RUBRIC = """The response must contain ALL of:
1. A specific root cause (not just "there is an issue")
2. A concrete action to take (command, config change, or restart)
3. A rollback plan if the action makes things worse
4. Blast radius assessment (what else could be affected)
If any of these are missing, reject with specific feedback on what's absent."""

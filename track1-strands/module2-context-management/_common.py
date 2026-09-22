"""Shared setup for Module 2. Loads .env from the project root."""
import os
from pathlib import Path
from dotenv import load_dotenv
from strands.models import BedrockModel

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-pro-v1:0")
REGION = os.environ.get("AWS_REGION", "us-west-2")


def make_model() -> BedrockModel:
    return BedrockModel(model_id=MODEL_ID, region_name=REGION)


TURNS = [
    "Alert on payment-service. Check logs.",
    "Now check the metrics too.",
    "Check logs again - any change?",
    "Pull metrics once more to confirm.",
    "Check logs for auth-service as well.",
    "Now get metrics for auth-service too.",
]

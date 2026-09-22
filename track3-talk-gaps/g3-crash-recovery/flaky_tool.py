"""
G3 -- BUILD. Deterministically crashable tool for the lab. Plain Python, runs
anywhere -- no AWS-specific claims here, confirmed fine as originally written.
"""
import os, time
from strands import tool


@tool
def scale_db_pool(service: str, new_size: int) -> dict:
    """Scale the DB connection pool for a service. Takes ~10s to apply."""
    if os.getenv("INJECT_CRASH") == "true":
        time.sleep(2)
        raise TimeoutError(f"Infrastructure timeout scaling {service} pool")
    return {"status": "scaled", "new_pool_size": new_size}

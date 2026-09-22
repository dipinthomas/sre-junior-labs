"""
Confirmed fix for Module 4's session ID length bug.

runtimeSessionId has a hard AWS minimum of 33 characters. A short, natural ID
gets rejected with ValidationException before it ever reaches your agent.
"""
import hashlib


def make_session_id(user_id: str, incident_id: str) -> str:
    """Deterministic, user-scoped, always >= 33 chars."""
    raw = f"{user_id}:{incident_id}"
    return f"sess-{hashlib.sha256(raw.encode()).hexdigest()[:40]}"  # 45 chars


if __name__ == "__main__":
    sid = make_session_id("alice@company.com", "INC-20260922-042")
    print(sid, f"({len(sid)} chars)")
    assert len(sid) >= 33

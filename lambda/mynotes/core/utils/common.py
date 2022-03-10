from datetime import datetime, timezone

def now() -> datetime:
    """Return the current time in UTC format"""
    return  datetime.now(timezone.utc)

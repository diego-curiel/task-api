from datetime import datetime, timezone


def datetime_now() -> datetime:
    """
    Returns the actual date and time in UTC
    """
    return datetime.now(timezone.utc)

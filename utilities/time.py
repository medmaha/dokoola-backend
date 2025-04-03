import math
from typing import Optional
from datetime import datetime, timezone


def utc_datetime(timestamp: Optional[float] = None, add_minutes: Optional[int] = None) -> datetime:
    if timestamp:
        _timestamp = add_minutes_to_timestamp(timestamp, add_minutes)
    else :
        _timestamp = utc_timestamp(add_minutes)
    return datetime.fromtimestamp(timestamp=_timestamp, tz=timezone.utc)

def utc_timestamp(add_minutes: Optional[float] = None) -> float:
    unix_timestamp = datetime.now(tz=timezone.utc).timestamp()
    timestamp = add_minutes_to_timestamp(unix_timestamp, add_minutes)
    return timestamp

__all__ = [
    "utc_datetime",
    "utc_timestamp"
]

DEFAULT_ADD_MINUTE = 5

def add_minutes_to_timestamp(timestamp:float, minutes: Optional[float] = None) -> float:
    if not minutes:
        minutes = DEFAULT_ADD_MINUTE
    return (math.floor(timestamp) + (minutes))

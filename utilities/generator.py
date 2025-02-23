import time
from uuid import UUID
from uuid_v7.base import uuid7

from rest_framework.serializers import ReturnDict, ReturnList


def primary_key_generator():
    id = uuid7().__str__()
    return id


def default_pid_generator(prefix: str):
    _id = uuid7().__str__()
    return public_id_generator(_id, prefix)


def public_id_generator(_id: str, prefix: str, max_length=20):
    try:
        _uuid = UUID(id).__str__()
    except:
        _uuid = primary_key_generator()

    try:
        time_hex = _uuid[:8] + _uuid[9:11]
        version = _uuid[14]
        _randomA = _uuid[15:22]
        _randomB = _uuid[25:]

        _pid = str(f"{time_hex}{version}{_randomB}{_randomA}").replace("-", "").strip().lower()
        _prefix = prefix[:3].lower()

        # If the pid is longer than the max length, truncate it
        if len(_pid) > max_length:
            _pid = _pid[:max_length]

        return f"{_prefix}_{_pid}"
    except:
        return _id[:max_length]


def get_serializer_error_message(
    error: ReturnDict | ReturnList, message: str | None = None
):
    """A helper method to get error message from serializer errors"""

    if isinstance(error, ReturnDict):
        for key, value in error.items():
            if isinstance(value, (list, tuple)):
                for val in value:
                    if key and key != "non_field_errors":
                        return f"{key}: {val}"
                    return val
            if key and key != "non_field_errors":
                return f"{key}: {value}"
            return value

        if error.get("message"):
            return error["message"]

    if isinstance(error, ReturnList):
        for value in error:
            if isinstance(value, (list, tuple)):
                for val in value:
                    return val
            return value

    return message or "Something went wrong"

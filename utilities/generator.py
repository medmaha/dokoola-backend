import time
from random import randint

from rest_framework.serializers import ReturnDict, ReturnList
from uuid_v7.base import UUID, uuid7


def primary_key_generator():
    id = uuid7()
    return id


def default_pid_generator(prefix: str):
    _id = uuid7().__str__()
    return public_id_generator(_id, prefix)


def public_id_generator(_id, prefix: str, max_length=20):
    _id = str(_id)
    try:
        _uuid = UUID(_id).__str__()
    except:
        _uuid = primary_key_generator().__str__()

    try:
        time_hex = _uuid[:8] + _uuid[9:11]
        version = _uuid[14]
        _randomA = _uuid[15:22]
        _randomB = _uuid[25:]
        _prefix = prefix[:3].lower()
        _pid = (
            str(f"{time_hex}{version}{_randomB}{_randomA}")
            .replace("-", "")
            .strip()
            .lower()
        )
        # If the pid is longer than the max length, truncate it
        if len(_pid) > max_length:
            _pid = _pid[:max_length]
        return f"{_prefix}_{_pid}".replace("-", "")

    except:
        return _id[:max_length]


def get_serializer_error_message(
    error: ReturnDict | ReturnList, default_message: str | None = None
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

    return default_message or "Something went wrong"


def generate_ott() -> str:
    return "".join(str(randint(0, 9)) for _ in range(5))

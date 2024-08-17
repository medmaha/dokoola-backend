import uuid
from rest_framework.serializers import ReturnDict, ReturnList


def id_generator(size=20):
    id = uuid.uuid4().hex

    return id[:size]


def hex_generator(size=15):
    id = uuid.uuid4().hex

    id.replace("-", "")

    return id[:size]


def get_serializer_error_message(
    error: ReturnDict | ReturnList, message: str | None = None
):
    """A helper method to get error message from serializer errors"""

    if isinstance(error, ReturnDict):
        for key, value in error.items():
            if isinstance(value, list) or isinstance(value, tuple):
                for val in value:
                    if key and key != "non_field_errors":
                        return "{}: {}".format(key, val)
                    return val
            if key and key != "non_field_errors":
                return "{}: {}".format(key, value)
            return value

        if error.get("message"):
            return error["message"]

    if isinstance(error, ReturnList):
        for value in error:
            if isinstance(value, list) or isinstance(value, tuple):
                for val in value:
                    return val
            return value

    return message or "Something went wrong"

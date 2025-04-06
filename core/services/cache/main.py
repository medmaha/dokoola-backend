from typing import Any
import json
from django.core.cache import cache

import after_response

@after_response.enable
def set_cache(key:str, value:Any, stringify=False):
    try:
        if stringify and not isinstance(value, str):
            value = json.dumps(value)
    except:
        pass
    cache.set(key, value)


class DokoolaCacheService:
    """Service for managing and executing callbacks after HTTP response"""

    @classmethod
    def set(cls, key: str, value: Any, stringify=True) -> None:
        set_cache.after_response(key, value, stringify)

    @classmethod
    def get(cls, key: str, default: Any=None, is_json=True) -> Any | None:
        data = cache.get(key, default=default)

        try:
            if is_json and isinstance(data, str):
                data = json.loads(data)     
        except:
            pass

        return data

    @classmethod
    def delete(cls, key: str) -> None:
        cache.delete(key)


__all__ = ["DokoolaCacheService"]

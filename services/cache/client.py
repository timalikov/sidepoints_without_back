from typing import Dict, Optional, Any
import time
import threading

class _CustomCache:
    _instance = None
    _stage: Dict
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "_CustomCache":
        if not isinstance(cls._instance, cls):
            cls._instance = super(cls.__class__, cls).__new__(cls, *args, **kwargs)
            cls._instance._stage = {}
        return cls._instance
    
    def get_value(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._stage.get(key)
            if item:
                value, expiration = item
                if expiration is None or expiration > time.time():
                    return value
                else:
                    del self._stage[key]
        return None
    
    def set_value(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            expiration = time.time() + ttl if ttl else None
            self._stage[key] = (value, expiration)
    
    def set_user_invite(
        self,
        user_id: int,
        invite_link: str,
        channel_name: str,
        guild_id: int,
    ) -> None:
        self.set_value(
            key=f"{user_id}",
            value={"invite_link": invite_link, "channel_name": channel_name, "guild_id": guild_id},
            ttl=86400
        )

    def get_user_invite(
        self,
        user_id: int,
    ) -> Optional[Dict[str, str]]:
        return self.get_value(key=f"{user_id}")
    

custom_cache = _CustomCache()

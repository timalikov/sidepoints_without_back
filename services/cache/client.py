import re
from typing import Dict, Optional, Any, Dict
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
    
    def set_top_up(
        self,
        user_id: int,
        balance: float
    ) -> None:
        self.set_value(
            key=f"top_up_{user_id}",
            value={"balance": balance, "attempt": 0}
        )

    def get_top_up(
        self,
        user_id: int
    ) -> Optional[Dict[str, int]]:
        return self.get_value(key=f"top_up_{user_id}")
    
    def set_purchase_id(
        self,
        purchase_id: int
    ) -> None:
        self.set_value(
            key=f"purchase_{purchase_id}",
            value=True,
            ttl=600
        )
    
    def get_purchase_id(self, purchase_id: int) -> Optional[Dict[str, int]]:
        return self.get_value(key=f"purchase_{purchase_id}")

    def get_all_top_up_users(self) -> Optional[Dict[str, int]]:
        pattern = r"^top_up_"
        all_keys = self._stage.keys()
        users: Dict[str, Dict[str, int]] = {}
        key: str
        for key in all_keys:
            if re.match(pattern, key):
                users[key.removeprefix("top_up_")] = self.get_value(key)
        return users
    
    def delete_top_up(self, user_id: int) -> None:
        try:
            del self._stage[f"top_up_{user_id}"]
        except KeyError:
            return

    def retry_top_up(
        self,
        user_id: int
    ) -> Optional[Dict[str, int]]:
        key = f"top_up_{user_id}"
        value = self.get_top_up(user_id)
        try:
            attempt = int(value["attempt"])
        except (ValueError, TypeError):
            return
        if attempt > 20:
            self.delete_top_up(user_id)
        else:
            attempt += 1
            value["attempt"] = attempt
            self.set_value(key=key, value=value)
    

custom_cache = _CustomCache()

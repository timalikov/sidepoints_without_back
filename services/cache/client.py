from typing import Dict, Optional, Any


class _CustomCache:
    _instance = None
    _stage: Dict

    def __new__(cls, *args, **kwargs) -> "_CustomCache":
        if not isinstance(cls._instance, cls):
            cls._instance =  super(cls.__class__, cls).__new__(cls, *args, **kwargs)
            cls._instance._stage = {}
        return cls._instance
    
    def get_value(self, key: str) -> Optional[Any]:
        return self._stage.get(key)
    
    def set_value(self, key: str, value: Any) -> Any:
        self._stage[key] = value
        return value
    
    def set_order_server_id(
        self,
        customer_id: int,
        kicker_id: int,
        server_id: int
    ) -> int:
        self.set_value(
            key=f"order-{customer_id}-{kicker_id}",
            value=server_id
        )

    def get_order_server_id(
        self,
        customer_id: int,
        kicker_id: int
    ) -> Optional[str]:
        return self.get_value(key=f"order-{customer_id}-{kicker_id}")
    

custom_cache = _CustomCache()

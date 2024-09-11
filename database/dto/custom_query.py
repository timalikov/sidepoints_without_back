from typing import Any, Literal


class CustomQuery:
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        self._query = f"SELECT * FROM {table_name}"

    def get(self) -> str:
        return self._query
    
    def add_filter(
        self,
        column: str,
        value: Any,
        operation: Literal['gte", "lte", "gt", "lt", "eq", "not", "like']
    ) -> None:
        operation_serializer: dict = {
            "gte": ">=",
            "lte": "<=",
            "gt": ">",
            "lt": "<",
            "eq": "IS" if isinstance(value, type(None)) else "=",
            "not": "IS NOT" if isinstance(value, type(None)) else "!=",
            "like": "LIKE",
        }
        symbol: str = operation_serializer.get(operation)
        if not symbol:
            raise ValueError("Enter current operation!")
        if "WHERE" in self._query:
            self._query += " AND "
        else:
            self._query += " WHERE "
        self._query += f"{column} {operation} {value}"
        
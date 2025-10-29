from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class Serializer:
    @classmethod
    def encode(cls, data: Any) -> Any:
        """
        Serialize different types of data to JSON-compatible format.

        Args:
            data (Any): The data to be serialized.

        Returns:
            Any: Serialized data.
        """
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")

        if isinstance(data, dict):
            return {key: cls.encode(value) for key, value in data.items()}

        if isinstance(data, (list, set, tuple)):
            return [cls.encode(item) for item in data]

        if isinstance(data, datetime):
            return data.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(data, (str, int, float, bool, type(None))):
            return data

        if isinstance(data, Enum):
            return data.value

        if hasattr(data, "__dict__"):
            data_dict: dict[str, Any] = data.__dict__
            data = {k: v for k, v in data_dict.items() if not k.startswith("_")}
            return cls.encode(data)

        return str(data)

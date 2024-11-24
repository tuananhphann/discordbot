from dataclasses import dataclass, asdict
from typing import Any, Union


# Base class for JSON serialization
@dataclass
class JsonObject:
    def to_dict(self) -> dict:
        def _convert(obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif isinstance(obj, list):
                return [_convert(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            else:
                return obj

        return {k: _convert(v) for k, v in asdict(self).items()}

    @classmethod
    def from_dict(cls, data: dict) -> "JsonObject":
        field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}

        def _convert(value: Any, target_type: Any) -> Any:
            if value is None:
                return None
            if hasattr(target_type, "from_dict"):
                return target_type.from_dict(value)
            if hasattr(target_type, "__origin__"):  # Handle List, Dict, Optional
                if target_type.__origin__ is list:
                    item_type = target_type.__args__[0]
                    return [_convert(item, item_type) for item in value]
                if target_type.__origin__ is dict:
                    return value
                if target_type.__origin__ is Union:  # Optional is Union[type, None]
                    inner_type = target_type.__args__[0]
                    return _convert(value, inner_type)
            return value

        kwargs = {
            key: _convert(value, field_types[key])
            for key, value in data.items()
            if key in field_types
        }
        return cls(**kwargs)

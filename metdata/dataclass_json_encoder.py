"""Provides a simple json.JSONEncoder object that transparently handles dataclasses, datetime objects, and date objects."""
import dataclasses, json, typing
from datetime import datetime, date


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)

        elif isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        else:
            return super().default(obj)

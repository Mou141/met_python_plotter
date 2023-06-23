"""Provides a simple json.JSONEncoder class that transparently handles dataclasses, datetime objects, time objects, timedelta objects, and date objects."""
import dataclasses
import json
import typing
from datetime import date, datetime, time, timedelta

__all__ = ["DataclassJSONEncoder"]


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)

        elif isinstance(obj, (datetime, date, time)):
            return obj.isoformat()

        elif isinstance(obj, timedelta):
            return obj.total_seconds()

        else:
            return super().default(obj)

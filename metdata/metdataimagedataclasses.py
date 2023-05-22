"""Data classes for handling data related to images from the API."""
from dataclasses import dataclass
from datetime import datetime, time
import typing

__all__ = ["SurfacePressureChartCapability"]


@dataclass(frozen=True)
class SurfacePressureChartCapability:
    data_date: datetime
    valid_from: datetime
    valid_to: datetime
    uri: str
    data_date_time: time
    period: int

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts data retrieved from the api to an instance of this class."""
        return cls(
            data_date=datetime.fromisoformat(d["DataDate"]),
            valid_from=datetime.fromisoformat(d["ValidFrom"]),
            valid_to=datetime.fromisoformat(d["ValidTo"]),
            uri=d["ProductURI"],
            data_date_time=time.fromisoformat(str(d["DataDateTime"]))
            if d["DataDateTime"] != 2400
            else time(0, 0),
            period=int(d["ForecastPeriod"]),
        )

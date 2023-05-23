"""Data classes for handling data related to images from the API."""
from dataclasses import dataclass
from datetime import datetime
import typing

__all__ = [
    "SurfacePressureChartCapability",
    "ForecastLayer",
    "ForecastLayerData",
    "ObservationLayer",
    "ObservationLayerData",
]


@dataclass(frozen=True)
class SurfacePressureChartCapability:
    data_date: datetime
    valid_from: datetime
    valid_to: datetime
    uri: str
    data_date_time: int
    period: int

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts data retrieved from the api to an instance of this class."""
        return cls(
            data_date=datetime.fromisoformat(d["DataDate"]),
            valid_from=datetime.fromisoformat(d["ValidFrom"]),
            valid_to=datetime.fromisoformat(d["ValidTo"]),
            uri=d["ProductURI"],
            data_date_time=int(d["DataDateTime"]),
            period=int(d["ForecastPeriod"]),
        )


@dataclass(frozen=True)
class BaseLayer:
    display_name: str
    name: str
    layer_name: str


@dataclass(frozen=True)
class ForecastLayer(BaseLayer):
    default_time: datetime
    timesteps: list[int]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            display_name=d["@displayName"],
            name=d["Service"]["@name"],
            layer_name=d["Service"]["LayerName"],
            default_time=datetime.fromisoformat(
                d["Service"]["Timesteps"]["@defaultTime"]
            ),
            timesteps=[int(t) for t in d["Service"]["Timesteps"]["Timestep"]],
        )


@dataclass(frozen=True)
class ObservationLayer(BaseLayer):
    times: list[datetime]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            display_name=d["@displayName"],
            name=d["Service"]["@name"],
            layer_name=d["Service"]["LayerName"],
            times=[datetime.fromisoformat(t) for t in d["Service"]["Times"]["Time"]]
            if isinstance(d["Service"]["Times"]["Time"], list)
            else [datetime.fromisoformat(d["Service"]["Times"]["Time"])],
        )


@dataclass(frozen=True)
class BaseLayerData:
    type: str
    time_format: str
    base_url: str


@dataclass(frozen=True)
class ForecastLayerData(BaseLayerData):
    layers: list[ForecastLayer]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            type=d["@type"],
            time_format=d["BaseUrl"]["@forServiceTimeFormat"],
            base_url=d["BaseUrl"]["$"],
            layers=[ForecastLayer.from_dict(l) for l in d["Layer"]]
            if isinstance(d["Layer"], list)
            else [ForecastLayer.from_dict(d["Layer"])],
        )


@dataclass(frozen=True)
class ObservationLayerData(BaseLayerData):
    layers: list[ObservationLayer]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            type=d["@type"],
            time_format=d["BaseUrl"]["@forServiceTimeFormat"],
            base_url=d["BaseUrl"]["$"],
            layers=[ObservationLayer.from_dict(l) for l in d["Layer"]]
            if isinstance(d["Layer"], list)
            else [ObservationLayer.from_dict(d["Layer"])],
        )

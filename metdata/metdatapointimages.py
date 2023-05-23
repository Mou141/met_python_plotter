"""Provides a subclass for getting images and associated data from the API."""
from PIL import Image
from datetime import datetime
import typing

from .metdatapoint import METDataPoint
from .metdataimagedataclasses import (
    SurfacePressureChartCapability,
    ForecastLayer,
    ForecastLayerData,
    ObservationLayer,
    ObservationLayerData,
)

__all__ = [
    "ImageMETDataPoint",
    "SurfacePressureChartCapability",
    "ForecastLayer",
    "ForecastLayerData",
    "ObservationLayer",
    "ObservationLayerData",
]


class ImageMETDataPoint(METDataPoint):
    """Subclass of METDataPoint to handle retrieving images and associated data
    while retaining all the original methods of the base class."""

    def get_surface_pressure_chart_capabilities(
        self,
    ) -> list[SurfacePressureChartCapability]:
        """Gets the list of available surface pressure images from the API."""
        r = self._session.get(
            f"{self.base_url}image/wxfcs/surfacepressure/json/capabilities",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return [
            SurfacePressureChartCapability.from_dict(s)
            for s in j["BWSurfacePressureChartList"]["BWSurfacePressureChart"]
        ]

    def get_surface_pressure_chart(self, period: int) -> Image.Image:
        """Gets the specified surface pressure chart from the API (in GIF format)
        and returns it as a PIL.Image instance."""

        with self._session.get(
            f"{self.base_url}image/wxfcs/surfacepressure/gif",
            params={"key": self.key, "timestep": period},
            stream=True,
        ) as r:
            r.raise_for_status()
            return Image.open(r.raw, formats=["GIF"])

    def get_all_surface_pressure_charts(
        self,
    ) -> typing.Generator[tuple[int, Image.Image], None, None]:
        """Yields the period and loaded image data of every available surface pressure chart."""

        periods = (c.period for c in self.get_surface_pressure_chart_capabilities())

        for p in periods:
            yield p, self.get_surface_pressure_chart(p)

    def get_forecast_layer_capabilities(self) -> ForecastLayerData:
        """Gets the types of forecast layers available and the timesteps for which each can be downloaded."""
        r = self._session.get(
            f"{self.base_url}layer/wxfcs/all/json/capabilities",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return ForecastLayerData.from_dict(j["Layers"])

    def get_forecast_layer_capabilities_as_dict(
        self,
    ) -> dict[str, tuple[datetime, list[int]]]:
        """Gets the types of forecast laters available and the timesteps for which each can be downloaded.
        However, this method returns a dictionary which maps the layer name to
        the default time that timesteps are measured from and the list of available time steps.
        """
        forecast_layers = self.get_forecast_layer_capabilities()

        return {
            l.layer_name: (l.default_time, l.timesteps) for l in forecast_layers.layers
        }

    def get_forecast_layer_at_time(
        self, layer_name: str, default_time: datetime | str, timestep: int
    ) -> Image.Image:
        """Gets an image of the specified forecast layer at the specified timestep."""

        if isinstance(default_time, datetime):
            default_time = default_time.isoformat()

        with self._session.get(
            f"{self.base_url}layer/wxfcs/{layer_name}/png",
            params={
                "key": self.key,
                "RUN": (default_time + "Z"),
                "FORECAST": timestep,
            },
            stream=True,
        ) as r:
            r.raise_for_status()
            return Image.open(r.raw, formats=["PNG"])

    def get_all_forecast_layers_of_type(
        self, layer_name: str
    ) -> typing.Generator[tuple[int, Image.Image], None, None]:
        """Gets the specified layer images at all available timesteps and yields them to the user.
        If layer_name is not a valid layer name then ValueError is raised."""
        layer_dict = self.get_forecast_layer_capabilities_as_dict()

        if layer_name not in layer_dict.keys():
            raise ValueError(
                f"'{layer_name}' is not a valid layer name (valid options: '{' ,'.join(layer_dict.keys())}')."
            )

        default_time, timesteps = layer_dict[layer_name]

        for t in timesteps:
            yield t, self.get_forecast_layer_at_time(layer_name, default_time, t)

    def get_observation_layer_capabilities(self) -> ObservationLayerData:
        """Gets the types of observation layer available and the timesteps for which they can be downloaded."""
        r = self._session.get(
            f"{self.base_url}layer/wxobs/all/json/capabilities",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return ObservationLayerData.from_dict(j["Layers"])

    def get_observation_layer_capabilities_as_dict(self) -> dict[str, list[datetime]]:
        """Gets the types of observation layer available and the timesteps for which they can be downloaded.
        However, this method returns a dictionary that maps the layer names to a list of available timesteps.
        """
        observation_layers = self.get_observation_layer_capabilities()

        return {o.layer_name: o.times for o in observation_layers.layers}

    def get_observation_layer_at_time(
        self, layer_name: str, timestep: datetime | str
    ) -> Image.Image:
        """Gets an image of the specified observation layer at the specified timestep."""

        if isinstance(timestep, datetime):
            timestep = timestep.isoformat()

        with self._session.get(
            f"{self.base_url}layer/wxobs/{layer_name}/png",
            params={"key": self.key, "TIME": (timestep + "Z")},
            stream=True,
        ) as r:
            r.raise_for_status()
            return Image.open(r.raw, formats=["PNG"])

    def get_all_observation_layers_of_type(
        self, layer_name: str
    ) -> typing.Generator[tuple[datetime, Image.Image], None, None]:
        """Gets the specified layer images at all available timesteps and yields them to the user.
        If layer_name is not a valid layer name, ValueError is raised."""
        layer_dict = self.get_observation_layer_capabilities_as_dict()

        if not layer_name in layer_dict.keys():
            raise ValueError(
                f"'{layer_name}' is not a valid layer name (valid options: '{' ,'.join(layer_dict.keys())}')."
            )

        for t in layer_dict[layer_name]:
            yield t, self.get_observation_layer_at_time(layer_name, t)

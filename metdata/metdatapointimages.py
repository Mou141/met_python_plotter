"""Provides a subclass for getting images and associated data from the API."""
from PIL import Image
import typing

from .metdatapoint import METDataPoint
from .metdataimagedataclasses import (
    SurfacePressureChartCapability,
    ForecastLayer,
    ForecastLayerData,
)

__all__ = [
    "ImageMETDataPoint",
    "SurfacePressureChartCapability",
    "ForecastLayer",
    "ForecastLayerData",
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
    ) -> dict[str, list[int]]:
        """Gets the types of forecast laters availableand the timesteps for which each can be downloaded.
        However, this method returns a dictionary which maps the layer name to the list of available time steps.
        """
        forecast_layers = self.get_forecast_layer_capabilities()

        return {l.layer_name: l.timesteps for l in forecast_layers.layers}

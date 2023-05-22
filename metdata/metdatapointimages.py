"""Provides a subclass for getting images and associated data from the API."""
from PIL import Image

from .metdatapoint import METDataPoint
from .metdataimagedataclasses import SurfacePressureChartCapability

__all__ = ["ImageMETDataPoint", "SurfacePressureChartCapability"]


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

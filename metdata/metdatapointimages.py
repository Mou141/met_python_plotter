"""Provides a subclass for getting images and associated data from the API."""
from PIL import Image

from .metdatapoint import METDataPoint

__all__ = ["ImageMETDataPoint"]


class ImageMETDataPoint(METDataPoint):
    """Subclass of METDataPoint to handle retrieving images and associated data
    while retaining all the original methods of the base class."""
    pass

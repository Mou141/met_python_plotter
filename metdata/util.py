"""Utility functions for interacting with the MET DataPoint API."""
from .metdataclasses import SiteInfo
from math import radians, sin, cos, acos

EARTH_RADIUS = 6371.009  # km

# sin and cos in degrees
dsin = lambda d: sin(radians(d))
dcos = lambda d: cos(radians(d))


def get_distance(lat1: float, long1: float, lat2: float, long2: float) -> float:
    """Gets the distance in km between two sets of coordinates."""
    return EARTH_RADIUS * acos(
        (dsin(lat1) * dsin(lat2)) + (dcos(lat1) * dcos(lat2) * dcos(abs(long1 - long2)))
    )


def get_closest(sites: list[SiteInfo], latitude: float, longitude: float) -> SiteInfo:
    """Returns the site in the list that is closest to the specified longitude and latitude."""
    return min(
        sites, key=lambda s: get_distance(s.latitude, s.longitude, latitude, longitude)
    )
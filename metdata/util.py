"""Utility functions for interacting with the MET DataPoint API."""
from datetime import date, datetime, time, timedelta, timezone
from math import acos, cos, radians, sin

from .metdataclasses import SiteInfo

__all__ = ["get_3hourly_forecast_datetime", "get_3hourly_forecast_time", "get_closest"]

EARTH_RADIUS = 6371.009  # km

# sin and cos in degrees
dsin = lambda d: sin(radians(d))
dcos = lambda d: cos(radians(d))


def get_3hourly_forecast_datetime(d: date, delta: timedelta) -> datetime:
    """Takes the date of a 3hourly forecast and the time since midnight of the forecast and returns a datetime object representing the forecast time."""
    return datetime.combine(d, time(0, 0, tzinfo=timezone.utc)) + delta


def get_3hourly_forecast_time(d: date, delta: timedelta) -> time:
    """Takes thedate of a 3hourly forecast and the time since midnight of the forecast and returns a time object representing the forecast time."""
    return get_3hourly_forecast_datetime(d, delta).time()


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

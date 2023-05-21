"""A simple object oriented interface for the MET Office's DataPoint API."""

import requests, functools, typing
from datetime import datetime, date
from .metdataclasses import (
    SiteInfo,
    Resolution,
    Forecast,
    Observation,
    UKExtremes,
    NationalParkLocation,
    RegionalForecastLocation,
    RegionalForecast,
    MountainAreaLocation,
)

__all__ = ["METDataPoint"]


class METDataPoint:
    """Downloads data from the MET DataPoint API.

    key: The key to use to access the MET DataPoint API."""

    base_url: str = "http://datapoint.metoffice.gov.uk/public/data/"

    def __init__(self, key: str):
        self.key = key

    @functools.cached_property
    def _session(self) -> requests.Session:
        """Session object to use to perform HTTP requests."""
        return requests.Session()

    def get_wxfcs_site_list(self) -> list[SiteInfo]:
        """Returns the list of sites for which daily and three-hourly data feeds are available."""
        r = self._session.get(
            f"{self.base_url}/val/wxfcs/all/json/sitelist",
            params={"key": self.key},
        )

        r.raise_for_status()
        return [SiteInfo.from_dict(s) for s in r.json()["Locations"]["Location"]]

    def get_wxobs_site_list(self) -> list[SiteInfo]:
        """Returns the list of sites for which hourly observation results are available."""
        r = self._session.get(
            f"{self.base_url}val/wxobs/all/json/sitelist", params={"key": self.key}
        )

        r.raise_for_status()
        return [SiteInfo.from_dict(s) for s in r.json()["Locations"]["Location"]]

    def get_wxfcs_capabilities(
        self, res: Resolution | str
    ) -> tuple[datetime, list[datetime]] | tuple[datetime, list[date]]:
        """Returns the date of the last data update and time steps available for the daily or three-hourly forecast feed (specify which with the res parameter)."""
        r = self._session.get(
            f"{self.base_url}val/wxfcs/all/json/capabilities",
            params={"key": self.key, "res": res},
        )

        r.raise_for_status()
        j = r.json()

        data_date = datetime.fromisoformat(j["Resource"]["dataDate"])

        if res == Resolution.DAILY:
            # For daily resolution, discard time portion
            time_steps = [
                datetime.fromisoformat(ts).date()
                for ts in j["Resource"]["TimeSteps"]["TS"]
            ]
        else:
            time_steps = [
                datetime.fromisoformat(ts) for ts in j["Resource"]["TimeSteps"]["TS"]
            ]

        return data_date, time_steps

    def get_wxobs_capabilities(self) -> list[datetime]:
        """Returns the timesteps for which observations are available (as datetime objects)."""
        r = self._session.get(
            f"{self.base_url}val/wxobs/all/json/capabilities",
            params={"key": self.key, "res": "hourly"},
        )

        r.raise_for_status()
        j = r.json()

        return [datetime.fromisoformat(d) for d in j["Resource"]["TimeSteps"]["TS"]]

    def get_forecasts(
        self,
        res: Resolution | str,
        location_id: int | str,
        time: typing.Optional[datetime | date | str] = None,
    ) -> tuple[datetime, Forecast]:
        """Returns forecasts for a specific location (or all locations if "all" is passed) at either daily or three-hourly resolution (as specified by the res parameter).
        To get a specific forecast, specify the time parameter."""
        params = {"key": self.key, "res": res}

        if time is not None:
            # If a time parameter is specified then a specific forecast has been requested rather than all available forecasts
            if isinstance(time, (datetime, date)):
                params["time"] = time.isoformat()
            else:
                params["time"] = time

        r = self._session.get(
            f"{self.base_url}val/wxfcs/all/json/{location_id}", params=params
        )

        r.raise_for_status()
        j = r.json()

        data_date = datetime.fromisoformat(j["SiteRep"]["DV"]["dataDate"])
        forecast = Forecast.from_dict(j["SiteRep"]["DV"]["Location"], res)

        return data_date, forecast

    def get_observations(
        self, location_id: int | str
    ) -> tuple[datetime, typing.Optional[Observation]]:
        """Returns the observation data and the date and time of the last update for a specific location.
        If no data is available for that location, then the date of last update and None are returned.
        """
        r = self._session.get(
            f"{self.base_url}val/wxobs/all/json/{location_id}",
            params={"key": self.key, "res": "hourly"},
        )

        r.raise_for_status()
        j = r.json()

        data_date = datetime.fromisoformat(j["SiteRep"]["DV"]["dataDate"])

        if "Location" not in j["SiteRep"]["DV"].keys():
            # There is no data for this location (although it is still a valid location)
            observation = None
        else:
            observation = Observation.from_dict(j["SiteRep"]["DV"]["Location"])

        return data_date, observation

    def get_uk_extremes_capabilities(self) -> tuple[date, datetime]:
        """Gets the date of the last UK extremes observation and the date and time the observation was issued."""
        r = self._session.get(
            f"{self.base_url}txt/wxobs/ukextremes/json/capabilities",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return date.fromisoformat(
            j["UkExtremes"]["extremeDate"]
        ), datetime.fromisoformat(j["UkExtremes"]["issuedAt"])

    def get_uk_extremes(self) -> UKExtremes:
        """Gets the latest extremes of weather in the UK."""
        r = self._session.get(
            f"{self.base_url}txt/wxobs/ukextremes/json/latest", params={"key": self.key}
        )

        r.raise_for_status()
        j = r.json()

        return UKExtremes.from_dict(j["UkExtremes"])

    def get_national_park_locations(self) -> list[NationalParkLocation]:
        """Gets the list of national park locations."""
        # The API doesn't seem to be responding to requests to the appropriate URL
        raise NotImplementedError

    def get_national_park_capabilities(self):
        """Gets the list of forecasts available for each national park."""
        # The API doesn't seem to be responding to requests to the appropriate URL
        raise NotImplementedError

    def get_national_park_forecasts(self, location_id: int | str):
        """Gets the national park forecasts for the given national park location (or 'all')."""
        # The API doesn't seem to be responding to requests to the appropriate URL
        raise NotImplementedError

    def get_regional_forecast_site_list(self) -> list[RegionalForecastLocation]:
        """Gets the list of locations for which regional forecasts are available."""
        r = self._session.get(
            f"{self.base_url}txt/wxfcs/regionalforecast/json/sitelist",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return [
            RegionalForecastLocation.from_dict(r) for r in j["Locations"]["Location"]
        ]

    def get_regional_forecast_capabilities(self) -> datetime:
        """Gets the date and time at which the most recent regional forecasts were issued."""
        r = self._session.get(
            f"{self.base_url}txt/wxfcs/regionalforecast/json/capabilities",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return datetime.fromisoformat(j["RegionalFcst"]["issuedAt"])

    def get_regional_forecast(self, location_id: int) -> RegionalForecast:
        """Gets the regional forecast at the specified location."""
        r = self._session.get(
            f"{self.base_url}txt/wxfcs/regionalforecast/json/{location_id}",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return RegionalForecast.from_dict(j["RegionalFcst"])

    def get_mountain_area_site_list(self) -> list[MountainAreaLocation]:
        """Gets the list of of mountain area forecast sites."""
        r = self._session.get(
            f"{self.base_url}txt/wxfcs/mountainarea/json/sitelist",
            params={"key": self.key},
        )

        r.raise_for_status()
        j = r.json()

        return [MountainAreaLocation.from_dict(l) for l in j["Locations"]["Location"]]

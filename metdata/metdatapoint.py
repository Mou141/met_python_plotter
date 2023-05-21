"""A simple object oriented interface for the MET Office's DataPoint API."""

import requests, functools, typing
from datetime import datetime, date
from .metdataclasses import SiteInfo, Resolution, Forecast, Observation

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
            if isinstance(time, datetime) or isinstance(time, date):
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

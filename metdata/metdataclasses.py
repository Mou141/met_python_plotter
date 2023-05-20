import typing, enum

from dataclasses import dataclass
from datetime import date, timedelta


class Resolution(enum.StrEnum):
    THREE_HOURLY = "3hourly"
    DAILY = "daily"


@dataclass(frozen=True)
class SiteInfo:
    """Holds the information on each site returned by METDataPoint.get_wxfcs_site_list and METDataPoint.get_wxobs_site_list."""

    id: int
    latitude: float
    longitude: float
    name: str

    def get_coordinates(self) -> tuple[float, float]:
        """Returns latitude and longitude in a tuple."""
        return self.latitude, self.longitude

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the dictionary returned by the DataPoint API to an instance of this class."""
        return cls(
            id=int(d["id"]),
            latitude=float(d["latitude"]),
            longitude=float(d["longitude"]),
            name=d["name"],
        )


@dataclass(frozen=True)
class ForecastLocation(SiteInfo):
    """Holds the location information of each forecast returned by the METDataPoint API."""

    country: str
    continent: str

    # This is optional because the API returns it but it's not specified in the documentation
    elevation: typing.Optional[float] = None

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the dictionary returned by the DataPoint API to an instance of this class."""

        if "elevation" in d.keys():
            elevation = float(d["elevation"])
        else:
            elevation = None

        return cls(
            id=int(d["i"]),
            latitude=float(d["lat"]),
            longitude=float(d["lon"]),
            name=d["name"],
            country=d["country"],
            continent=d["continent"],
            elevation=elevation,
        )


class Period(enum.StrEnum):
    DAY = "Day"
    NIGHT = "Night"


class Visibility(enum.StrEnum):
    UNKNOWN = "UN"
    VERY_POOR = "VP"
    POOR = "PO"
    MODERATE = "MO"
    GOOD = "GO"
    VERY_GOOD = "VG"
    EXCELLENT = "EX"


class SignificantWeather(enum.IntEnum):
    CLEAR_NIGHT = 0
    SUNNY_DAY = 1
    PARTLY_CLOUDY_NIGHT = 2
    PARTLY_CLOUDY_DAY = 3
    MIST = 5
    FOG = 6
    CLOUDY = 7
    OVERCAST = 8
    LIGHT_RAIN_SHOWER_NIGHT = 9
    LIGHT_RAIN_SHOWER_DAY = 10
    DRIZZLE = 11
    LIGHT_RAIN = 12
    HEAVY_RAIN_SHOWER_NIGHT = 13
    HEAVY_RAIN_SHOWER_DAY = 14
    HEAVY_RAIN = 15
    SLEET_SHOWER_NIGHT = 16
    SLEET_SHOWER_DAY = 17
    SLEET = 18
    HAIL_SHOWER_NIGHT = 19
    HAIL_SHOWER_DAY = 20
    HAIL = 21
    LIGHT_SNOW_SHOWER_NIGHT = 22
    LIGHT_SNOW_SHOWER_DAY = 23
    LIGHT_SNOW = 24
    HEAVY_SNOW_SHOWER_NIGHT = 25
    HEAVY_SNOW_SHOWER_DAY = 26
    HEAVY_SNOW = 27
    THUNDER_SHOWER_NIGHT = 28
    THUNDER_SHOWER_DAY = 29
    THUNDER = 30

    @classmethod
    def from_returned_str(cls, s: str) -> typing.Optional[typing.Self]:
        """The API returns an integer in string format (or 'NA' for if not available)."""
        if s == "NA":
            return None
        else:
            return cls(int(s))


class Visibility(enum.StrEnum):
    UNKNOWN = "UN"
    VERY_POOR = "VP"
    POOR = "PO"
    MODERATE = "MO"
    GOOD = "GO"
    VERY_GOOD = "VG"
    EXCELLENT = "EX"

    @classmethod
    def from_returned_str(cls, s: str) -> typing.Self | int:
        """The API can return a string describing visibility or a distance in metres.
        This function will handle either possibility."""
        try:
            return int(s)
        except ValueError:
            return cls(s)


class WindDirection(enum.StrEnum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
    NORTH_EAST = "NE"
    SOUTH_EAST = "SE"
    SOUTH_WEST = "SW"
    NORTH_WEST = "NW"
    NORTH_NORTH_EAST = "NNE"
    EAST_NORTH_EAST = "ENE"
    EAST_SOUTH_EAST = "ESE"
    SOUTH_SOUTH_WEST = "SSW"
    SOUTH_SOUTH_EAST = "SSE"
    WEST_SOUTH_WEST = "WSW"
    WEST_NORTH_WEST = "WNW"
    NORTH_NORTH_WEST = "NNW"


@dataclass(frozen=True)
class BaseForecastRep:
    visibility: Visibility
    wind_direction: WindDirection
    wind_speed: float
    wind_gust: float
    weather_type: typing.Optional[SignificantWeather]
    max_uv_index: typing.Optional[int]
    temperature: float
    feels_like_temperature: float
    precipitation_probability: float
    relative_humidity: float

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Gets the appropriate class to represent the 'Rep' objects for this type of forecast."""
        raise NotImplementedError()


@dataclass(frozen=True)
class DailyForecastRep(BaseForecastRep):
    period: Period

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Gets the appropriate class to represent the 'Rep' objects for this type of forecast."""
        return cls(
            feels_like_temperature=float(d.get("FDm", d.get("FNm"))),
            temperature=float(d.get("Dm", d.get("Nm"))),
            wind_direction=WindDirection(d["D"]),
            wind_gust=float(d.get("Gn", d.get("Gm"))),
            relative_humidity=float(d.get("Hn", d.get("Hm"))),
            visibility=Visibility(d["V"]),
            wind_speed=float(d["S"]),
            max_uv_index=int(d["U"])
            if ("U" in d.keys())
            else None,  # No UV index at night
            weather_type=SignificantWeather.from_returned_str(d["W"]),
            precipitation_probability=float(d.get("PPd", d.get("PPn"))),
            period=Period(d["$"]),
        )


@dataclass(frozen=True)
class ThreeHourlyForecastRep(BaseForecastRep):
    period: timedelta

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the dictionary returned by the DataPoint API to an instance of this class."""
        return cls(
            feels_like_temperature=float(d["F"]),
            wind_gust=float(d["G"]),
            relative_humidity=float(d["H"]),
            temperature=float(d["T"]),
            visibility=Visibility(d["V"]),
            wind_direction=WindDirection(d["D"]),
            wind_speed=float(d["S"]),
            max_uv_index=int(d["U"])
            if ("U" in d.keys())
            else None,  # No UV index at night
            weather_type=SignificantWeather.from_returned_str(d["W"]),
            precipitation_probability=float(d["Pp"]),
            period=timedelta(minutes=float(d["$"])),
        )


@dataclass(frozen=True)
class ForecastPeriod:
    type: str
    forecast_date: date
    reps: list[DailyForecastRep | ThreeHourlyForecastRep]

    @staticmethod
    def get_rep_class(
        res: Resolution | str,
    ) -> typing.Type[DailyForecastRep] | typing.Type[ThreeHourlyForecastRep]:
        """Gets the appropriate class to represent the 'Rep' objects for this type of forecast."""
        if res == Resolution.DAILY:
            return DailyForecastRep
        elif res == Resolution.THREE_HOURLY:
            return ThreeHourlyForecastRep
        else:
            raise ValueError(f"'{res}' is not a valid Resolution.")

    @classmethod
    def from_dict(
        cls, d: dict[str, str | list[dict[str, str]]], res: Resolution | str
    ) -> typing.Self:
        """Converts the dictionary returned by the DataPoint API to an instance of this class."""
        rep_cls = cls.get_rep_class(res)

        return cls(
            type=d["type"],
            forecast_date=date.fromisoformat(
                d["value"].replace("Z", "")
            ),  # date.fromisoformat doesn't like the 'Z' in the date string
            reps=[rep_cls.from_dict(r) for r in d["Rep"]]
            if isinstance(d["Rep"], list)
            else [rep_cls.from_dict(d["Rep"])],
        )


@dataclass(frozen=True)
class Forecast:
    location: ForecastLocation
    periods: list[ForecastPeriod]

    @classmethod
    def from_dict(
        cls,
        d: dict[str, str | list[dict[str, str] | list[dict[str, str]]]],
        res: Resolution | str,
    ) -> typing.Self:
        """Converts the dictionary returned by the forecast API (under ['DV']['Location']) to an instance of this class."""

        return cls(
            location=ForecastLocation.from_dict(d),
            periods=[ForecastPeriod.from_dict(p, res) for p in d["Period"]]
            if isinstance(d["Period"], list)
            else [ForecastPeriod.from_dict(d["Period"], res)],
        )

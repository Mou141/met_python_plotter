import typing, enum, functools

from dataclasses import dataclass
from datetime import date, datetime, timedelta

__all__ = [
    "Resolution",
    "SiteInfo",
    "ForecastLocation",
    "Period",
    "Visibility",
    "SignificantWeather",
    "WindDirection",
    "DailyForecastRep",
    "ThreeHourlyForecastRep",
    "ForecastPeriod",
    "Forecast",
    "ObservationRep",
    "ObservationPeriod",
    "Observation",
    "PressureTendency",
    "ExtremeType",
    "ExtremeRegion",
    "Extreme",
    "UKExtremes",
    "ExtremeUnit",
]


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
    visibility: Visibility | int
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

    @functools.cached_property
    def is_visibility(self) -> bool:
        """Returns True if self.visibility is an instance of the Visibility class."""
        return isinstance(self.visibility, Visibility)

    @functools.cached_property
    def has_uv_index(self) -> bool:
        """Returns True if self.max_uv_index is specified."""
        return self.max_uv_index is not None

    @functools.cached_property
    def weather_type_unknown(self) -> bool:
        """Returns true if the weather type is not known."""
        return self.weather_type is None


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
    reps: list[DailyForecastRep] | list[ThreeHourlyForecastRep]

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


class PressureTendency(enum.StrEnum):
    RISING = "R"
    FALLING = "F"
    STEADY = "S"


@dataclass(frozen=True)
class ObservationRep:
    temperature: typing.Optional[float]
    wind_direction: typing.Optional[WindDirection]
    wind_speed: typing.Optional[float]
    wind_gust: typing.Optional[float]
    dew_point: typing.Optional[float]
    relative_humidity: typing.Optional[float]
    weather_type: typing.Optional[SignificantWeather]
    visibility: typing.Optional[float]
    pressure: typing.Optional[float]
    pressure_tendency: typing.Optional[PressureTendency]
    period: timedelta

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            temperature=float(d["T"]) if "T" in d.keys() else None,
            wind_direction=WindDirection(d["D"]) if "D" in d.keys() else None,
            wind_speed=float(d["S"]) if "S" in d.keys() else None,
            wind_gust=float(d["G"]) if "G" in d.keys() else None,
            dew_point=float(d["Dp"]) if "Dp" in d.keys() else None,
            relative_humidity=float(d["H"]) if "H" in d.keys() else None,
            weather_type=SignificantWeather.from_returned_str(d["W"])
            if "W" in d.keys()
            else None,
            visibility=float(d["V"]) if "V" in d.keys() else None,
            pressure=float(d["P"]) if "P" in d.keys() else None,
            pressure_tendency=PressureTendency(d["Pt"]) if "Pt" in d.keys() else None,
            period=timedelta(minutes=float(d["$"])),
        )


@dataclass(frozen=True)
class ObservationPeriod:
    type: str
    observation_date: date
    reps: list[ObservationRep]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            type=d["type"],
            observation_date=date.fromisoformat(
                d["value"].replace("Z", "")
            ),  # date.fromisoformat doesn't like the 'Z' in the string
            reps=[ObservationRep.from_dict(r) for r in d["Rep"]]
            if isinstance(d["Rep"], list)
            else [ObservationRep.from_dict(d["Rep"])],
        )


@dataclass(frozen=True)
class Observation:
    location: ForecastLocation
    periods: list[ObservationPeriod]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            location=ForecastLocation.from_dict(d),
            periods=[ObservationPeriod.from_dict(p) for p in d["Period"]]
            if isinstance(d["Period"], list)
            else [ObservationPeriod.from_dict(d["Period"])],
        )


class ExtremeUnit(enum.StrEnum):
    CELSIUS = "degC"
    MILLIMETRE = "mm"
    HOURS = "hours"


class ExtremeType(enum.StrEnum):
    HIGHEST_MAX_TEMP = "HMAXT"
    LOWEST_MIN_TEMP = "LMINT"
    LOWEST_MAX_TEMP = "LMAXT"
    HIGHEST_MIN_TEMP = "HMINT"
    HIGHEST_RAINFALL = "HRAIN"
    HIGHEST_HOURS_SUN = "HSUN"

    def get_unit(self) -> ExtremeUnit:
        """Get the unit of measurement associated with this type of extreme."""
        if self in (
            self.HIGHEST_MAX_TEMP,
            self.HIGHEST_MIN_TEMP,
            self.LOWEST_MAX_TEMP,
            self.LOWEST_MAX_TEMP,
        ):
            return ExtremeUnit.CELSIUS

        elif self == self.HIGHEST_RAINFALL:
            return ExtremeUnit.MILLIMETRE

        elif self == self.HIGHEST_HOURS_SUN:
            return ExtremeUnit.HOURS

        else:
            raise ValueError(f"Type {repr(self)} does not have an associated unit.")


@dataclass(frozen=True)
class Extreme:
    location_id: str
    location_name: str
    type: ExtremeType
    unit: ExtremeUnit
    value: float

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            location_id=d["locId"],
            location_name=d["locationName"],
            type=ExtremeType(d["type"]),
            unit=ExtremeUnit(d["uom"]),
            value=float(d["$"]),
        )


@dataclass(frozen=True)
class ExtremeRegion:
    region_id: str
    region_name: str
    extremes: list[Extreme]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            region_id=d["id"],
            region_name=d["name"],
            extremes=[Extreme.from_dict(e) for e in d["Extremes"]["Extreme"]],
        )


@dataclass(frozen=True)
class UKExtremes:
    extreme_date: date
    issued_at: datetime
    regions: list[ExtremeRegion]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            extreme_date=date.fromisoformat(d["extremeDate"]),
            issued_at=datetime.fromisoformat(d["issuedAt"]),
            regions=[ExtremeRegion.from_dict(r) for r in d["Regions"]["Region"]],
        )

"""Data classes for storing data retrieved from the API."""
import enum
import functools
import typing
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

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
    "NationalParkLocation",
    "RegionalForecastLocation",
    "RegionalForecastParagraph",
    "RegionalForecastPeriodID",
    "RegionalForecastPeriod",
    "RegionalForecast",
    "MountainAreaLocation",
    "MountainForecastCapabilities",
    "HazardElement",
    "HazardLikelihood",
    "Hazard",
    "Evening",
    "SimpleDay",
    "FirstExtendedDay",
    "ExtendedDayPeriod",
    "Height",
    "ExtendedDayPeakTemperature",
    "ExtendedDayValleyTemperature",
    "SecondExtendedDay",
    "MountainAreaForecast",
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

    # Set containing enum members that represent clear weather
    _clear = enum.nonmember({CLEAR_NIGHT, SUNNY_DAY})

    # Set containing enum members that represent thunder
    _thunder = enum.nonmember(
        {
            THUNDER_SHOWER_NIGHT,
            THUNDER_SHOWER_DAY,
            THUNDER,
        }
    )
    # Set containing enum members that represent snow
    _snow = enum.nonmember(
        {
            LIGHT_SNOW_SHOWER_NIGHT,
            LIGHT_SNOW_SHOWER_DAY,
            LIGHT_SNOW,
            HEAVY_SNOW_SHOWER_NIGHT,
            HEAVY_SNOW_SHOWER_DAY,
            HEAVY_SNOW,
        }
    )

    # Set containing enum members that represent hail
    _hail = enum.nonmember(
        {
            HAIL_SHOWER_NIGHT,
            HAIL_SHOWER_DAY,
            HAIL,
        }
    )

    # Set containing enum members that represent rain
    _rain = enum.nonmember(
        {
            LIGHT_RAIN_SHOWER_NIGHT,
            LIGHT_RAIN_SHOWER_DAY,
            DRIZZLE,
            LIGHT_RAIN,
            HEAVY_RAIN_SHOWER_NIGHT,
            HEAVY_RAIN_SHOWER_DAY,
            HEAVY_RAIN,
            THUNDER_SHOWER_NIGHT,
            THUNDER_SHOWER_DAY,
        }
    )

    # Set containing members that represent sleet
    _sleet = enum.nonmember(
        {
            SLEET_SHOWER_NIGHT,
            SLEET_SHOWER_DAY,
            SLEET,
        }
    )

    # Set containing members that represent precipitation
    _precipitation = enum.nonmember(_snow | _hail | _rain | _sleet)

    def is_rain(self) -> bool:
        """Returns True if this is a rain weather type."""
        return self in self._rain

    def is_sleet(self) -> bool:
        """Returns True if this is a sleet weather type."""
        return self in self._sleet

    def is_hail(self) -> bool:
        """Returns True if this is a hail weather type."""
        return self in self._hail

    def is_snow(self) -> bool:
        """Returns True if this is a snow weather type."""
        return self in self._snow

    def is_thunder(self) -> bool:
        """Returns True if this is a thunder weather type."""
        return self in self._thunder

    def is_precipitation(self) -> bool:
        """Returns True if this is a precipitation weather type (rain, snow, etc.)"""
        return self in self._precipitation

    def is_clear(self) -> bool:
        """Returns True if this is a clear weather type."""
        return self in self._clear

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
        raise NotImplementedError

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

    _lookup = enum.nonmember(
        {
            HIGHEST_HOURS_SUN: ExtremeUnit.HOURS,
            LOWEST_MIN_TEMP: ExtremeUnit.CELSIUS,
            LOWEST_MAX_TEMP: ExtremeUnit.CELSIUS,
            HIGHEST_MIN_TEMP: ExtremeUnit.CELSIUS,
            HIGHEST_MAX_TEMP: ExtremeUnit.CELSIUS,
            HIGHEST_RAINFALL: ExtremeUnit.MILLIMETRE,
        }
    )

    def get_unit(self) -> ExtremeUnit:
        """Get the unit of measurement associated with this type of extreme."""
        if self in self._lookup.keys():
            return self._lookup[self]

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


@dataclass(frozen=True)
class NationalParkLocation:
    location_id: int
    location_name: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            location_id=int(d["id"]),
            location_name=d["name"],
        )


@dataclass(frozen=True)
class RegionalForecastLocation:
    location_id: int
    location_name: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            location_id=int(d["@id"]),
            location_name=d["@name"],
        )


@dataclass(frozen=True)
class RegionalForecastParagraph:
    title: str
    text: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            title=d["title"],
            text=d["$"],
        )


class RegionalForecastPeriodID(enum.StrEnum):
    ONE_TO_TWO = "day1to2"
    THREE_TO_FIVE = "day3to5"
    SIX_TO_FIFTEEN = "day6to15"
    SIXTEEN_TO_THIRTY = "day16to30"


@dataclass(frozen=True)
class RegionalForecastPeriod:
    id: RegionalForecastPeriodID
    paragraphs: list[RegionalForecastParagraph]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            id=RegionalForecastPeriodID(d["id"]),
            paragraphs=[RegionalForecastParagraph.from_dict(p) for p in d["Paragraph"]]
            if isinstance(d["Paragraph"], list)
            else [RegionalForecastParagraph.from_dict(d["Paragraph"])],
        )


@dataclass(frozen=True)
class RegionalForecast:
    created_on: datetime
    issued_at: datetime
    region_id: str
    periods: list[RegionalForecastPeriod]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            created_on=datetime.fromisoformat(d["createdOn"]),
            issued_at=datetime.fromisoformat(d["issuedAt"]),
            region_id=d["regionId"],
            periods=[
                RegionalForecastPeriod.from_dict(p) for p in d["FcstPeriods"]["Period"]
            ]
            if isinstance(d["FcstPeriods"]["Period"], list)
            else [RegionalForecastPeriod.from_dict(d["FcstPeriods"]["Period"])],
        )


@dataclass(frozen=True)
class MountainAreaLocation:
    location_id: str
    location_name: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            location_id=d["@id"],
            location_name=d["@name"],
        )


@dataclass(frozen=True)
class MountainForecastCapabilities:
    data_date: datetime
    valid_from: datetime
    valid_to: datetime
    created_date: datetime
    uri: str
    area: str
    risk: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            data_date=datetime.fromisoformat(d["DataDate"]),
            valid_from=datetime.fromisoformat(d["ValidFrom"]),
            valid_to=datetime.fromisoformat(d["ValidTo"]),
            created_date=datetime.fromisoformat(d["CreatedDate"]),
            uri=d["URI"],
            area=d["Area"],
            risk=d["Risk"],
        )


@dataclass(frozen=True)
class BaseHazardData:
    type: str
    value: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            type=d["Type"],
            value=d["$"],
        )


@dataclass(frozen=True)
class HazardElement(BaseHazardData):
    pass


@dataclass(frozen=True)
class HazardLikelihood(BaseHazardData):
    pass


@dataclass(frozen=True)
class Hazard:
    element: HazardElement
    likelihood: HazardLikelihood

    @classmethod
    def from_dict(cls, d: dict[str, dict[str, str]]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            element=HazardElement.from_dict(d["Element"]),
            likelihood=HazardLikelihood.from_dict(d["Likelihood"]),
        )


@dataclass(frozen=True)
class BaseDay:
    validity: datetime


@dataclass(frozen=True)
class BaseSimpleDay(BaseDay):
    summary: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            validity=datetime.fromisoformat(d["Validity"]),
            summary=d["Summary"],
        )


@dataclass(frozen=True)
class Evening(BaseSimpleDay):
    pass


@dataclass(frozen=True)
class SimpleDay(BaseSimpleDay):
    pass


@dataclass(frozen=True)
class BaseExtendedDay(BaseDay):
    weather: str
    visibility: str


@dataclass(frozen=True)
class Height:
    level: str
    wind_direction: WindDirection
    wind_speed: float
    max_gust: float
    temperature: float
    feels_like: float

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            level=d["Level"],
            wind_direction=WindDirection(d["WindDirection"]),
            wind_speed=float(d["WindSpeed"]),
            max_gust=float(d["MaxGust"]),
            temperature=float(d["Temperature"]),
            feels_like=float(d["FeelsLike"]),
        )


@dataclass(frozen=True)
class ExtendedDayPeriod:
    end: time
    start: time
    weather_type: typing.Optional[SignificantWeather]
    weather_description: str
    precipitation_probability: str
    heights: list[Height]
    freezing_level: str

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            end=time.fromisoformat(d["End"]) if d["End"] != "24:00" else time(0, 0),
            start=time.fromisoformat(d["Start"]),
            weather_type=SignificantWeather.from_returned_str(
                d["SignificantWeather"]["Code"]
            ),
            weather_description=d["SignificantWeather"]["$"],
            precipitation_probability=d["Precipitation"]["Probability"],
            heights=[Height.from_dict(h) for h in d["Height"]]
            if isinstance(d["Height"], list)
            else [Height.from_dict(d["Height"])],
            freezing_level=d["FreezingLevel"],
        )


@dataclass(frozen=True)
class FirstExtendedDay(BaseExtendedDay):
    headline: str
    confidence: str
    view: str
    cloud_free_hilltop: str
    hazards: list[Hazard]
    periods: list[Period]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            validity=datetime.fromisoformat(d["Validity"]),
            headline=d["Headline"],
            confidence=d["Confidence"],
            view=d["View"],
            cloud_free_hilltop=d["CloudFreeHillTop"],
            weather=d["Weather"],
            visibility=d["Visibility"],
            hazards=[Hazard.from_dict(h) for h in d["Hazards"]["Hazard"]]
            if isinstance(d["Hazards"]["Hazard"], list)
            else [Hazard.from_dict(d["Hazards"]["Hazard"])],
            periods=[ExtendedDayPeriod.from_dict(p) for p in d["Periods"]["Period"]]
            if isinstance(d["Periods"]["Period"], list)
            else [ExtendedDayPeriod.from_dict(d["Periods"]["Period"])],
        )


@dataclass(frozen=True)
class BaseExtendedDayTemperature:
    description: str


@dataclass(frozen=True)
class ExtendedDayPeakTemperature(BaseExtendedDayTemperature):
    level: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        cls(
            level=d["Level"],
            description=d["$"],
        )


@dataclass(frozen=True)
class ExtendedDayValleyTemperature(BaseExtendedDayTemperature):
    title: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            title=d["Title"],
            description=d["$"],
        )


@dataclass(frozen=True)
class SecondExtendedDay(BaseExtendedDay):
    wind: str
    hill_cloud: str
    peak_temperature: ExtendedDayPeakTemperature
    valley_temperature: ExtendedDayValleyTemperature
    freezing: str

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data returned from the API to an instance of this class."""
        return cls(
            validity=datetime.fromisoformat(d["Validity"]),
            weather=d["Weather"],
            wind=d["Wind"],
            hill_cloud=d["HillCloud"],
            visibility=d["Visibility"],
            peak_temperature=ExtendedDayPeakTemperature.from_dict(
                d["Temperature"]["Peak"]
            ),
            valley_temperature=ExtendedDayValleyTemperature.from_dict(
                d["Temperature"]["Valley"]
            ),
            freezing=d["Temperature"]["Freezing"],
        )


@dataclass(frozen=True)
class MountainAreaForecast:
    location: str
    issue: time
    issued: datetime
    type: str
    evening: Evening
    first_day: typing.Optional[FirstExtendedDay]
    second_day: typing.Optional[SecondExtendedDay]
    other_days: list[SimpleDay]

    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        """Converts the data from the API to an instance of this class."""
        return cls(
            location=d["Location"],
            issue=time.fromisoformat(d["Issue"]),
            issued=datetime.fromisoformat(d["Issued"]),
            type=d["Type"],
            evening=Evening.from_dict(d["Evening"]),
            first_day=FirstExtendedDay.from_dict(d["Days"]["Day"][0])
            if isinstance(d["Days"]["Day"], list) and len(d["Days"]["Day"]) >= 1
            else None,
            second_day=SecondExtendedDay.from_dict(d["Days"]["Day"][1])
            if isinstance(d["Days"]["Day"], list) and len(d["Days"]["Day"]) >= 2
            else None,
            other_days=[SimpleDay.from_dict(day) for day in d["Days"]["Day"][2:]]
            if isinstance(d["Days"]["Day"], list) and len(d["Days"]["Day"]) >= 3
            else [],
        )

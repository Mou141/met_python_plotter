"""Gets the most recent forecast for a specified location and saves it."""
from pathlib import Path
import sys, json, argparse
from datetime import datetime, date, timezone

# Add the directory containing the metdata package to the python path
_LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(_LIB_DIR))

from metdata import METDataPoint, Resolution
from metdata.dataclass_json_encoder import DataclassJSONEncoder


def parse_args() -> tuple[int, str, Resolution]:
    """Parses arguments from the command line."""

    resolution_dict = {"daily": Resolution.DAILY, "3hourly": Resolution.THREE_HOURLY}

    parser = argparse.ArgumentParser(
        description="Gets the most recent forecast for a specified location."
    )

    parser.add_argument(
        "location_id", type=int, help="The ID of the location of the forecast."
    )
    parser.add_argument("api_key", type=str, help="API key for the MET DataPoint API.")
    parser.add_argument(
        "forecast_type",
        type=str,
        choices=list(resolution_dict.keys()),
        help="The type of forecast to retrueve.",
    )

    args = parser.parse_args()

    return args.location_id, args.api_key, resolution_dict[args.forecast_type]


def main(location_id: int, api_key: str, forecast_type: Resolution):
    print(
        f"Retrieving forecast availability for location '{location_id}' at resolution '{forecast_type}'..."
    )

    m = METDataPoint(api_key)

    data_date, data_points = m.get_wxfcs_capabilities(forecast_type)
    most_recent = min(
        data_points,
        key=lambda x: abs(
            x
            - (
                datetime.now(tz=timezone.utc)
                if isinstance(x, datetime)
                else date.today()
            )
        ),
    )

    print(
        f"Most recent forecast as of {data_date.strftime('%c')}: {most_recent.strftime('%c')}."
    )

    print("Getting forecast...")
    _, forecast = m.get_forecasts(forecast_type, location_id, time=most_recent)
    print("Forecast retrieved.")

    json_forecast = json.dumps(forecast, cls=DataclassJSONEncoder, indent=4)

    print(json_forecast)

    try:
        with open("forecast.json", "w") as f:
            f.write(json_forecast)
    except (IOError, OSError) as e:
        print(f"Error while saving forecast to file: '{e}'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(*args)

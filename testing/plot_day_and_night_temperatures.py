"""Gets the daily forecast for a location and plots the maximum day and minimum night temperatures."""

import sys, argparse, requests
from pathlib import Path

import matplotlib.pyplot as plt

# Add the metdata package location to the python path
LIB_PATH = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_PATH))

from metdata import METDataPoint, Resolution, Forecast, Period
from datetime import date


def parse_args() -> tuple[str, int]:
    "Parses command line arguments."

    parser = argparse.ArgumentParser(
        description="Retrieves the minimum night and maximum day temperatures for the daily forecasts for a location and plots them on a graph.."
    )

    parser.add_argument(
        "api_key", type=str, help="API key for MET Office DataPoint API."
    )
    parser.add_argument(
        "location_id", type=int, help="Location ID of the forecast site."
    )

    args = parser.parse_args()

    return args.api_key, args.location_id


def extract_temperatures(
    forecast: Forecast,
) -> tuple[list[date], list[float], list[float]]:
    """Takes a forecast object and returns a list of forecast dates, day maximum temperatures and night minimum temperatures."""

    dates = []
    day_temps = []
    night_temps = []

    for p in forecast.periods:
        dates.append(p.forecast_date)

        day_rep = p.reps[0]
        night_rep = p.reps[1]

        assert (
            day_rep.period == Period.DAY
        ), "First rep object should contain the day data."
        assert (
            night_rep.period == Period.NIGHT
        ), "Second rep object should contain the night data."

        day_temps.append(day_rep.temperature)
        night_temps.append(night_rep.temperature)

    return dates, day_temps, night_temps


def plot_graph(
    dates: list[date], day_temps: list[float], night_temps: list[float], location: str
):
    """Plot a graph of the day and night temperatures and display it."""

    date_str = [d.isoformat() for d in dates]

    # Label axes
    plt.xlabel("Date")
    plt.ylabel("Temperature ($^\circ C$)")

    plt.title(f"Forecast Temperatures for {location}")

    plt.plot(date_str, day_temps, "ro", label="Day Maximum")
    plt.plot(date_str, night_temps, "bo", label="Night Minimum")

    plt.legend(loc="best")

    plt.show()


def main(api_key: str, location_id: int):
    m = METDataPoint(api_key)

    print(f"Retrieving forecast for location '{location_id}'...")

    try:
        data_date, forecast = m.get_forecasts(Resolution.DAILY, location_id)

    except requests.exceptions.RequestException as e:
        print(f"Error while retrieving forecast: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        print(
            f"Forecast for {forecast.location.name} ({forecast.location.country}) retrieved (last updated: {data_date.strftime('%c')})."
        )

    dates, day_temps, night_temps = extract_temperatures(forecast)

    plot_graph(
        dates,
        day_temps,
        night_temps,
        f"{forecast.location.name} ({forecast.location.country})",
    )


if __name__ == "__main__":
    args = parse_args()
    main(*args)

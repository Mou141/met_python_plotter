"""Gets the daily forecasts for a location and plots the maximum UV indices."""

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
        description="Retrieves the max UV indices from the forecasts for a location and plots them on a graph."
    )

    parser.add_argument(
        "api_key", type=str, help="API key for MET Office DataPoint API."
    )
    parser.add_argument(
        "location_id", type=int, help="Location ID of the forecast site."
    )

    args = parser.parse_args()

    return args.api_key, args.location_id


def extract_uv_indices(forecast: Forecast) -> tuple[list[date], list[int]]:
    """Takes a Forecast object and returns a list of forecast dates and a list of max UV indices forecast on those dates."""
    dates = []
    indices = []

    for p in forecast.periods:
        dates.append(p.forecast_date)

        # The daytime forecast is the first rep (the nighttime one doesn't have UV info)
        day_rep = p.reps[0]

        assert (
            day_rep.period == Period.DAY
        ), "First 'rep' object should contain the day data."

        indices.append(day_rep.max_uv_index)

    return dates, indices


def plot_graph(dates: list[date], uv_indices: list[int], location: str):
    """Plots the UV data on a graph and displays it."""

    # Label axes
    plt.xlabel("Date")
    plt.ylabel("Maximum UV Index")

    plt.title(f"UV Forecast for {location}")

    # Set appropriate y limits for UV indices
    plt.ylim(0, 12)

    # Make sure there's a major tick for every index
    plt.yticks(range(0, 13))

    plt.plot([d.isoformat() for d in dates], uv_indices, "ro")

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
        print(f"Forecast retrieved (last updated: {data_date.strftime('%c')}).")

    dates, uv_indices = extract_uv_indices(forecast)

    plot_graph(
        dates, uv_indices, f"{forecast.location.name} ({forecast.location.country})"
    )


if __name__ == "__main__":
    args = parse_args()
    main(*args)

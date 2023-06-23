"""Gets the 3hourly forecast for a location and plots the temperature in a graph."""

import argparse
import sys
from datetime import date, time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import requests

# Add the metdata package location to the python path
LIB_PATH = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_PATH))

from metdata import Forecast, METDataPoint, Resolution
from metdata.util import get_3hourly_forecast_time


def parse_args() -> tuple[str, int]:
    "Parses command line arguments."

    parser = argparse.ArgumentParser(
        description="Retrieves the forecast temperatures for a location and plots them on a graph."
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
) -> dict[date, tuple[list[time], list[float]]]:
    """Get the temperatures from the forecast and store a list of temperatures and forecast times
    in a dictionary by forecast date."""
    out = {}

    for p in forecast.periods:
        times = []
        temps = []

        for r in p.reps:
            # Get the time on the forecast day that these forecasts are for
            times.append(get_3hourly_forecast_time(p.forecast_date, r.period))
            temps.append(r.temperature)

        out[p.forecast_date] = (times, temps)

    return out


def get_axes(num: int) -> tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes]]:
    """Get subplots to plot the data on."""
    fig, ax = plt.subplots(ncols=num, sharey=True)

    # plt.subplots returns only one matplotlib.axes.Axes object when num == 1
    # In which case, it needs to be wrapped in a list so that it's still subscriptable
    if num == 1:
        ax = [ax]

    return fig, ax


def plot_graph(temp_dict: dict[date, tuple[list[time], list[float]]], location: str):
    """Plot the temperature graphs on a set of subplots (one for each day that forecasts are available for)."""

    # Extract the keys from the dictionary into a list
    dates = list(temp_dict.keys())

    # Make sure they're in order (since dict doesn't preserve order)
    dates.sort()

    fig, axes = get_axes(len(dates))

    fig.suptitle(f"Forecast Temperatures for {location}")

    # Rotate x-axis labels so that they're horizontal
    # Also centre labels relative to tick marks
    fig.autofmt_xdate(rotation=90, ha="center")

    # y-axis is shared so only need to label one
    axes[0].set(ylabel="Temperature ($^\circ C$)")

    # Put tick labels on the right side of the last subplot too
    axes[-1].tick_params(labelright=True)

    for d, a in zip(dates, axes):
        times, temps = temp_dict[d]

        assert len(times) == len(
            temps
        ), f"Error: number of time values ({len(times)}) not equal to number of temperature values ({len(temps)})."

        a.set_title(d.isoformat())

        a.plot([t.strftime("%H:%M") for t in times], temps, "ro")

        # If more than 3 labels on axis,
        # Skip every other label so that they fit better
        if len(times) > 3:
            plt.setp(a.get_xticklabels()[1::2], visible=False)

        # Set wider margins so that plot points don't overlap edge
        a.margins(x=0.2)

        # Put ticks on the right side of each subplot as well
        a.tick_params(right=True)

    plt.show()


def main(api_key: str, location_id: int):
    m = METDataPoint(api_key)

    print(f"Retrieving forecast for location '{location_id}'...")

    try:
        data_date, forecast = m.get_forecasts(Resolution.THREE_HOURLY, location_id)

    except requests.exceptions.RequestException as e:
        print(f"Error while retrieving forecast: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        # Forecast list should contain only one Forecast object, so extract it
        forecast = forecast[0]

        print(
            f"Forecast for {forecast.location.name} ({forecast.location.country}) retrieved (last updated: {data_date.strftime('%c')})."
        )

    temp_dict = extract_temperatures(forecast)

    plot_graph(temp_dict, f"{forecast.location.name} ({forecast.location.country})")


if __name__ == "__main__":
    args = parse_args()
    main(*args)

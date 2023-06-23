"""Find the closest forecast or observation site to a specified latitude and longitude."""
import argparse
import sys
from pathlib import Path

import requests

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata import METDataPoint
from metdata.util import get_closest


def parse_args() -> tuple[str, float, float, str]:
    """Parses command line arguments."""

    parser = argparse.ArgumentParser(
        description="Gets the details of the forecast site closest to the specified coordinates."
    )

    parser.add_argument(
        "api_key", type=str, help="API Key for MET Office DataPoint API."
    )
    parser.add_argument("latitude", type=float, help="Latitude of location.")
    parser.add_argument("longitude", type=float, help="Longitude of location.")

    parser.add_argument(
        "--type",
        "-t",
        choices=["forecast", "observation"],
        default="forecast",
        help="Type of site to find.",
    )

    args = parser.parse_args()

    return args.api_key, args.latitude, args.longitude, args.type


def main(api_key: str, latitude: float, longitude: float, site_type: str):
    m = METDataPoint(api_key)

    print("Getting list of sites...")

    try:
        if site_type == "forecast":
            sites = m.get_wxfcs_site_list()

        elif site_type == "observation":
            sites = m.get_wxobs_site_list()

        else:
            print(f"Error: '{site_type}' is not a valid type of site.", file=sys.stderr)
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error while attempting to retrieve data: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        print("List retrieved.")

    closest = get_closest(sites, latitude, longitude)

    print(f"Closest site to ({latitude}, {longitude}): {closest}")


if __name__ == "__main__":
    args = parse_args()
    main(*args)

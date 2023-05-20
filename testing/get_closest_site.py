"""Find the closest forecast site to a specified latitude and longitude."""
import sys, argparse

from pathlib import Path

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata import METDataPoint
from metdata.util import get_closest

def parse_args() -> tuple[str, float, float]:
    """Parses command line arguments."""
    
    parser = argparse.ArgumentParser(description="Gets the details of the forecast site closest to the specified coordinates.")

    parser.add_argument("api_key", type=str, help="API Key for MET Office DataPoint API.")
    parser.add_argument("latitude", type=float, help="Latitude of location.")
    parser.add_argument("longitude", type=float, help="Longitude of location.")

    args = parser.parse_args()

    return args.api_key, args.latitude, args.longitude


def main(api_key: str, latitude: float, longitude: float):
    m = METDataPoint(api_key)

    print("Getting list of sites...")
    sites = m.get_wxfcs_site_list()
    print("List retrieved.")

    closest = get_closest(sites, latitude, longitude)

    print(f"Closest site to ({latitude}, {longitude}): {closest}")

if __name__ == "__main__":
    args = parse_args()
    main(*args)
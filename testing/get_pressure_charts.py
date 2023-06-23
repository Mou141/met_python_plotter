"""Gets all pressure charts and saves them to file."""
import argparse
import sys
from pathlib import Path

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata.metdatapointimages import ImageMETDataPoint


def parse_args():
    parser = argparse.ArgumentParser(
        description="Downloads all available surface pressure charts."
    )

    parser.add_argument(
        "api_key", type=str, help="API key for MET Office DataPoint API."
    )

    args = parser.parse_args()

    return (args.api_key,)


def main(key):
    m = ImageMETDataPoint(key)

    print("Getting pressure charts...")

    try:
        for t, img in m.get_all_surface_pressure_charts():
            fname = f"pressure_at_{t}.gif"
            print(f"Saving to '{fname}'...")

            img.save(fname, format="GIF")

    except (ValueError, OSError) as e:
        print(f"Error while retrieving pressure charts: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        print("All pressure charts saved.")


if __name__ == "__main__":
    args = parse_args()
    main(*args)

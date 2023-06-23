"""Downloads the pressure charts and then saves them as an animated GIF."""
import argparse
import sys
import typing
from pathlib import Path

import requests

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata.metdatapointimages import ImageMETDataPoint, save_animated_gif


def parse_args():
    parser = argparse.ArgumentParser(
        description="Downloads all available surface pressure charts and saves them as an animated GIF."
    )

    parser.add_argument("api_key", type=str, help="The MET DataPoint API key.")
    parser.add_argument("out_file", type=Path, help="File to save the GIF to.")

    args = parser.parse_args()

    return args.api_key, args.out_file


def main(api_key: str, out_file: Path | str | typing.BinaryIO):
    m = ImageMETDataPoint(api_key)

    try:
        print("Retrieving pressure charts...")
        images = [
            i[1]
            for i in sorted(m.get_all_surface_pressure_charts(), key=lambda x: x[0])
        ]

    except (requests.RequestException, ValueError) as e:
        print(f"Error while retrieving pressure charts: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        print("All pressure charts retrieved.")

    try:
        print("Saving animated GIF...")
        save_animated_gif(out_file, images)

    except (OSError, ValueError) as e:
        print(f"Error while saving GIF: '{e}'", file=sys.stderr)
        sys.exit(1)

    else:
        print("GIF saved.")


if __name__ == "__main__":
    args = parse_args()
    main(*args)

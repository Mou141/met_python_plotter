"""Lists all available layers of the specified type."""
import sys, argparse, requests

from pathlib import Path

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata.metdatapointimages import ImageMETDataPoint


def parse_args():
    parser = argparse.ArgumentParser(
        description="Lists all available layer names of the specified type."
    )

    parser.add_argument("api_key", type=str, help="Key for the MET DataPoint APU.")
    parser.add_argument(
        "layer_type",
        type=str,
        choices=("observation", "forecast"),
        help="Type of layer to list.",
    )

    args = parser.parse_args()

    return (args.api_key, args.layer_type)


def main(api_key: str, layer_type: str):
    m = ImageMETDataPoint(api_key)

    if layer_type == "observation":
        fetch_func = m.get_observation_layer_capabilities_as_dict

    elif layer_type == "forecast":
        fetch_func = m.get_forecast_layer_capabilities_as_dict

    else:
        print(
            f"'{layer_type}' is not a valid layer type (can be either 'observation' or 'forecast').",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        for layer_name in fetch_func().keys():
            print(layer_name)

    except (ValueError, requests.RequestException) as e:
        print(f"Error while attempting to retrieve layer names: '{e}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(*args)

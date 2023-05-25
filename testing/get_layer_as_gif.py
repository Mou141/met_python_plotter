"""Gets all available layer images of the specified type and saves them as an animated GIF."""
import sys, argparse, typing, requests

from pathlib import Path

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata.metdatapointimages import ImageMETDataPoint, save_animated_gif


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gets the specified forecast or observation layer at all available times and saves it as an animated GIF."
    )

    parser.add_argument("api_key", type=str, help="The MET DataPoint API key.")
    parser.add_argument(
        "layer_type",
        type=str,
        choices=("observation", "forecast"),
        help="The type of layer to retrieve.",
    )
    parser.add_argument(
        "layer_name", type=str, help="The name of the layer to retrieve."
    )
    parser.add_argument("out_file", type=Path, help="The file name to save the GIF to.")

    args = parser.parse_args()

    return args.api_key, args.layer_type, args.layer_name, args.out_file


def main(
    api_key: str,
    layer_type: str,
    layer_name: str,
    out_file: Path | str | typing.BinaryIO,
):
    m = ImageMETDataPoint(api_key)

    print("Attempting to retrieve images...")

    if layer_type == "observation":
        fetch_func = m.get_all_observation_layers_of_type

    elif layer_type == "forecast":
        fetch_func = m.get_all_forecast_layers_of_type

    else:
        print(
            f"Layer Type '{layer_type}' is not recoginised. Must be either 'observation' or 'forecast'.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        print(f"Retrieving images of {layer_type} layer '{layer_name}'...")
        images = [i[1] for i in sorted(fetch_func(layer_name), key=lambda x: x[0])]

    except (ValueError, OSError, requests.RequestException) as e:
        print(
            f"Error while attempting to retrieve layer images: '{e}'", file=sys.stderr
        )
        sys.exit(1)

    else:
        print("Images retrueved successfully.")

    try:
        print("Saving as GIF...")
        save_animated_gif(out_file, images, duration=500)

    except (ValueError, OSError) as e:
        print(f"Error while attempting to save GIF: '{e}'", file=sys.stderr)

    else:
        pass


if __name__ == "__main__":
    args = parse_args()
    main(*args)

"""Gets the specified observation layer at all available timesteps."""
import sys, argparse

from pathlib import Path

# Add metdata package to the python path
LIB_DIR = Path(__file__).parent.parent.resolve()
sys.path.append(str(LIB_DIR))

from metdata.metdatapointimages import ImageMETDataPoint


def parse_args():
    parser = argparse.ArgumentParser(
        description="Downloads the specified observation layer at all available timesteps."
    )

    parser.add_argument(
        "api_key", type=str, help="API key for MET Office DataPoint API."
    )
    parser.add_argument("layer_name", type=str, help="Name of the layer to retrieve.")

    args = parser.parse_args()

    return args.api_key, args.layer_name


def main(api_key: str, layer_name: str):
    m = ImageMETDataPoint(api_key)

    print(f"Retrieving images of layer '{layer_name}'...")

    try:
        for t, img in m.get_all_observation_layers_of_type(layer_name):
            fname = f"{layer_name}_({t.strftime('%d.%m.%Y_%H.%M.%S')}).png"

            print(f"Saving to '{fname}...")
            img.save(fname, format="PNG")

    except (OSError, ValueError) as e:
        print(
            f"Error while retrieving observation layer images: '{e}'", file=sys.stderr
        )
        sys.exit(1)

    else:
        print("All images retrieved.")


if __name__ == "__main__":
    args = parse_args()
    main(*args)

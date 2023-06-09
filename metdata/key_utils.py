"""Utility functions for loading an API key from file and saving it to file."""
import json
import typing
from pathlib import Path

from .metdatapoint import METDataPoint

__all__ = [
    "from_txt_file",
    "to_txt_file",
    "from_json_file",
    "to_json_file",
    "from_file",
]


def from_txt_file(path: Path | str, encoding: typing.Optional[str] = None) -> str:
    """Loads an API key from a text file which contains only the key and whitespace.
    This function opens the file in text mode and will read at most 200 characters.
    An encoding can optionally be specified with the encoding parameter."""

    with open(path, "r", encoding=encoding) as f:
        return f.read(200).strip()


def to_txt_file(
    path: Path | str, api_key: str | METDataPoint, encoding: typing.Optional[str] = None
) -> None:
    """Writes an API key to the specified file as a single line.
    api_key can be a string containing the key or a METDataPoint instance.
    An encoding can optionally be specified with the encoding parameter."""

    if isinstance(api_key, METDataPoint):
        api_key = api_key.key

    with open(path, "w", encoding=encoding) as f:
        print(api_key, file=f)


def from_json_file(
    path: Path | str, json_args: typing.Optional[dict[str, typing.Any]] = {}
) -> str:
    """Loads an API key from a json formatted text file (in utf-8 encoding).
    It assumes that the file contains a dictionary with the key stored under 'met_api_key'.
    All other entries will be ignored and if a dictionary is not returned a ValueError will be raised.
    Specify any keyword arguments for the json.load function by specifying a dictionary as the json_args parameter.
    """

    with open(path, "r", encoding="utf-8") as f:
        j = json.load(f, **json_args)

    if not isinstance(j, dict):
        raise ValueError(
            f"JSON file '{str(path)}' does not contain a dictionary (returned object was of type {str(type(j))})."
        )

    elif not "met_api_key" in j.keys():
        raise ValueError(f"JSON file '{str(path)}' does not contain an API key.")

    else:
        key = j["met_api_key"]

        if not isinstance(key, str):
            raise (
                f"JSON file '{str(path)}' did not contain a string for the 'met_api_key' entry (entry eas of type {str(type(key))})."
            )

        else:
            return key


def to_json_file(
    path: Path | str,
    api_key: str | METDataPoint,
    json_args: typing.Optional[dict[str, typing.Any]] = {},
) -> None:
    """Saves an API key to a json formatted text file (in utf-8 encoding).
    The API will be saved as a dictionary with a singly entry: {'met_api_key': api_key}.
    api_key can be a string containing the key or a METDataPoint instance.
    Specify any keyword arguments for the json.dump function by specifying a dictionary as the json_args parameter.
    """

    if isinstance(api_key, METDataPoint):
        api_key = api_key.key

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"met_api_key": api_key}, f, **json_args)


# Functions to load key from file
_LOADERS = {".txt": from_txt_file, ".json": from_json_file}


def from_file(
    path: Path | str,
    loaders: typing.Optional[dict[str, typing.Callable[[Path | str], str]]] = _LOADERS,
    cls: typing.Type[METDataPoint] = METDataPoint,
) -> METDataPoint:
    """Loads an API key from a file using an appropriate function based on the extension of the file,
    and then uses it to instantiate an object for accessing the MET DataPoint API.
    Default loaders are provided for '.txt' and '.json'.
    The loaders can be changed by passing a dictionary mapping file extensions to callables to the loaders parameter.
    Each callable should take the file path as a parameter and return the API key.
    By default an instance of METDataPoint is returned but a different class (which accepts a key= keyword parameter)
    can be substituted by passing a class as this function's cls parameter.
    """

    ext = Path(path).suffix.lower()

    if ext in loaders.keys():
        return cls(key=loaders[ext](path))

    else:
        raise ValueError(
            f"No loader available which can load a key from a file of extension '{ext}'."
        )

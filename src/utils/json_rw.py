"""This module provides json loading and writing helpers."""

from typing import Dict, Any
import json


def load(filepath: str) -> str:
    """Loads a json file into a dictionnary."""
    with open(filepath, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def write(json_dict: Dict[str, Any],
          filename: str
          ) -> None:
    """Writes a dictionnary in a file."""
    with open(filename, 'w') as file:
        json.dump(json_dict, file)

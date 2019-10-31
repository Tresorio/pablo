"""This module provides json loading and writing helpers."""

import json


def load(filepath: str):
    """Loads a json file into a dictionnary."""

    with open(filepath, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return ''


def write(json_dict: dict, filename: str):
    """Writes a dictionnary in a file."""

    with open(filename, 'w') as file:
        json.dump(json_dict, file)
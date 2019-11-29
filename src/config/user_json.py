"""This module handles the getting and setting of the user config"""

from typing import Dict, Any

import src.utils.json_rw as json
from src.config import paths


def _get_user_config() -> Dict[str, Any]:
    """Convert the user json config into a dictionnary"""
    template_user_json = json.load(paths.DEFAULT_USER_CONFIG_PATH)
    try:
        user_json = json.load(paths.USER_CONFIG_PATH)
    except FileNotFoundError:
        return template_user_json

    for key in template_user_json:
        try:
            user_json[key]
        except KeyError:
            user_json[key] = template_user_json[key]
    return user_json


if 'USER_CONFIG' not in globals():
    USER_CONFIG = _get_user_config()


def set_user_config() -> None:
    """Write the user config json file"""
    try:
        json.write(USER_CONFIG, paths.USER_CONFIG_PATH)
    except OSError as err:
        print(err)

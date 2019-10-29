from typing import Dict, Any
import src.config.paths as paths
import src.utils.json_rw as json


def _get_user_config() -> Dict[str, Any]:
    """Converts the user json config into a dictionnary"""
    try:
        user_json = json.load(paths.USER_CONFIG_PATH)
    except FileNotFoundError:
        return json.load(paths.DEFAULT_USER_CONFIG_PATH)
    return user_json


USER_CONFIG = _get_user_config()


def set_user_config() -> None:
    try:
        json.write(USER_CONFIG, paths.USER_CONFIG_PATH)
    except OSError as err:
        print(err)

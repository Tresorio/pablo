"""This module loads the configurations related to the Tresorio API's"""

import src.utils.json_rw as json
from . import paths

API_CONFIG = json.load(paths.TRESORIO_CONFIG_PATH)

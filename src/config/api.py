"""This module loads the configurations related to the Tresorio API"""

import ssl

from bundle_modules import certifi
from src.config import paths
import src.utils.json_rw as json

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.load_verify_locations(certifi.where())

IS_MOCKED = False
API_CONFIG = json.load(paths.TRESORIO_CONFIG_PATH)

MODE = "prod"

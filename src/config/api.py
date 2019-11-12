"""This module loads the configurations related to the Tresorio API"""

import src.utils.json_rw as json
import src.config.paths as paths
import ssl
from bundle_modules import certifi

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.load_verify_locations(certifi.where())

IS_MOCKED = False
API_CONFIG = json.load(paths.TRESORIO_CONFIG_PATH)

MODE = "dev"
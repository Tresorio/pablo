"""This module provides all the paths used for configuration"""

import os
import bpy

# Finds the absolute path to the addon's directory. If you move `paths.py
# to another folder, make sure the os.path.dirname chaining still leads
# to the addon's folder.
ABS_ADDON_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Absolute path to the 'config/lang' folder
LANG_PATH = os.path.join(ABS_ADDON_PATH, 'config', 'lang')

# Paths leading to addon / local user configs
TRESORIO_LOCAL_CONFIG_PATH = os.path.join(ABS_ADDON_PATH, 'config', 'tresorio')
TRESORIO_CONFIG_PATH = os.path.join(TRESORIO_LOCAL_CONFIG_PATH, 'config.json')
DEFAULT_USER_CONFIG_PATH = os.path.join(TRESORIO_LOCAL_CONFIG_PATH, 'user.json')

ICONS_PATH = os.path.join(ABS_ADDON_PATH, 'assets', 'icons')

USER_CONFIG_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), 'user.json')
LOGS_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), 'logs.txt')

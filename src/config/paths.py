"""This module provides all the paths used for configuration"""

import os
import bpy

# TODO split the end only
DIRNAME = os.path.dirname(__file__).split(os.path.join('src', 'config'))[0]
CONFIG_JSONS_DIRNAME = 'config'
ASSETS_DIRNAME = 'assets'

LANG_PATH = os.path.join(DIRNAME, CONFIG_JSONS_DIRNAME, 'lang')
LANG_DESCRIPTION_PATH = os.path.join(LANG_PATH, 'description.json')
LANG_FIELD_PATH = os.path.join(LANG_PATH, 'field.json')
LANG_NOTIFICATION_PATH = os.path.join(LANG_PATH, 'notification.json')

TRESORIO_ADDON_PATH = os.path.join(DIRNAME, CONFIG_JSONS_DIRNAME, 'tresorio')
TRESORIO_CONFIG_PATH = os.path.join(TRESORIO_ADDON_PATH, 'config.json')
DEFAULT_USER_CONFIG_PATH = os.path.join(TRESORIO_ADDON_PATH, 'user.json')

ICONS_PATH = os.path.join(DIRNAME, ASSETS_DIRNAME, 'icons')

USER_CONFIG_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), 'user.json')
LOGS_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), "logs.txt")

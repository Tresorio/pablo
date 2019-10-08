"""This module provides all the paths used for configuration"""

import os
import bpy

DIRNAME = os.path.dirname(__file__).split('src/config')[0]
CONFIG_JSONS_DIRNAME = 'config'
ASSETS_DIRNAME = 'assets'

LANG_PATH = os.path.join(DIRNAME, CONFIG_JSONS_DIRNAME, 'lang')
LANG_DESCRIPTION_PATH = os.path.join(LANG_PATH, 'description.json')
LANG_FIELD_PATH = os.path.join(LANG_PATH, 'field.json')
LANG_NOTIFICATION_PATH = os.path.join(LANG_PATH, 'notification.json')

TRESORIO_ADDON_PATH = os.path.join(DIRNAME, CONFIG_JSONS_DIRNAME, 'tresorio')
TRESORIO_CONFIG_PATH = os.path.join(TRESORIO_ADDON_PATH, 'config.json')

ICONS_PATH = os.path.join(DIRNAME, ASSETS_DIRNAME, 'icons')

EMAIL_CONFIG_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), "email.json")
LANG_CONFIG_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), 'lang.json')
LOGS_PATH = os.path.join(bpy.utils.user_resource(
    'CONFIG', path='tresorio', create=True), "logs.txt")

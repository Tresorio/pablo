"""This modules handles the registration / liberation of Tresorio's icons"""

import os
import bpy.utils.previews
from src.config.paths import ICONS_PATH

ICONS_DICT = None


# pylint: disable=global-statement

class TresorioIconsLoader:
    """Icons loader"""

    @staticmethod
    def icon(icon_name: str
             ) -> int:
        """Custom icon getter"""
        return ICONS_DICT[icon_name].icon_id

    @staticmethod
    def load(icon_filename: str
             ) -> None:
        """Load a new icon"""
        icon_name = os.path.splitext(icon_filename)[0].upper()
        bl_icon_name = f'TRESORIO_{icon_name}'
        icon_path = os.path.join(ICONS_PATH, icon_filename)
        ICONS_DICT.load(bl_icon_name, icon_path, 'IMAGE')

    @classmethod
    def register(cls):
        """Load the icons in the icons dict"""
        global ICONS_DICT
        ICONS_DICT = bpy.utils.previews.new()
        for icon_filename in os.listdir(ICONS_PATH):
            cls.load(icon_filename)

    @staticmethod
    def unregister():
        """Remove the icon dict from memory"""
        global ICONS_DICT
        ICONS_DICT.close()
        del ICONS_DICT

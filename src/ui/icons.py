import os
import bpy.utils.previews
from src.config.paths import ICONS_PATH


class TresorioIconsLoader:

    icons_dict = None

    @classmethod
    def icon(cls, icon_name):
        return cls.icons_dict[icon_name].icon_id

    @classmethod
    def register(cls):
        cls.icons_dict = bpy.utils.previews.new()
        for icon_filename in os.listdir(ICONS_PATH):
            cls.load(icon_filename)

    @classmethod
    def load(cls, icon_filename):
        no_ext = os.path.splitext(icon_filename)[0].upper()
        icon_name = f'TRESORIO_{no_ext}'
        icon_path = os.path.join(ICONS_PATH, icon_filename)
        cls.icons_dict.load(icon_name, icon_path, 'IMAGE')

    @classmethod
    def unregister(cls):
        if cls.icons_dict is not None:
            bpy.utils.previews.remove(cls.icons_dict)

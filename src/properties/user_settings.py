"""This module defines the user settings properties"""

import bpy
from src.config.user_json import USER_CONFIG
from src.config.langs import TRADUCTOR, CONFIG_LANG


def update_open_image_on_download(ptr: 'TresorioUserSettingsProps',
                                  context: bpy.types.Context
                                  ) -> None:
    """Update the user config for the open_image_on_download option"""
    del context
    USER_CONFIG['open_image_on_download'] = ptr.open_image_on_download


class TresorioUserSettingsProps(bpy.types.PropertyGroup):
    """User settings properties"""
    download_when_over: bpy.props.BoolProperty(
        name='',
        description='',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    download_when_over_path: bpy.props.StringProperty(
        name='',
        description='',
        default='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['open_image_on_download'][CONFIG_LANG]
    open_image_on_download: bpy.props.BoolProperty(
        name='',
        default=USER_CONFIG['open_image_on_download'],
        description=desc,
        options={'HIDDEN', 'SKIP_SAVE'},
        update=update_open_image_on_download,
    )

    desc = TRADUCTOR['desc']['show_selected_render'][CONFIG_LANG]
    show_selected_render: bpy.props.BoolProperty(
        name='',
        description=desc,
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_user_settings_props = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_user_settings_props',
            options={'HIDDEN', 'SKIP_SAVE'},
        )

    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_user_settings_props

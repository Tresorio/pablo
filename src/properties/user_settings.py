import bpy
from src.config.user_json import USER_CONFIG
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS


class TresorioUserProps(bpy.types.PropertyGroup):

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
        del bpy.types.WindowManager.tresorio_user_settings_props

import bpy
from src.config.user_json import USER_CONFIG
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS


def update_open_image_on_download(ptr, ctx):
    USER_CONFIG['open_image_on_download'] = ptr.open_image_on_download


def select_all(ptr, context):
    pass


class TresorioUserSettingsProps(bpy.types.PropertyGroup):

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

    desc = TRADUCTOR['desc']['select_all_renders'][CONFIG_LANG]
    select_all_renders: bpy.props.BoolProperty(
        name='',
        default=False,
        description=desc,
        options={'HIDDEN', 'SKIP_SAVE'},
        update=select_all,
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

import bpy
import json
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty
from src.config import lang_desc as ld, all_langs
from src.login.save_login import login_from_conf
from .password_tools import switch_password_visibility
from src.config import set_new_lang
from src.config import config_lang


class TresorioSettings(bpy.types.PropertyGroup):
    bl_idname = "tresorio.settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def register(TresorioSettings):
        prelogged_in, mail = login_from_conf()

        TresorioSettings.is_logged = BoolProperty(
            name="",
            default=prelogged_in,
            options={'HIDDEN', 'SKIP_SAVE'}
        )

        TresorioSettings.langs = EnumProperty(
            name="",
            items=(all_langs["eng"], all_langs["fr"]),
            update=set_new_lang,
            default=all_langs[config_lang][0],
        )

        desc = ld["mail"][config_lang]
        TresorioSettings.mail = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            options={'HIDDEN', 'SKIP_SAVE'},
            default=mail,
        )

        desc = ld["password"][config_lang]
        TresorioSettings.hidden_password = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            default="",
            options={'HIDDEN', 'SKIP_SAVE'},
            subtype="PASSWORD",
        )

        desc = ld["password"][config_lang]
        TresorioSettings.clear_password = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            default="",
            options={'HIDDEN', 'SKIP_SAVE'},
            subtype="NONE",
        )

        desc = ld["toggle_password"][config_lang]
        TresorioSettings.show_password = BoolProperty(
            name="",
            description=desc,
            default=False,
            update=switch_password_visibility,
            options={'SKIP_SAVE'}
        )

        desc = ld["stay_connected"][config_lang]
        TresorioSettings.stay_connected = BoolProperty(
            name="",
            description=desc,
            default=prelogged_in,
        )

        bpy.types.Scene.tresorio_settings = PointerProperty(
            type=TresorioSettings, name="tresorio_settings")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.tresorio_settings

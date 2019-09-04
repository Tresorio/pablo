import bpy
import json
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty
from src.config import lang_desc
from src.login.save_login import login_from_conf
from .password_tools import switch_password_visibility
from .lang_tools import get_default_lang


class TresorioSettings(bpy.types.PropertyGroup):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def register(TresorioSettings):
        prelogged_in = login_from_conf()
        default_lang = get_default_lang()

        TresorioSettings.is_logged = BoolProperty(
            name="",
            default=prelogged_in,
        )

        TresorioSettings.langs = EnumProperty(
            name="",
            items=(("eng", "English", "English language"),),
        )

        TresorioSettings.curr_lang = StringProperty(
            name="",
            default=default_lang
        )

        desc = lang_desc["mail"][default_lang]
        TresorioSettings.mail = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            default="",
        )

        desc = lang_desc["password"][default_lang]
        TresorioSettings.hidden_password = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            default="",
            subtype="PASSWORD",
        )

        desc = lang_desc["password"][default_lang]
        TresorioSettings.clear_password = StringProperty(
            name="",
            description=desc,
            maxlen=128,
            default="",
            subtype="NONE",
        )

        desc = lang_desc["toggle_password"][default_lang]
        TresorioSettings.show_password = BoolProperty(
            name="",
            description=desc,
            default=False,
            update=switch_password_visibility,
        )

        desc = lang_desc["stay_connected"][default_lang]
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

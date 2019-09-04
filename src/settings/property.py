import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty
import json
from src.login.save_login import login_from_conf
from .password_tools import switch_password_visibility


class TresorioSettings(bpy.types.PropertyGroup):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def register(TresorioSettings):
        prelogged_in = login_from_conf()

        TresorioSettings.is_logged = BoolProperty(
            name="",
            default=prelogged_in,
        )

        TresorioSettings.mail = StringProperty(
            name="",
            description="Tresorio account mail",
            maxlen=128,
            default=""
        )

        TresorioSettings.hidden_password = StringProperty(
            name="",
            description="Tresorio account password",
            maxlen=128,
            default="",
            subtype="PASSWORD",
        )

        TresorioSettings.clear_password = StringProperty(
            name="",
            description="Tresorio account password",
            maxlen=128,
            default="",
            subtype="NONE",
        )

        TresorioSettings.show_password = BoolProperty(
            name="",
            description="Reveal or hide the password",
            default=False,
            update=switch_password_visibility,
        )

        TresorioSettings.stay_connected = BoolProperty(
            name="",
            description="Connect automatically at the next login",
            default=prelogged_in,
        )

        bpy.types.Scene.tresorio_settings = PointerProperty(
            type=TresorioSettings, name="tresorio_settings")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.tresorio_settings

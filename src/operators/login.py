import bpy
import asyncio
import requests
import urllib.parse as url
from src.services import async_loop
from src.config.api import API_CONFIG
from src.services.backend import TresorioBackend
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.utils.password import reset_password, get_password
from src.utils.email import set_email_in_conf, remove_email_from_conf


class TresorioLoginOperator(bpy.types.Operator):
    bl_idname = 'tresorio.login'
    bl_label = 'Login'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_login'][CONFIG_LANG]

    def execute(self, context):
        user_props = context.window_manager.tresorio_user_props
        email, password = user_props.email, get_password(user_props)
        context.window_manager.tresorio_user_props.hidden_password = reset_password(
            len(password))
        context.window_manager.tresorio_user_props.clear_password = reset_password(
            len(password))

        if user_props.is_logged == True:
            self.report({'INFO'},
                        TRADUCTOR['notif']['already_logged_in'][CONFIG_LANG])
            return {'CANCELLED'}
        if email == '' and password == '':
            self.report({'ERROR'},
                        TRADUCTOR['notif']['no_mail_password'][CONFIG_LANG])
            return {'CANCELLED'}
        if email == '':
            self.report({'INFO'},
                        TRADUCTOR['notif']['no_mail'][CONFIG_LANG])
            return {'CANCELLED'}
        if password == '':
            self.report({'INFO'},
                        TRADUCTOR['notif']['no_password'][CONFIG_LANG])
            return {'CANCELLED'}

        TresorioBackend.connect_to_tresorio(email, password)

        # TODO redraw panel once connected to update it

        return {'FINISHED'}

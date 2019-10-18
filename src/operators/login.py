import bpy
import asyncio
import requests
import urllib.parse as url
from src.ui.popup import popup
from src.services import async_loop
from src.config.api import API_CONFIG
from src.config.user_json import USER_CONFIG
from src.services.backend import connect_to_tresorio
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.utils.password import reset_password, get_password


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
            popup(TRADUCTOR['notif']['already_logged_in'][CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}
        if email == '' and password == '':
            popup(TRADUCTOR['notif']['no_mail_password'][CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}
        if email == '':
            popup(TRADUCTOR['notif']['no_mail'][CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}
        if password == '':
            popup(TRADUCTOR['notif']['no_password'][CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        if user_props.remember_email is True:
            USER_CONFIG['email'] = email
        else:
            USER_CONFIG['email'] = ''

        connect_to_tresorio(email, password)

        return {'FINISHED'}

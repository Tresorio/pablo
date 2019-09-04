import bpy
import requests
import urllib.parse as url

from src.settings.password_tools import get_password
from src.config import tresorio_config as tc, lang_notif as ln
from .save_login import save_login_infos, remove_login_infos


class TresorioLogin(bpy.types.Operator):
    """Login to Tresorio"""
    bl_idname = 'tresorio.login'
    bl_label = 'Login'

    def execute(self, context):
        settings = context.scene.tresorio_settings
        lang = settings.curr_lang
        mail, password = settings.mail, get_password(settings)
        context.scene.tresorio_settings.hidden_password = ""
        context.scene.tresorio_settings.clear_password = ""

        if settings.is_logged == True:
            self.report({'INFO'}, ln["already_logged_in"][lang])
            return {'CANCELLED'}
        if mail == "" and password == "":
            self.report({'ERROR'}, ln["no_mail_password"][lang])
            return {'CANCELLED'}
        if mail == "":
            self.report({'INFO'}, ln["no_mail"][lang])
            return {'CANCELLED'}
        if password == "":
            self.report({'INFO'}, ln["no_password"][lang])
            return {'CANCELLED'}

        body = {
            "email": mail,
            "password": password,
        }

        try:
            signin_url = url.urljoin(tc['backend'], tc['routes']['signin'])
            r = requests.post(signin_url, data=body)
            auth_res = r.json()
        except Exception as e:
            print(e)
            self.report(
                {'ERROR'}, "Internal error when trying to log in, please retry")
            return {'CANCELLED'}

        if "token" not in auth_res:
            self.report({'WARNING'}, "Invalid email or password")
            return {'CANCELLED'}

        if settings.stay_connected == True:
            save_login_infos(mail, auth_res['token'], context)
        elif settings.stay_connected == False:
            remove_login_infos()

        context.scene.tresorio_settings.is_logged = True
        self.report({'INFO'}, "Successfully logged in")
        return {'FINISHED'}

import bpy
import requests
import urllib.parse as url
from src.settings.password_tools import get_password
from src.config import (tresorio_config as tc, 
                        lang_notif as ln, 
                        lang_desc as ld,
                        config_lang)
from .save_login import save_login_infos, remove_login_infos


def reset_password(n):
    import string
    from random import SystemRandom
    lock = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
    lock = ""
    return lock

class TresorioLogin(bpy.types.Operator):
    bl_idname = 'tresorio.login'
    bl_label = 'Login'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = ld['tresorio_login'][config_lang]

    def execute(self, context):
        settings = context.scene.tresorio_settings
        mail, password = settings.mail, get_password(settings)
        context.scene.tresorio_settings.hidden_password = reset_password(len(password))
        context.scene.tresorio_settings.clear_password = reset_password(len(password))

        if settings.is_logged == True:
            self.report({'INFO'}, ln["already_logged_in"][config_lang])
            return {'CANCELLED'}
        if mail == "" and password == "":
            self.report({'ERROR'}, ln["no_mail_password"][config_lang])
            return {'CANCELLED'}
        if mail == "":
            self.report({'INFO'}, ln["no_mail"][config_lang])
            return {'CANCELLED'}
        if password == "":
            self.report({'INFO'}, ln["no_password"][config_lang])
            return {'CANCELLED'}

        body = {
            "email": mail,
            "password": password,
        }

        try:
            signin_url = url.urljoin(tc['backend'], tc['routes']['signin'])
            r = requests.post(signin_url, data=body)
            del body
            auth_res = r.json()
        except Exception as e:
            print(e)
            self.report({'ERROR'}, ln['internal_error_login'][config_lang])
            return {'CANCELLED'}

        if "token" not in auth_res:
            self.report({'WARNING'}, ln['invalid_login'][config_lang])
            return {'CANCELLED'}

        if settings.stay_connected == True:
            save_login_infos(mail, auth_res['token'], context)
        elif settings.stay_connected == False:
            remove_login_infos()

        context.scene.tresorio_settings.is_logged = True
        self.report({'INFO'}, ln['success_login'][config_lang])
        return {'FINISHED'}

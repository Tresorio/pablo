import bpy
import requests
import urllib.parse as url
from src.settings.password_tools import get_password
from src.config import (tresorio_config as tc, 
                        lang_notif as ln, 
                        lang_desc as ld,
                        config_lang)
from .save_email import save_email_infos, remove_email_infos


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
        email, password = settings.email, get_password(settings)
        context.scene.tresorio_settings.hidden_password = reset_password(len(password))
        context.scene.tresorio_settings.clear_password = reset_password(len(password))

        if settings.is_logged == True:
            self.report({'INFO'}, ln["already_logged_in"][config_lang])
            return {'CANCELLED'}
        if email == "" and password == "":
            self.report({'ERROR'}, ln["no_mail_password"][config_lang])
            return {'CANCELLED'}
        if email == "":
            self.report({'INFO'}, ln["no_mail"][config_lang])
            return {'CANCELLED'}
        if password == "":
            self.report({'INFO'}, ln["no_password"][config_lang])
            return {'CANCELLED'}

        body = {
            "email": email,
            "password": password,
        }

        try:
            signin_url = url.urljoin(tc['backend'], tc['routes']['signin'])
            r = requests.post(signin_url, data=body)
            auth_res = r.json()
            print("first:", r)
        except Exception as e:
            print(e)
            self.report({'ERROR'}, ln['internal_error_login'][config_lang])
            return {'CANCELLED'}
        finally:
            if "token" not in auth_res:
                self.report({'WARNING'}, ln['invalid_login'][config_lang])
                return {'CANCELLED'}
            else:
                context.scene.tresorio_settings.token = auth_res['token']


        if settings.remember_email == True:
            save_email_infos(email)
        elif settings.remember_email == False:
            remove_email_infos()

        context.scene.tresorio_settings.is_logged = True
        self.report({'INFO'}, ln['success_login'][config_lang])
        return {'FINISHED'}

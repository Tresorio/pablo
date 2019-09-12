import bpy
import requests
import urllib.parse as url
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.config.api import API_CONFIG
from src.utils.password import reset_password, get_password
from src.utils.email import set_email_in_conf, remove_email_from_conf


class TresorioLogin(bpy.types.Operator):
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

        body = {
            'email': email,
            'password': password,
        }

        try:
            signin_url = url.urljoin(API_CONFIG['backend'],
                                     API_CONFIG['routes']['signin'])
            r = requests.post(signin_url, data=body)
            auth_res = r.json()
        except requests.ConnectionError as exc:
            print(exc)
            self.report({'ERROR'},
                        TRADUCTOR['notif']['internal_error_login'][CONFIG_LANG])
            return {'CANCELLED'}
        else:
            if 'token' not in auth_res:
                self.report({'WARNING'},
                            TRADUCTOR['notif']['invalid_login'][CONFIG_LANG])
                return {'CANCELLED'}
            else:
                context.window_manager.tresorio_user_props.token = auth_res['token']

        if user_props.remember_email == True:
            set_email_in_conf(email)
        elif user_props.remember_email == False:
            remove_email_from_conf()

        context.window_manager.tresorio_user_props.is_logged = True

        self.report({'INFO'},
                    TRADUCTOR['notif']['success_login'][CONFIG_LANG])
        return {'FINISHED'}

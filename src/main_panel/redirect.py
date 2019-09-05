import bpy
import urllib.parse as urlparse
from src.config import (lang_desc as ld,
                        tresorio_config as tc,
                        config_lang)

class TresorioRedirectForgotPassword(bpy.types.Operator):
    bl_idname = 'tresorio.redirect_forgot_password'
    bl_label = "Forgot password"

    @classmethod
    def set_doc(cls):
        cls.__doc__ = ld['forgot_password'][config_lang]

    def execute(self, context):
        import webbrowser

        url = urlparse.urljoin(tc['frontend'], tc['routes']['register'])
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            print(e)
            return {'CANCELLED'}

        return {'FINISHED'}

class TresorioRedirectRegister(bpy.types.Operator):
    bl_idname = 'tresorio.redirect_register'
    bl_label = "Register"

    @classmethod
    def set_doc(cls):
        cls.__doc__ = ld['create_account'][config_lang]

    def execute(self, context):
        import webbrowser

        url = urlparse.urljoin(tc['frontend'], tc['routes']['forgot_password'])
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            print(e)
            return {'CANCELLED'}

        return {'FINISHED'}
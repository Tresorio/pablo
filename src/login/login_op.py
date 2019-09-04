import bpy
import requests
from src.settings.password_tools import get_password
from .save_login import save_login_infos, remove_login_infos

class TresorioLogin(bpy.types.Operator):
    """Login to Tresorio"""
    bl_idname = 'tresorio.login'
    bl_label = 'Login'

    def execute(self, context):
        settings = context.scene.tresorio_settings
        mail, password = settings.mail, get_password(settings)
        context.scene.tresorio_settings.hidden_password = ""
        context.scene.tresorio_settings.clear_password = ""

        if settings.is_logged == True:
            self.report({'INFO'}, "Already logged in, consider login out"); return {'CANCELLED'}
        if mail == "" and password == "":
            self.report({'ERROR'}, "Please enter your mail and password"); return {'CANCELLED'}
        if mail == "":
            self.report({'INFO'}, "No mail given"); return {'CANCELLED'}
        if password == "":
            self.report({'INFO'}, "No password given"); return {'CANCELLED'}

        if settings.stay_connected == True:
            save_login_infos(mail, password, context)
        elif settings.stay_connected == False:
            remove_login_infos()
        body = {
            "email": mail,
            "password": password,
        }
        try:
            r = requests.post("http://0.0.0.0:5000/auth/signin", data=body)
            print("token:", r.json()['token'])
        except Exception as e:
            print(e)
            self.report({'WARNING'}, "Error when login in")
            return {'CANCELLED'}
        context.scene.tresorio_settings.is_logged = True
        self.report({'INFO'}, "Successfully logged in"); return {'FINISHED'}

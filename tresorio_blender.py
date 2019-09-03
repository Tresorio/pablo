import os
import bpy
import json
import requests
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty

## TODO : temporary, to remove
MAIL = "dev@tresorio.com"
PASSWORD = "dev"
LOGIN_CONFIG_FILEPATH = os.path.join(bpy.utils.user_resource('CONFIG', path='Tresorio', create=True), "login.json")

## UTILS ##
def draw_popup(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

## RENDER ##

class TresorioRender(bpy.types.Operator):
    """Render with Tresorio !"""
    bl_idname = 'tresorio.render'
    bl_label = 'Render'
    

## CONNECTION BUTTONS ##
def save_login_infos(mail, password, context):
    conf = {
        "mail": mail,
        "password": password,
    }   
    conf_json = json.dumps(conf)
    with open(LOGIN_CONFIG_FILEPATH, "w") as f:
        f.write(conf_json)
    print("TODO : save user token at "+ LOGIN_CONFIG_FILEPATH)

def remove_login_infos():
    try:
        open(LOGIN_CONFIG_FILEPATH, 'w').close() # empty conf file
    except FileNotFoundError as e:
        print(e)

def get_password(settings):
    if settings.show_password:
        return settings.clear_password
    else:
        return settings.hidden_password

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
        if mail != MAIL or password != PASSWORD:
            self.report({'WARNING'}, "Invalid mail or password"); return {'CANCELLED'}

        ## TODO call gandalf for connection and check for return
        if settings.stay_connected == True:
            save_login_infos(mail, password, context)
        elif settings.stay_connected == False:
            remove_login_infos()
        body = {
            "email": "dev@tresorio.com",
            "password": "dev",
        }
        r = requests.post("http://0.0.0.0:5000/auth/signin", data=body)
        print("token:", r.json()['token'])
        context.scene.tresorio_settings.is_logged = True
        self.report({'INFO'}, "Successfully logged in"); return {'FINISHED'}

class TresorioLogout(bpy.types.Operator):
    """Logout of Tresorio"""
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    def execute(self, context):
        settings = context.scene.tresorio_settings
        if settings.is_logged == False:
            self.report({'INFO'}, "Can't log out if you're not logged in")
            return {'CANCELLED'}
        ## TODO call gandalf to logout properly and check return, send signal to gandalf on blender's end ?
        context.scene.tresorio_settings.is_logged = False
        self.report({'INFO'}, "Successfully logged out")
        return {'FINISHED'}

## MAIN SETTINGS ##
def login_from_conf():
    with open(LOGIN_CONFIG_FILEPATH, "r") as f:
        try:
            login_conf = json.load(f)
        except Exception as e:
            print(e)
            return False
        if "mail"not in login_conf or "password" not in login_conf:
            remove_login_infos()
            return False
        elif login_conf["mail"] != MAIL or login_conf["password"] != PASSWORD:
            remove_login_infos()
            return False
        return True
## /auth/signin password mail
def switch_password_visibility(settings, ctx):
    if settings.show_password:
        settings.clear_password = settings.hidden_password
    else:
        settings.hidden_password = settings.clear_password

class TresorioSettings(bpy.types.PropertyGroup):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def register(TresorioSettings):
        prelogged_in = login_from_conf()
        
        TresorioSettings.is_logged = BoolProperty(
            name = "",
            default = prelogged_in,
        )

        TresorioSettings.mail = StringProperty(
            name = "",
            description = "Tresorio account mail",
            maxlen = 128,
            default = ""
        )

        TresorioSettings.hidden_password = StringProperty(
            name = "",
            description = "Tresorio account password",
            maxlen = 128,
            default = "",
            subtype = "PASSWORD",
        )
        
        TresorioSettings.clear_password = StringProperty(
            name = "",
            description = "Tresorio account password",
            maxlen = 128,
            default = "",
            subtype = "NONE",
        )

        TresorioSettings.show_password = BoolProperty(
            name = "",
            description = "Reveal or hide the password",
            default = False,
            update = switch_password_visibility,
        )    

        TresorioSettings.stay_connected = BoolProperty(
            name = "",
            description = "Connect automatically at the next login",
            default = prelogged_in,
        )

        bpy.types.Scene.tresorio_settings = PointerProperty(type=TresorioSettings, name="tresorio_settings")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.tresorio_settings


## MAIN PANEL ##
class TresorioPanel(bpy.types.Panel):
    """Tresorio's blender plugin, un plugin qui chauffe plutot pas mal."""
    bl_label = "Tresorio Rendering"
    bl_idname = "OBJECT_PT_TRESORIO_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:

            col = layout.row().split(factor=0.36)
            col.label(text="")
            col.label(text="Connection")

            layout.label(text="Mail")
            layout.prop(settings, "mail", text="")
            layout.label(text="Password:")

            row = layout.row().split(factor=0.9)
            if settings.show_password:
                row.prop(settings, "clear_password", text="")
            else:
                row.prop(settings, "hidden_password", text="")
            row.prop(settings, "show_password", icon_only=True, icon="HIDE_OFF")

            layout.separator(factor=0.1)

            row = layout.row().split(factor=0.3)
            row.column().prop(settings, "stay_connected", text="Stay connected")
            col = row.column()
            if settings.mail=="" or settings.hidden_password=="" and settings.clear_password=="":
                col.enabled=False
            col.operator("tresorio.login", icon='UNLOCKED', text='Login')

            layout.separator(factor=4.0)

            layout.operator("wm.url_open", text="Forgot your password ?", icon="QUESTION").url = "http://192.168.15.20:3000/password"
            layout.operator("wm.url_open", text="Create your account now", icon="PLUS").url = "http://192.168.15.20:3000/register"

            ## TODO Login panel, interface ...
        elif settings.is_logged == True:

            row = layout.row()
            row.label(text=settings.mail)
            row.operator("tresorio.logout", icon='LOCKED', text='Logout')
            row.operator("tresorio.render", icon='RENDER_ANIMATION')

## BLENDER INTERNALS ##
def register():
    bpy.utils.register_class(TresorioSettings)
    bpy.utils.register_class(TresorioPanel)
    bpy.utils.register_class(TresorioLogin)
    bpy.utils.register_class(TresorioLogout)
    bpy.utils.register_class(TresorioRender)

def unregister():
    bpy.utils.unregister_class(TresorioSettings)
    bpy.utils.unregister_class(TresorioPanel)
    bpy.utils.unregister_class(TresorioLogin)
    bpy.utils.unregister_class(TresorioLogout)
    bpy.utils.unregister_class(TresorioRender)

## TODO BIG SECURITY FLAW ON PASSWORD : it is accessible to any other addone while its being entered in the textbox
if __name__ == "__main__":
    register()

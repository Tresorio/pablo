import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


def logout():
    user_props = bpy.context.window_manager.tresorio_user_props
    remember_email = user_props.remember_email

    bpy.context.window_manager.property_unset('tresorio_user_props')
    bpy.context.window_manager.property_unset('tresorio_report_props')
    bpy.context.window_manager.property_unset('tresorio_render_form')
    bpy.context.window_manager.property_unset('tresorio_render_packs')
    bpy.context.window_manager.property_unset('tresorio_renders_details')

    if remember_email is True:
        bpy.context.window_manager.tresorio_user_props.email = user_props.email
        bpy.context.window_manager.tresorio_user_props.remember_email = True
    else:
        bpy.context.window_manager.tresorio_user_props.email = ''
        bpy.context.window_manager.tresorio_user_props.remember_email = False


class TresorioLogoutOperator(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_logout'][CONFIG_LANG]

    def execute(self, context):
        logout()
        self.report({'INFO'},
                    TRADUCTOR['notif']['success_logout'][CONFIG_LANG])
        return {'FINISHED'}

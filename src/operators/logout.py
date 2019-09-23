import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioLogoutOperator(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_logout'][CONFIG_LANG]

    def execute(self, context):
        user_props = context.window_manager.tresorio_user_props

        if user_props.is_logged == False:
            self.report({'INFO'},
                        TRADUCTOR['notif']['not_logged_in'][CONFIG_LANG])
            return {'CANCELLED'}
        remember_email = user_props.remember_email

        context.window_manager.property_unset('tresorio_user_props')
        context.window_manager.property_unset('tresorio_report_props')
        context.window_manager.property_unset('tresorio_render_form')
        context.window_manager.property_unset('tresorio_render_packs')

        if remember_email is True:
            context.window_manager.tresorio_user_props.email = user_props.email
            context.window_manager.tresorio_user_props.remember_email = True
        else:
            context.window_manager.tresorio_user_props.email = ''
            context.window_manager.tresorio_user_props.remember_email = False

        self.report({'INFO'},
                    TRADUCTOR['notif']['success_logout'][CONFIG_LANG])
        return {'FINISHED'}

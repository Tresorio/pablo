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

        context.window_manager.property_unset('tresorio_user_props')
        context.window_manager.property_unset('tresorio_report_props')
        context.window_manager.property_unset('tresorio_render_form')

        self.report({'INFO'},
                    TRADUCTOR['notif']['success_logout'][CONFIG_LANG])
        return {'FINISHED'}

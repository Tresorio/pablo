import bpy
from src.ui.popup import popup
from src.services.async_loop import shutdown_loop
from src.config.langs import TRADUCTOR, CONFIG_LANG


def logout():
    shutdown_loop()
    bpy.context.scene.property_unset('tresorio_report_props')
    bpy.context.window_manager.property_unset('tresorio_render_packs')
    bpy.context.window_manager.property_unset('tresorio_renders_details')
    bpy.context.window_manager.property_unset('tresorio_user_props')


class TresorioLogoutOperator(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_logout'][CONFIG_LANG]

    def execute(self, context):
        logout()
        self.report({'INFO'}, TRADUCTOR['notif']
                    ['success_logout'][CONFIG_LANG])
        return {'FINISHED'}

import bpy
from src.config import lang_notif as ln, lang_desc as ld


class TresorioLogout(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls, lang):
        cls.__doc__ = ld['tresorio_logout'][lang]

    def execute(self, context):
        settings = context.scene.tresorio_settings
        lang = settings.curr_lang

        if settings.is_logged == False:
            self.report({'INFO'}, ln['not_logged_in'][lang])
            return {'CANCELLED'}

        context.scene.tresorio_settings.is_logged = False
        self.report({'INFO'}, ln['success_logout'][lang])
        return {'FINISHED'}

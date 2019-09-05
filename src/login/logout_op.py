import bpy
from src.config import (lang_notif as ln,
                        lang_desc as ld,
                        config_lang)


class TresorioLogout(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = ld['tresorio_logout'][config_lang]

    def execute(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.report({'INFO'}, ln['not_logged_in'][config_lang])
            return {'CANCELLED'}

        context.scene.tresorio_settings.is_logged = False
        self.report({'INFO'}, ln['success_logout'][config_lang])
        return {'FINISHED'}

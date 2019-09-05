import bpy
from src.config import (lang_notif as ln,
                        lang_desc as ld,
                        config_lang)

class TresorioRenderFrame(bpy.types.Operator):
    bl_idname = 'tresorio.render_frame'
    bl_label = 'Render frame'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = ld['tresorio_render_frame'][config_lang]

    def execute(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.report({'INFO'}, ln['not_logged_in'][config_lang])
            return {'CANCELLED'}

        if bpy.data.is_saved == False:
            self.report({'WARNING'}, ln['file_not_saved'][config_lang])
            return {'CANCELLED'}

        print("IT SHOULD UPLOAD HERE")

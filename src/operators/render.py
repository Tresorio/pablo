import os
import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRenderFrame(bpy.types.Operator):
    bl_idname = 'tresorio.render_frame'
    bl_label = 'Render frame'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_render_frame'][CONFIG_LANG]

    def execute(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.report({'INFO'},
                        TRADUCTOR['notif']['not_logged_in'][CONFIG_LANG])
            return {'CANCELLED'}

        if bpy.data.is_saved == False or bpy.data.is_dirty == True:
            self.report({'WARNING'},
                        TRADUCTOR['notif']['file_not_saved'][CONFIG_LANG])
            return {'CANCELLED'}

        return {'FINISHED'}

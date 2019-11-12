import bpy
from src.config.enums import RenderStatus
from src.services.backend import delete_all_renders
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioDeleteAllRendersOperator(bpy.types.Operator):
    bl_idname = 'tresorio.delete_all_renders'
    bl_label = ''

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['delete_all_renders'][CONFIG_LANG]

    def execute(self, context):
        delete_all_renders()
        return {'FINISHED'}

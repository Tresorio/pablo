import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import delete_targeted_render_results


class TresorioDeleteTargetedRendersOperator(bpy.types.Operator):
    bl_idname = 'tresorio.delete_targeted_renders'
    bl_label = TRADUCTOR['field']['delete_targeted_results'][CONFIG_LANG]

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['delete_targeted_renders'][CONFIG_LANG]

    @classmethod
    def poll(cls, context: bpy.types.Context):
        for render in context.window_manager.tresorio_renders_details:
            if render.is_target:
                return True
        return False

    def execute(self, context):
        delete_targeted_render_results()
        return {'FINISHED'}

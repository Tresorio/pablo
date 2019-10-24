import bpy
from src.config.enums import RenderStatus
from src.services.backend import delete_render
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioDeleteRenderOperator(bpy.types.Operator):
    bl_idname = 'tresorio.delete_render'
    bl_label = ''

    index: bpy.props.IntProperty()

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['delete_render'][CONFIG_LANG]

    def execute(self, context):
        render = context.window_manager.tresorio_renders_details[self.index]
        render.status = RenderStatus.STOPPING
        delete_render(render, self.index)
        return {'FINISHED'}

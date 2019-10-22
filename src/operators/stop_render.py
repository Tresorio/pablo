import bpy
from src.services.backend import stop_render
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioStopRenderOperator(bpy.types.Operator):
    bl_idname = 'tresorio.stop_render'
    bl_label = ''

    index: bpy.props.IntProperty()

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['stop_render'][CONFIG_LANG]

    def execute(self, context):
        render = context.window_manager.tresorio_renders_details[self.index]
        stop_render(render)
        return {'FINISHED'}

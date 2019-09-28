import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import download_render_results


class TresorioDownloadRenderResultsOperator(bpy.types.Operator):
    bl_idname = 'tresorio.download_render_results'
    bl_label = ''

    index: bpy.props.IntProperty()
    render_result_path: bpy.props.StringProperty(subtype='DIR_PATH')

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['download_render_results'][CONFIG_LANG]

    def execute(self, context):
        render_id = context.window_manager.tresorio_renders_details[self.index].id
        download_render_results(render_id, '/tmp/')#self.render_result_path)
        return {'FINISHED'}

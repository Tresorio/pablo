import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import download_render_results


class TresorioDownloadRenderResultsOperator(bpy.types.Operator):
    bl_idname = 'tresorio.download_render_results'
    bl_label = TRADUCTOR['field']['download_results'][CONFIG_LANG]

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob: bpy.props.StringProperty(
        default='',
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    directory: bpy.props.StringProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['download_render_results'][CONFIG_LANG]

    def execute(self, context):
        render = context.window_manager.tresorio_renders_details[self.index]
        download_render_results(render, self.directory)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

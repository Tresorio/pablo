import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import download_targeted_render_results


class TresorioDownloadTargetedRenderResultsOperator(bpy.types.Operator):
    bl_idname = 'tresorio.download_targeted_render_results'
    bl_label = TRADUCTOR['field']['download_targeted_results'][CONFIG_LANG]

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
        cls.__doc__ = TRADUCTOR['desc']['download_targets_render_results'][CONFIG_LANG]

    @classmethod
    def poll(cls, context: bpy.types.Context):
        for render in context.window_manager.tresorio_renders_details:
            if render.is_target:
                return True
        return False

    def execute(self, context):
        download_targeted_render_results(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

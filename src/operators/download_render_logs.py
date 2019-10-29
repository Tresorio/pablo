import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import download_render_logs

class TresorioDownloadRenderLogsOperator(bpy.types.Operator):
    bl_idname = 'tresorio.download_render_logs'
    bl_label = TRADUCTOR['field']['download_logs'][CONFIG_LANG]    

    index: bpy.props.IntProperty()
    directory: bpy.props.StringProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    filepath: bpy.props.StringProperty(
        name='',
        description='',
        subtype='FILE_PATH',
        options={'HIDDEN', 'SKIP_SAVE'}
    )


    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['download_render_logs'][CONFIG_LANG]

    def execute(self, context):
        render_id = context.window_manager.tresorio_renders_details[self.index].id
        download_render_logs(render_id, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
import bpy
from src.services.backend import update_list_renderings
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRefreshRendersOperator(bpy.types.Operator):
    bl_idname = 'tresorio.refresh_renders'
    bl_label = ''

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['refresh_renders'][CONFIG_LANG]

    def execute(self, context):
        if context.window_manager.tresorio_report_props.are_renders_refreshing is False:
            update_list_renderings()
        return {'FINISHED'}

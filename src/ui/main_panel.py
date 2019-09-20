import bpy
from .draw_connection_panel import draw_connection_panel


class TresorioMainPanel(bpy.types.Panel):
    bl_label = 'Tresorio'
    bl_idname = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context: bpy.types.Context):
        user_props = context.window_manager.tresorio_user_props
        report_props = context.window_manager.tresorio_report_props
        layout = self.layout

        if report_props.connection_error is True:
            layout.label(text=report_props.connection_error_msg, icon='ERROR')

        if user_props.is_logged == False:
            draw_connection_panel(layout, context)

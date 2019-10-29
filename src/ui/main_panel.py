import bpy
from src.ui.icons import TresorioIconsLoader as til
from src.ui.draw_connection_panel import draw_connection_panel


class TresorioMainPanel(bpy.types.Panel):
    bl_label = 'Tresorio'
    bl_idname = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw_header(self, context):
        self.layout.label(icon_value=til.icon('TRESORIO_TRESORIO'))

    def draw(self, context: bpy.types.Context):
        user_props = context.window_manager.tresorio_user_props
        layout = self.layout

        if user_props.is_logged == False:
            draw_connection_panel(layout, context)

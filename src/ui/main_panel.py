"""Main panel"""

from src.ui.draw_connection_panel import draw_connection_panel
from src.ui.icons import TresorioIconsLoader as til
import bpy


class TresorioMainPanel(bpy.types.Panel):
    """Main panel"""
    bl_label = 'Tresorio'
    bl_idname = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw_header(self,
                    context: bpy.types.Context
                    ) -> None:
        """Draw the header of the panel"""
        del context
        self.layout.label(icon_value=til.icon('TRESORIO_TRESORIO'))

    def draw(self,
             context: bpy.types.Context
             ) -> None:
        """Draw the body of the panel"""
        user_props = context.window_manager.tresorio_user_props
        layout = self.layout

        if not user_props.is_logged:
            draw_connection_panel(layout, context)

"""Main panel"""

from src.ui.draw_connection_panel import draw_connection_panel
from src.ui.draw_version_panel import draw_version_panel
from src.ui.draw_advanced_settings_pannel import draw_advanced_settings_panel
from src.ui.icons import TresorioIconsLoader as til
from src.config.api import API_CONFIG
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

        latest_version = user_props.latest_version

        actual_version = f"{API_CONFIG['version']['major']}.{API_CONFIG['version']['minor']}.{API_CONFIG['version']['patch']}"

        # Get version from gandalf
        # If pas à jour, panel mettre à jour

        major, minor, patch = map(int, latest_version.split('.'))

        if major > API_CONFIG['version']['major'] or (major == API_CONFIG['version']['major'] and minor > API_CONFIG['version']['minor']):
            draw_version_panel(layout, context, actual_version, latest_version)
        elif not user_props.is_logged and not user_props.advanced_settings:
            draw_connection_panel(layout, context)
        elif user_props.advanced_settings:
            draw_advanced_settings_panel(layout, context)

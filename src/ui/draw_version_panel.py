"""Defines the drawer for the connection panel"""

from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


def draw_version_panel(layout: bpy.types.UILayout,
                          context: bpy.types.Context,
                          actual_version: str,
                          latest_version: str,
                          ) -> None:
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props
    report_props = bpy.context.window_manager.tresorio_report_props

    title = layout.row()
    title.label(text=f"{TRADUCTOR['desc']['new_version'][CONFIG_LANG]}")
    title = layout.row()
    title.label(text=f"{TRADUCTOR['desc']['actual_version'][CONFIG_LANG]} : {actual_version}")
    title = layout.row()
    title.label(text=f"{TRADUCTOR['desc']['latest_version'][CONFIG_LANG]} : {latest_version}")
    layout.operator('tresorio.download_addon',
        text=f"{TRADUCTOR['desc']['download_latest'][CONFIG_LANG]}",
        icon_value=til.icon('TRESORIO_LEAF')
    )



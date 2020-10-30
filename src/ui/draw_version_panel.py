"""Defines the drawer for the connection panel"""

import bpy
from bundle_modules import i18n
from src.ui.icons import TresorioIconsLoader as til


def draw_version_panel(layout: bpy.types.UILayout,
                          context: bpy.types.Context,
                          actual_version: str,
                          latest_version: str,
                          ) -> None:
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props
    report_props = bpy.context.window_manager.tresorio_report_props

    title = layout.row()
    title.label(text=i18n.t('blender.new-version'))
    title = layout.row()
    title.label(text=f"{i18n.t('blender.actual-version')} : {actual_version}")
    title = layout.row()
    title.label(text=f"{i18n.t('blender.latest-version')} : {latest_version}")
    layout.operator('tresorio.download_addon',
        text=i18n.t('blender.download-latest'),
        icon_value=til.icon('TRESORIO_LEAF')
    )



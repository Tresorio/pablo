"""This module defines the render frame operator"""

from typing import Set

from bundle_modules import i18n
from src.ui.popup import popup
from src.services.backend import new_render
import bpy

class TresorioLaunchRenderingOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.launch')
    bl_idname = 'tresorio.launchrendering'
    bl_label = i18n.t('blender.launch')

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        context.window_manager.tresorio_user_props.is_launching_rendering = True
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(i18n.t('blender.not-logged-in'), icon='ERROR')
            return {'CANCELLED'}

        farms = bpy.context.window_manager.tresorio_farm_props
        index = bpy.context.window_manager.tresorio_farm_props_index
        if index < 0 or index >= len(farms):
            popup(i18n.t('blender.choose-farm'), icon='ERROR')
            return {'FINISHED'}

        new_render()
        bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False

        return {'FINISHED'}

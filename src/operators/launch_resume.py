"""This module defines the render frame operator"""

from typing import Set

from bundle_modules import i18n
from src.services.backend import resume_render
from src.ui.popup import popup
import bpy

class TresorioLaunchResumeOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.launch')
    bl_idname = 'tresorio.launchresume'
    bl_label = i18n.t('blender.launch')

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(i18n.t('blender.not-logged-in'), icon='ERROR')
            return {'CANCELLED'}

        farms = bpy.context.window_manager.tresorio_farm_props
        farm_index = bpy.context.window_manager.tresorio_farm_props_index

        if farm_index < 0 or farm_index >= len(farms):
            popup(i18n.t('blender.choose-farm'), icon='ERROR')
            return {'FINISHED'}

        bpy.context.window_manager.tresorio_user_props.is_resuming_rendering = False

        render_index = context.window_manager.tresorio_renders_list_index
        render = context.window_manager.tresorio_renders_details[render_index]
        resume_render(render, farm_index)

        return {'FINISHED'}

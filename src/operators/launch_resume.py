"""This module defines the render frame operator"""

from typing import Set

from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import resume_render
from src.services.loggers import BACKEND_LOGGER
from src.ui.popup import popup, alert
from src.services.backend import new_render
import bpy

class TresorioLaunchResumeOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['launch'][CONFIG_LANG]
    bl_idname = 'tresorio.launchresume'
    bl_label = TRADUCTOR['desc']['launch'][CONFIG_LANG]

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        farms = bpy.context.window_manager.tresorio_farm_props
        farm_index = bpy.context.window_manager.tresorio_farm_props_index
        if farm_index < 0 or farm_index >= len(farms):
            popup(TRADUCTOR['notif']['choose_farm'][CONFIG_LANG], icon='ERROR')
            return {'FINISHED'}
        selected_farm = farms[farm_index]

        bpy.context.window_manager.tresorio_user_props.is_resuming_rendering = False

        render_index = context.window_manager.tresorio_renders_list_index
        render = context.window_manager.tresorio_renders_details[render_index]
        resume_render(render, farm_index)

        return {'FINISHED'}

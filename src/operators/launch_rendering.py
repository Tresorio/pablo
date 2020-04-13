"""This module defines the render frame operator"""

from typing import Set

from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import get_farms
from src.services.loggers import BACKEND_LOGGER
from src.ui.popup import popup, alert
from src.services.backend import new_render
import bpy

class TresorioLaunchRenderingOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['launch'][CONFIG_LANG]
    bl_idname = 'tresorio.launchrendering'
    bl_label = TRADUCTOR['desc']['launch'][CONFIG_LANG]

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        context.window_manager.tresorio_user_props.is_launching_rendering = True
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        farms = bpy.context.window_manager.tresorio_farm_props
        index = bpy.context.window_manager.tresorio_farm_props_index
        if index < 0 or index >= len(farms):
            popup(TRADUCTOR['notif']['choose_farm'][CONFIG_LANG], icon='ERROR')
            return {'FINISHED'}
        selected_farm = farms[index]

        new_render()
        bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False

        return {'FINISHED'}

"""This module defines the render frame operator"""

from typing import Set

from src.ui.popup import popup, alert, notif
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import get_farms
from src.properties.render_form import get_render_type
from src.config.enums import RenderStatus, RenderTypes
import bpy

class TresorioCpuRenderFrameOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['tresorio_cpurender'][CONFIG_LANG]
    bl_idname = 'tresorio.cpurender'
    bl_label = TRADUCTOR['field']['cpulaunch'][CONFIG_LANG]

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Wether to enable or disable the operator"""
        del cls
        return (context.window_manager.tresorio_user_props.is_logged and
                context.scene.tresorio_render_form.rendering_name)

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        name = bpy.context.scene.tresorio_render_form.rendering_name

        is_name_already_taken = False
        for render in bpy.context.window_manager.tresorio_renders_details:
            if render.name == name:
                is_name_already_taken = True

        if len(name) == 0 or "/" in name or name.isspace():
            popup(msg=TRADUCTOR['notif']['wrong_name'][CONFIG_LANG], icon='ERROR')
            return {'FINISHED'}
        elif is_name_already_taken == True:
            popup(msg= TRADUCTOR['notif']['render_name_already_taken'][CONFIG_LANG].format(name.capitalize()), icon='ERROR')
            return {'FINISHED'}

        bpy.context.window_manager.tresorio_farm_props_index = -1
        context.window_manager.tresorio_user_props.is_launching_rendering = True
        user_props = context.window_manager.tresorio_user_props

        number_of_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
        if get_render_type() == RenderTypes.FRAME:
            number_of_frames = 1
        bpy.context.scene.tresorio_render_form.number_of_frames = number_of_frames

        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        context.window_manager.tresorio_farm_props.clear()
        context.window_manager.tresorio_user_props.rendering_mode = 'CPU'
        get_farms('CPU')

        return {'FINISHED'}

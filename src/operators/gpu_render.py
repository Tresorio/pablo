"""This module defines the render frame operator"""

from typing import Set

from bundle_modules import i18n
from src.ui.popup import popup
from src.services.backend import get_farms
from src.properties.render_form import get_render_type
from src.config.enums import RenderTypes
import bpy

class TresorioGpuRenderFrameOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.tresorio-gpurender')
    bl_idname = 'tresorio.gpurender'
    bl_label = i18n.t('blender.gpulaunch')

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
            popup(msg=i18n.t('blender.wrong-name'), icon='ERROR')
            return {'FINISHED'}
        elif is_name_already_taken == True:
            popup(msg=i18n.t('blender.render-name-already-taken').format(name.capitalize()), icon='ERROR')
            return {'FINISHED'}

        bpy.context.window_manager.tresorio_farm_props_index = -1
        context.window_manager.tresorio_user_props.is_launching_rendering = True
        user_props = context.window_manager.tresorio_user_props

        number_of_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
        if get_render_type() == RenderTypes.FRAME:
            number_of_frames = 1
        bpy.context.scene.tresorio_render_form.number_of_frames = number_of_frames

        if not user_props.is_logged:
            popup(i18n.t('blender.not-logged-in'), icon='ERROR')
            return {'CANCELLED'}

        context.window_manager.tresorio_farm_props.clear()
        context.window_manager.tresorio_user_props.rendering_mode = 'GPU'
        get_farms('GPU', number_of_frames)

        return {'FINISHED'}

"""This module defines the Delete render operator"""

from typing import Set

from src.config.enums import RenderStatus
from src.services.backend import get_farms
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=too-few-public-methods

class TresorioResumeRenderOperator(bpy.types.Operator):
    """Delete render operator"""
    __doc__ = TRADUCTOR['desc']['resume_render'][CONFIG_LANG]
    bl_idname = 'tresorio.resume_render'
    bl_label = ''

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""

        context.window_manager.tresorio_renders_list_index = self.index
        render = context.window_manager.tresorio_renders_details[self.index]
        mode = render.mode
        number_of_frames = render.total_frames - render.rendered_frames

        user_props = context.window_manager.tresorio_user_props
        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        # Reset context
        bpy.context.window_manager.tresorio_farm_props_index = -1
        context.window_manager.tresorio_user_props.is_resuming_rendering = True
        context.window_manager.tresorio_farm_props.clear()

        get_farms(mode, number_of_frames)

        return {'FINISHED'}

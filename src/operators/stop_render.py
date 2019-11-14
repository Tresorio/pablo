"""This module defines the stop render operator"""


from typing import Set

from src.config.enums import RenderStatus
from src.services.backend import stop_render
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


# pylint: disable=too-few-public-methods

class TresorioStopRenderOperator(bpy.types.Operator):
    """Stop render operator"""
    __doc__ = TRADUCTOR['desc']['stop_render'][CONFIG_LANG]
    bl_idname = 'tresorio.stop_render'
    bl_label = ''

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when this operator is called"""
        render = context.window_manager.tresorio_renders_details[self.index]
        render.status = RenderStatus.STOPPING
        stop_render(render)
        return {'FINISHED'}

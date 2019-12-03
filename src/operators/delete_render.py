"""This module defines the Delete render operator"""

from typing import Set

from src.config.enums import RenderStatus
from src.services.backend import delete_render
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


# pylint: disable=too-few-public-methods

class TresorioDeleteRenderOperator(bpy.types.Operator):
    """Delete render operator"""
    __doc__ = TRADUCTOR['desc']['delete_render'][CONFIG_LANG]
    bl_idname = 'tresorio.delete_render'
    bl_label = ''

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        render = context.window_manager.tresorio_renders_details[self.index]
        render.status = RenderStatus.STOPPING
        delete_render(render.id)
        return {'FINISHED'}

"""This module defines the render frame operator"""

from typing import Set

from src.ui.popup import popup
from src.services.backend import new_render
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=no-self-use


class TresorioCancelRenderingOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['cancel'][CONFIG_LANG]
    bl_idname = 'tresorio.cancelrendering'
    bl_label = TRADUCTOR['desc']['cancel'][CONFIG_LANG]

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        context.window_manager.tresorio_user_props.is_launching_rendering = False
        context.window_manager.tresorio_user_props.is_resuming_rendering = False
        return {'FINISHED'}

"""This module defines the render frame operator"""

from typing import Set

from bundle_modules import i18n
import bpy

# pylint: disable=no-self-use


class TresorioCancelRenderingOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.cancel')
    bl_idname = 'tresorio.cancelrendering'
    bl_label = i18n.t('blender.cancel')

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        context.window_manager.tresorio_user_props.is_launching_rendering = False
        context.window_manager.tresorio_user_props.is_resuming_rendering = False
        return {'FINISHED'}

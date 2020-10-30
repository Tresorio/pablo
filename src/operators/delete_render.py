"""This module defines the Delete render operator"""

from typing import Set

from bundle_modules import i18n
from src.services.backend import delete_render

import bpy


# pylint: disable=too-few-public-methods

class TresorioDeleteRenderOperator(bpy.types.Operator):
    """Delete render operator"""
    __doc__ = i18n.t('blender.delete-render')
    bl_idname = 'tresorio.delete_render'
    bl_label = ''

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        render = context.window_manager.tresorio_renders_details[self.index]
        delete_render(render.id)
        return {'FINISHED'}

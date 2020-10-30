"""This module defines the delete all the renders of the user"""

from typing import Set

from bundle_modules import i18n
from src.services.backend import delete_all_renders

import bpy

# pylint: disable=too-few-public-methods,no-self-use


class TresorioDeleteAllRendersOperator(bpy.types.Operator):
    """Delete all the user's renders"""
    __doc__ = i18n.t('blender.delete-all-renders')
    bl_idname = 'tresorio.delete_all_renders'
    bl_label = ''

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        del context
        delete_all_renders()
        return {'FINISHED'}

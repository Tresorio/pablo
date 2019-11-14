"""This module defines the delete all the renders of the user"""

from typing import Set

from src.services.backend import delete_all_renders
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=too-few-public-methods,no-self-use


class TresorioDeleteAllRendersOperator(bpy.types.Operator):
    """Delete all the user's renders"""
    __doc__ = TRADUCTOR['desc']['delete_all_renders'][CONFIG_LANG]
    bl_idname = 'tresorio.delete_all_renders'
    bl_label = ''

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        del context
        delete_all_renders()
        return {'FINISHED'}

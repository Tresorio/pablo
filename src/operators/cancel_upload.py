"""This module defines the render frame operator"""

from typing import Set

from src.ui.popup import popup
from src.services.backend import new_render
from src.config.langs import TRADUCTOR, CONFIG_LANG
import src.operators.upload_modal
import bpy


class TresorioCancelUploadOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['cancel'][CONFIG_LANG]
    bl_idname = 'tresorio.cancelupload'
    bl_label = ''

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        src.operators.upload_modal.stop_upload_modal()
        return {'FINISHED'}

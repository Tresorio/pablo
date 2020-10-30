"""This module defines the render frame operator"""

from typing import Set

from bundle_modules import i18n
import src.operators.upload_modal
import bpy


class TresorioCancelUploadOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.cancel')
    bl_idname = 'tresorio.cancelupload'
    bl_label = ''

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        src.operators.upload_modal.stop_upload_modal()
        return {'FINISHED'}

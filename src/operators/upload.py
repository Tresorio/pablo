"""This module defines the upload frame operator"""

from typing import Set

from src.ui.popup import popup
from src.services.backend import new_upload
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=no-self-use


class TresorioUploadOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['tresorio_upload'][CONFIG_LANG]
    bl_idname = 'tresorio.upload'
    bl_label = TRADUCTOR['field']['upload'][CONFIG_LANG]

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Wether to enable or disable the operator"""
        del cls
        return (context.window_manager.tresorio_user_props.is_logged and
                context.scene.tresorio_render_form.rendering_name)

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        if not bpy.data.is_saved or bpy.data.is_dirty:
            popup(TRADUCTOR['notif']['file_not_saved']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        new_upload()

        return {'FINISHED'}

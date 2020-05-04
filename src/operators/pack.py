"""This module defines the upload frame operator"""

from typing import Set

from src.ui.popup import popup
from src.services.backend import pack_project
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy
import os

# pylint: disable=no-self-use


class TresorioPackOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['tresorio_pack'][CONFIG_LANG]
    bl_idname = 'tresorio.pack'
    bl_label = TRADUCTOR['field']['pack'][CONFIG_LANG]

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

        if not bpy.data.is_saved or bpy.data.is_dirty:
            popup(TRADUCTOR['notif']['file_not_saved']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        path = context.scene.tresorio_render_form.project_folder
        project = context.scene.tresorio_render_form.project_name

        pack_project(path, project)

        return {'FINISHED'}

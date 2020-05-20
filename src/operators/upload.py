"""This module defines the upload frame operator"""

from typing import Set

from src.ui.popup import popup, alert
from src.services.backend import new_upload
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy
import os

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


        folder = context.scene.tresorio_render_form.project_folder
        project_name = context.scene.tresorio_render_form.project_name
        project = project_name.replace(" ", "_") + TRADUCTOR['field']['tresorio_suffix'][CONFIG_LANG]
        path = os.path.join(folder, project)

        if not os.path.exists(path):
            alert(TRADUCTOR['notif']['pack_first'][CONFIG_LANG].format(project))
            return {'CANCELLED'}
        if not os.path.isdir(path):
            alert(TRADUCTOR['notif']['pack_error'][CONFIG_LANG].format(project))
            return {'CANCELLED'}

        new_upload(path, project_name)

        return {'FINISHED'}

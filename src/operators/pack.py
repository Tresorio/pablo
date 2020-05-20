"""This module defines the upload frame operator"""

from typing import Set

from src.ui.popup import popup, alert
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

        folder = context.scene.tresorio_render_form.project_folder
        project = context.scene.tresorio_render_form.project_name.replace(" ", "_") + TRADUCTOR['field']['tresorio_suffix'][CONFIG_LANG]
        path = os.path.join(folder, project)

        if not os.path.exists(folder):
            alert(TRADUCTOR['notif']['doesnt_exist'][CONFIG_LANG].format(folder))
            return {'CANCELLED'}
        if not os.path.isdir(folder):
            alert(TRADUCTOR['notif']['not_dir'][CONFIG_LANG].format(folder))
            return {'CANCELLED'}


        pack_project(path)

        return {'FINISHED'}

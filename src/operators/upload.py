"""This module defines the upload frame operator"""

from typing import Set

from src.ui.popup import popup, alert
from src.services.backend import new_upload
from bundle_modules import i18n
import bpy
import os

# pylint: disable=no-self-use


class TresorioUploadOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = i18n.t('blender.tresorio-upload')
    bl_idname = 'tresorio.upload'
    bl_label = i18n.t('blender.upload')

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
            popup(i18n.t('blender.not-logged-in'), icon='ERROR')
            return {'CANCELLED'}

        if not bpy.data.is_saved or bpy.data.is_dirty:
            popup(i18n.t('blender.file-not-saved'), icon='ERROR')
            return {'CANCELLED'}


        blend_path = bpy.data.filepath
        folder = context.scene.tresorio_render_form.project_folder
        project_name = bpy.path.clean_name(context.scene.tresorio_render_form.project_name)
        project = project_name + i18n.t('blender.tresorio-suffix')
        target_path = os.path.join(folder, project)

        if not os.path.exists(folder):
            alert(i18n.t('blender.doesnt-exist').format(folder))
            return {'CANCELLED'}
        if not os.path.isdir(folder):
            alert(i18n.t('blender.not-dir').format(folder))
            return {'CANCELLED'}
        if os.path.exists(target_path) and not os.path.isdir(target_path):
            alert(i18n.t('blender.pack-error').format(project))
            return {'CANCELLED'}

        new_upload(blend_path, target_path, project_name)

        return {'FINISHED'}
